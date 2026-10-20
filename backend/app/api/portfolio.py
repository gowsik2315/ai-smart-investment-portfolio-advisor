"""
Portfolio Tracking API Routes

Portfolios hold a ledger of transactions. Holdings, valuations and
profit are DERIVED from that ledger on every read (see
`services/portfolio_tracker.py`), so there is no stored position that
can fall out of step with the transactions behind it.

Live prices are best-effort. A holding that cannot be priced falls back
to the price of its last transaction and says so, rather than quietly
reporting a value that nothing has repriced.
"""

import logging
import time
from typing import Dict, List, Optional

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.dependencies import get_current_user
from app.ml.data import load_history
from app.models.portfolio import Portfolio
from app.models.transaction import Transaction
from app.schemas.portfolio import (
    HoldingResponse,
    PortfolioCreate,
    PortfolioDetailResponse,
    PortfolioOverviewResponse,
    PortfolioResponse,
    PortfolioSummary,
    PortfolioUpdate,
    TransactionCreate,
    TransactionResponse,
)
from app.services.portfolio_tracker import (
    InsufficientHoldingError,
    PortfolioTracker,
)
from app.services.yahoo_finance_service import YahooFinanceService

logger = logging.getLogger(__name__)

router = APIRouter()

# Quotes are cached briefly so that opening the dashboard and then a
# portfolio does not fetch the same symbol twice. Short enough that a
# refresh still shows a moving price.
#
# The cached entry holds the price AND the sector, because both arrive in
# the same Yahoo response. Classifying a holding's sector therefore costs
# no extra network call.
_QUOTE_CACHE: Dict[str, tuple] = {}
_QUOTE_CACHE_TTL_SECONDS = 60


def _fetch_quotes(symbols: List[str]) -> Dict[str, Dict]:
    """
    Best-effort current price and sector for each symbol.

    A symbol that cannot be fetched is simply absent from the result;
    the tracker then falls back to its last transaction price and
    labels the holding accordingly. One unavailable ticker must never
    fail the whole portfolio view.

    Returns:
        symbol -> {"price": float, "sector": str or None}
    """
    quotes: Dict[str, Dict] = {}
    now = time.monotonic()

    for symbol in {s.strip().upper() for s in symbols if s and s.strip()}:
        cached = _QUOTE_CACHE.get(symbol)
        if cached and (now - cached[0]) < _QUOTE_CACHE_TTL_SECONDS:
            quotes[symbol] = cached[1]
            continue

        try:
            info = YahooFinanceService.get_stock_info(symbol)
            price = float(info.get("current_price") or 0.0)
            sector = info.get("sector")
            # yfinance uses the string "N/A" rather than omitting the key.
            if sector in (None, "", "N/A"):
                sector = None

            if price > 0:
                quote = {"price": price, "sector": sector}
                quotes[symbol] = quote
                _QUOTE_CACHE[symbol] = (now, quote)
        except Exception as exc:  # noqa: BLE001 - yfinance raises broadly
            logger.warning("Quote lookup failed for %s: %s", symbol, exc)

    return quotes


def _owned_portfolio(portfolio_id: int, user_id: int, db: Session) -> Portfolio:
    """Fetch a portfolio or 404. Scoped to the owner, so another user's id is a 404."""
    portfolio = db.query(Portfolio).filter(
        Portfolio.id == portfolio_id,
        Portfolio.user_id == user_id,
    ).first()

    if not portfolio:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Portfolio not found",
        )
    return portfolio


def _scoped_transactions(
    db: Session,
    user_id: int,
    portfolio_id: Optional[int],
) -> List[Transaction]:
    """
    The user's transactions, optionally narrowed to one portfolio.

    With no `portfolio_id` the analysis spans every portfolio, which is
    the right default: concentration and risk are properties of
    everything you own, not of the folders you filed it under. Passing
    one scopes the analysis to that portfolio, and an id belonging to
    someone else (or to nothing) is a 404 rather than a silent fallback
    to "everything".
    """
    query = db.query(Transaction).filter(Transaction.user_id == user_id)

    if portfolio_id is not None:
        _owned_portfolio(portfolio_id, user_id, db)
        query = query.filter(Transaction.portfolio_id == portfolio_id)

    return query.all()


def _build_view(transactions: List[Transaction]) -> tuple:
    """Replay a ledger, price it, and summarise. Returns (holdings, summary)."""
    try:
        derived = PortfolioTracker.build_holdings(transactions)
    except InsufficientHoldingError as exc:
        # The ledger itself is inconsistent. This should be prevented at
        # write time, so surface it loudly rather than showing a wrong total.
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Transaction history is inconsistent: {exc}",
        )

    symbols = [h.get("asset_symbol") for h in derived["holdings"]]
    quotes = _fetch_quotes(symbols)
    valued = PortfolioTracker.value_holdings(
        derived["holdings"],
        {s: q["price"] for s, q in quotes.items()},
        sectors={s: q["sector"] for s, q in quotes.items() if q["sector"]},
    )
    summary = PortfolioTracker.summarise(
        valued,
        realised_pnl=derived["realised_pnl"],
        dividend_income=derived["dividend_income"],
    )
    return valued, summary


# ── Aggregate views (declared before /{portfolio_id} so they match) ──

@router.get("/overview", response_model=PortfolioOverviewResponse)
async def get_portfolio_overview(
    current_user_id: int = Depends(get_current_user),
    db: Session = Depends(get_db),
    portfolio_id: Optional[int] = None,
):
    """
    Holdings and totals, across every portfolio or within one.

    This is what the dashboard shows. With no transactions recorded it
    returns zeros and an empty holdings list, not an error.

    Note that holdings are merged by asset across portfolios: the same
    stock bought in two portfolios is one position, which is what a
    concentration view needs.
    """
    transactions = _scoped_transactions(db, current_user_id, portfolio_id)

    holdings, summary = _build_view(transactions)
    num_portfolios = 1 if portfolio_id is not None else db.query(Portfolio).filter(
        Portfolio.user_id == current_user_id
    ).count()

    return {
        "summary": summary,
        "holdings": holdings,
        "num_portfolios": num_portfolios,
        "portfolio_id": portfolio_id,
    }


@router.get("/holdings/diversification")
async def get_holdings_for_diversification(
    current_user_id: int = Depends(get_current_user),
    db: Session = Depends(get_db),
    portfolio_id: Optional[int] = None,
):
    """
    Real holdings reshaped for the diversification analyzer.

    Lets the Diversification page analyse the user's actual portfolio
    instead of generated sample data.

    Sector is not stored on a transaction; it is resolved from market
    data for holdings that have a ticker, and non-equity assets (gold,
    bonds) are their own sector. Whatever is left stays "Unclassified"
    rather than being guessed, and `coverage` reports how much of the
    portfolio that affects so the caller can caveat the score.

    Spans every portfolio by default, since concentration is a property
    of everything owned. Pass `portfolio_id` to analyse one in isolation.

    Returns an empty list rather than an error when nothing is held: the
    analyzer rejects an empty holdings list, so the caller must not send
    one.
    """
    transactions = _scoped_transactions(db, current_user_id, portfolio_id)

    holdings, _ = _build_view(transactions)
    shaped = PortfolioTracker.to_diversification_holdings(holdings)
    coverage = PortfolioTracker.sector_coverage(holdings)

    return {
        "holdings": shaped,
        "portfolio_id": portfolio_id,
        "coverage": coverage,
        "note": (
            f"{coverage['classified_holdings']} of {coverage['total_holdings']} holdings "
            f"({coverage['classified_value_percent']}% by value) have a known sector. "
            "Holdings without a ticker cannot be classified and are reported as Unclassified."
        ) if shaped else "No holdings recorded yet.",
    }


@router.get("/value-series")
async def get_portfolio_value_series(
    current_user_id: int = Depends(get_current_user),
    db: Session = Depends(get_db),
    period: str = "1y",
    portfolio_id: Optional[int] = None,
):
    """
    The portfolio's daily value as a time-weighted index.

    This is what Portfolio Analytics needs in order to compute volatility,
    Sharpe and drawdown from the user's real holdings instead of a
    generated series. The index moves only with prices, never with
    deposits or withdrawals (see `build_value_series`), so the risk
    metrics describe the investments rather than the saving habit.

    The series is an INDEX rebased to 100, not a balance. Because
    cashflows are excluded its level cannot track the portfolio's actual
    worth, so it is deliberately not denominated in rupees.
    `opening_value` says what the first day's 100 was worth.

    Holdings with no price history are excluded and reported in
    `coverage`, because carrying them flat would understate volatility.

    Spans every portfolio by default. Pass `portfolio_id` to measure one
    in isolation, which is how two strategies can be compared.

    Returns an empty series rather than an error when there is nothing
    to measure; the analyzer needs at least two points.
    """
    transactions = _scoped_transactions(db, current_user_id, portfolio_id)

    if not transactions:
        return {
            "series": [], "opening_value": 0.0,
            "coverage": {"priced_holdings": 0, "total_holdings": 0,
                         "priced_value_percent": 0.0},
            "excluded_holdings": [],
            "note": "No transactions recorded yet.",
        }

    symbols = {
        (t.asset_symbol or "").strip().upper()
        for t in transactions if (t.asset_symbol or "").strip()
    }

    price_history: Dict[str, Dict] = {}
    for symbol in symbols:
        try:
            frame = load_history(symbol, period=period)
            price_history[symbol] = {
                index.date().isoformat(): float(close)
                for index, close in frame["close"].items()
                if close and close > 0
            }
        except Exception as exc:  # noqa: BLE001 - price data is best-effort
            logger.warning("History unavailable for %s: %s", symbol, exc)

    result = PortfolioTracker.build_value_series(transactions, price_history)

    coverage = result["coverage"]
    if not result["series"]:
        note = (
            "No price history is available for any holding, so a value series "
            "cannot be built. Add a ticker symbol to a holding to enable this."
        )
    elif coverage["priced_value_percent"] < 100:
        note = (
            f"Covers {coverage['priced_value_percent']}% of invested value. "
            f"{len(result['excluded_holdings'])} holding(s) without price history "
            "are excluded, because valuing them flat would understate volatility."
        )
    else:
        note = "Covers 100% of invested value."

    return {**result, "note": note, "period": period, "portfolio_id": portfolio_id}


# ── Portfolio CRUD ───────────────────────────────────────────────────

@router.post("/", response_model=PortfolioResponse, status_code=status.HTTP_201_CREATED)
async def create_portfolio(
    payload: PortfolioCreate,
    current_user_id: int = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Create an empty portfolio to record transactions against."""
    portfolio = Portfolio(
        user_id=current_user_id,
        portfolio_name=payload.portfolio_name,
        portfolio_type=payload.portfolio_type,
        notes=payload.notes,
        is_active=True,
        allocation={},          # NOT NULL in the schema; holdings are derived
        total_value=0.0,
        invested_amount=0.0,
        current_amount=0.0,
        current_return=0.0,
    )

    db.add(portfolio)
    db.commit()
    db.refresh(portfolio)
    return portfolio


@router.get("/", response_model=List[PortfolioResponse])
async def list_portfolios(
    current_user_id: int = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Every portfolio the user owns, newest first."""
    return db.query(Portfolio).filter(
        Portfolio.user_id == current_user_id
    ).order_by(Portfolio.created_at.desc()).all()


@router.get("/{portfolio_id}", response_model=PortfolioDetailResponse)
async def get_portfolio(
    portfolio_id: int,
    current_user_id: int = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    A portfolio with its derived holdings and totals.

    The stored snapshot columns are refreshed here, so a later list call
    shows the values this view computed.
    """
    portfolio = _owned_portfolio(portfolio_id, current_user_id, db)

    transactions = db.query(Transaction).filter(
        Transaction.portfolio_id == portfolio_id,
        Transaction.user_id == current_user_id,
    ).all()

    holdings, summary = _build_view(transactions)

    portfolio.invested_amount = summary["invested_amount"]
    portfolio.current_amount = summary["current_value"]
    portfolio.total_value = summary["current_value"]
    portfolio.current_return = summary["total_return_percent"]
    db.commit()
    db.refresh(portfolio)

    return {
        "portfolio": portfolio,
        "summary": summary,
        "holdings": holdings,
        "transaction_count": len(transactions),
    }


@router.put("/{portfolio_id}", response_model=PortfolioResponse)
async def update_portfolio(
    portfolio_id: int,
    payload: PortfolioUpdate,
    current_user_id: int = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Rename a portfolio, change its notes, or deactivate it."""
    portfolio = _owned_portfolio(portfolio_id, current_user_id, db)

    for field, value in payload.dict(exclude_unset=True).items():
        setattr(portfolio, field, value)

    db.commit()
    db.refresh(portfolio)
    return portfolio


@router.delete("/{portfolio_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_portfolio(
    portfolio_id: int,
    current_user_id: int = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Delete a portfolio and the transactions recorded against it.

    Transactions are deleted explicitly: the relationship has no cascade,
    so without this they would be left orphaned with a dangling
    portfolio_id and would still count towards the dashboard totals.
    """
    portfolio = _owned_portfolio(portfolio_id, current_user_id, db)

    db.query(Transaction).filter(
        Transaction.portfolio_id == portfolio_id,
        Transaction.user_id == current_user_id,
    ).delete(synchronize_session=False)

    db.delete(portfolio)
    db.commit()
    return None


# ── Transactions ─────────────────────────────────────────────────────

@router.post(
    "/{portfolio_id}/transactions",
    response_model=TransactionResponse,
    status_code=status.HTTP_201_CREATED,
)
async def add_transaction(
    portfolio_id: int,
    payload: TransactionCreate,
    current_user_id: int = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Record a buy, sell, SIP instalment or dividend.

    A sale is validated against the quantity actually held at that point
    in the ledger and rejected if it would oversell, so the stored
    history can never describe an impossible position.
    """
    _owned_portfolio(portfolio_id, current_user_id, db)

    total_amount = payload.quantity * payload.price_per_unit

    transaction = Transaction(
        user_id=current_user_id,
        portfolio_id=portfolio_id,
        transaction_type=payload.transaction_type,
        asset_type=payload.asset_type,
        asset_name=payload.asset_name,
        asset_symbol=payload.asset_symbol,
        quantity=payload.quantity,
        price_per_unit=payload.price_per_unit,
        total_amount=total_amount,
        fees=payload.fees,
        transaction_date=payload.transaction_date,
        notes=payload.notes,
    )

    # Replay the existing ledger plus this transaction before saving it.
    # Validating the whole history (rather than just the current balance)
    # also catches a back-dated sale inserted before its purchase.
    existing = db.query(Transaction).filter(
        Transaction.portfolio_id == portfolio_id,
        Transaction.user_id == current_user_id,
    ).all()

    try:
        PortfolioTracker.build_holdings(existing + [transaction])
    except InsufficientHoldingError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        )

    db.add(transaction)
    db.commit()
    db.refresh(transaction)
    return transaction


@router.get("/{portfolio_id}/transactions", response_model=List[TransactionResponse])
async def list_transactions(
    portfolio_id: int,
    current_user_id: int = Depends(get_current_user),
    db: Session = Depends(get_db),
    asset_symbol: Optional[str] = None,
):
    """Transaction ledger for one portfolio, newest first."""
    _owned_portfolio(portfolio_id, current_user_id, db)

    query = db.query(Transaction).filter(
        Transaction.portfolio_id == portfolio_id,
        Transaction.user_id == current_user_id,
    )
    if asset_symbol:
        query = query.filter(Transaction.asset_symbol == asset_symbol.strip().upper())

    return query.order_by(
        Transaction.transaction_date.desc(), Transaction.id.desc()
    ).all()


@router.delete(
    "/{portfolio_id}/transactions/{transaction_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def delete_transaction(
    portfolio_id: int,
    transaction_id: int,
    current_user_id: int = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Delete a transaction.

    Removing a purchase can leave a later sale overselling, so the
    remaining ledger is replayed first and the deletion refused if it
    would make the history impossible.
    """
    _owned_portfolio(portfolio_id, current_user_id, db)

    transaction = db.query(Transaction).filter(
        Transaction.id == transaction_id,
        Transaction.portfolio_id == portfolio_id,
        Transaction.user_id == current_user_id,
    ).first()

    if not transaction:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Transaction not found",
        )

    remaining = db.query(Transaction).filter(
        Transaction.portfolio_id == portfolio_id,
        Transaction.user_id == current_user_id,
        Transaction.id != transaction_id,
    ).all()

    try:
        PortfolioTracker.build_holdings(remaining)
    except InsufficientHoldingError as exc:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=(
                f"Deleting this transaction would make the history impossible: {exc}. "
                "Delete the later sale first."
            ),
        )

    db.delete(transaction)
    db.commit()
    return None
