"""
Portfolio Tracker

Turns a transaction ledger into current holdings, valuations and profit
and loss.

Holdings are DERIVED from transactions rather than stored as their own
rows. A stored holding has to be kept in step with every buy, sell and
correction, and the two drift apart the moment one write fails. Deriving
them means the ledger is the only thing that can be wrong, and a holding
can always be explained by the transactions that produced it.

Cost basis uses the AVERAGE COST method: every unit of an asset is
treated as having cost the running average. This is what Indian mutual
funds report, it needs no lot tracking, and it makes a partial sale
unambiguous. FIFO would give different realised figures and is left for
a later phase.

Nothing here touches the database or the network. Prices arrive as a
plain lookup dict, so the whole module is testable with no I/O.
"""

from typing import Dict, Iterable, List, Optional, Tuple

# Transaction types the ledger understands.
BUY = "Buy"
SELL = "Sell"
SIP = "SIP"
DIVIDEND = "Dividend"

# SIP instalments are purchases; they are a separate type only so the UI
# can show where the money came from.
PURCHASE_TYPES = (BUY, SIP)

# Below this many units a position is treated as fully closed. Floating
# point subtraction of equal quantities rarely lands exactly on zero.
CLOSED_POSITION_EPSILON = 1e-9

# Where a valuation price came from. Never guess silently: a holding
# priced from its own purchase price shows no gain by construction, and
# the caller has to be able to tell that apart from a real flat return.
PRICE_LIVE = "live"
PRICE_LAST_TRADE = "last_transaction_price"

# Sector shown when nothing could classify the holding. Deliberately a
# real bucket rather than a blank, so it is visible in the breakdown
# instead of silently merging with something else.
UNCLASSIFIED_SECTOR = "Unclassified"

# Asset types that are their own sector. A gold bond or a bond fund has
# no equity sector, and filing them under "Unclassified" would overstate
# how much of the portfolio is genuinely unknown.
NON_EQUITY_ASSET_TYPES = ("Gold", "Bonds")


class InsufficientHoldingError(ValueError):
    """Raised when a sale exceeds the quantity actually held."""


class PortfolioTracker:
    """Derives holdings and performance from a transaction ledger."""

    @staticmethod
    def _position_key(transaction) -> Tuple[str, str]:
        """
        Identity of a position.

        Symbol when there is one, otherwise the name, paired with the
        asset type. Two assets with the same name but different types
        (a gold ETF and physical gold) stay separate positions.
        """
        symbol = (getattr(transaction, "asset_symbol", None) or "").strip()
        name = (transaction.asset_name or "").strip()
        return (symbol.upper() if symbol else name.lower(), transaction.asset_type)

    @staticmethod
    def build_holdings(transactions: Iterable) -> Dict:
        """
        Replay a ledger into open positions and realised results.

        Transactions are processed in date order, then by id, so a buy
        and a sell recorded on the same day are applied in the order
        they were entered.

        Args:
            transactions: Transaction model instances (or any object with
                the same attributes).

        Returns:
            dict with:
              holdings: list of open positions, largest cost basis first
              realised_pnl: profit/loss already booked by sales
              dividend_income: dividends received
              closed_positions: positions sold down to nothing

        Raises:
            InsufficientHoldingError: a sale exceeded the quantity held.
        """
        ordered = sorted(
            transactions,
            key=lambda t: (t.transaction_date, t.id or 0),
        )

        positions: Dict[Tuple[str, str], Dict] = {}
        realised_pnl = 0.0
        dividend_income = 0.0

        for txn in ordered:
            key = PortfolioTracker._position_key(txn)
            quantity = float(txn.quantity or 0.0)
            fees = float(txn.fees or 0.0)
            total = float(txn.total_amount or 0.0)

            position = positions.setdefault(key, {
                "asset_name": txn.asset_name,
                "asset_symbol": txn.asset_symbol,
                "asset_type": txn.asset_type,
                "quantity": 0.0,
                "cost_basis": 0.0,
                "realised_pnl": 0.0,
                "dividend_income": 0.0,
                "last_price": float(txn.price_per_unit or 0.0),
                "transaction_count": 0,
            })
            position["transaction_count"] += 1
            if txn.price_per_unit:
                position["last_price"] = float(txn.price_per_unit)

            if txn.transaction_type in PURCHASE_TYPES:
                # Fees are part of what the position cost to acquire.
                position["quantity"] += quantity
                position["cost_basis"] += total + fees

            elif txn.transaction_type == SELL:
                held = position["quantity"]
                if quantity > held + CLOSED_POSITION_EPSILON:
                    raise InsufficientHoldingError(
                        f"Cannot sell {quantity:g} of {txn.asset_name}: "
                        f"only {held:g} held on {txn.transaction_date}"
                    )

                # Average cost: remove the proportional share of basis.
                average_cost = position["cost_basis"] / held if held else 0.0
                cost_removed = average_cost * quantity
                proceeds = total - fees

                booked = proceeds - cost_removed
                position["realised_pnl"] += booked
                realised_pnl += booked

                position["quantity"] = held - quantity
                position["cost_basis"] = max(0.0, position["cost_basis"] - cost_removed)

            elif txn.transaction_type == DIVIDEND:
                # Income, not a change in the position's size or cost.
                position["dividend_income"] += total
                dividend_income += total

            else:
                raise ValueError(f"Unknown transaction type: {txn.transaction_type!r}")

        open_positions, closed_positions = [], []
        for position in positions.values():
            if position["quantity"] > CLOSED_POSITION_EPSILON:
                position["average_cost"] = round(
                    position["cost_basis"] / position["quantity"], 4
                )
                open_positions.append(position)
            else:
                position["quantity"] = 0.0
                position["cost_basis"] = 0.0
                position["average_cost"] = 0.0
                closed_positions.append(position)

        open_positions.sort(key=lambda p: p["cost_basis"], reverse=True)

        return {
            "holdings": open_positions,
            "closed_positions": closed_positions,
            "realised_pnl": round(realised_pnl, 2),
            "dividend_income": round(dividend_income, 2),
        }

    @staticmethod
    def value_holdings(
        holdings: List[Dict],
        prices: Optional[Dict[str, float]] = None,
        sectors: Optional[Dict[str, str]] = None,
    ) -> List[Dict]:
        """
        Attach a current price, sector and unrealised profit to each holding.

        A holding whose price could not be fetched falls back to the
        price of its last transaction and is labelled
        `last_transaction_price`, exactly as the volatility service
        labels a historical fallback. Such a holding shows no gain
        because nothing has repriced it, which is very different from a
        genuine flat return, so the label travels with the number.

        Sector is looked up the same way. It is not recorded on a
        transaction, so it comes from the market-data provider when the
        holding has a ticker. Anything else is left unclassified rather
        than guessed, because inventing a sector would quietly corrupt
        the diversification score that reads it.

        Args:
            holdings: open positions from `build_holdings`
            prices: symbol (upper case) -> current price per unit
            sectors: symbol (upper case) -> sector name

        Returns:
            New list of holdings with valuation fields added.
        """
        prices = {k.upper(): v for k, v in (prices or {}).items()}
        sectors = {k.upper(): v for k, v in (sectors or {}).items()}
        valued = []

        for holding in holdings:
            priced = dict(holding)
            symbol = (holding.get("asset_symbol") or "").strip().upper()

            # Non-equity assets describe themselves: a gold bond's
            # "sector" is Gold. Only genuinely unknown ones stay blank.
            looked_up = sectors.get(symbol) if symbol else None
            if looked_up:
                priced["sector"] = looked_up
            elif holding["asset_type"] in NON_EQUITY_ASSET_TYPES:
                priced["sector"] = holding["asset_type"]
            else:
                priced["sector"] = holding.get("sector") or UNCLASSIFIED_SECTOR

            live_price = prices.get(symbol) if symbol else None
            if live_price and live_price > 0:
                price, source = float(live_price), PRICE_LIVE
            else:
                price, source = float(holding.get("last_price") or 0.0), PRICE_LAST_TRADE

            market_value = price * holding["quantity"]
            cost_basis = holding["cost_basis"]
            unrealised = market_value - cost_basis

            priced["current_price"] = round(price, 2)
            priced["price_source"] = source
            priced["market_value"] = round(market_value, 2)
            priced["cost_basis"] = round(cost_basis, 2)
            priced["unrealised_pnl"] = round(unrealised, 2)
            priced["unrealised_pnl_percent"] = (
                round((unrealised / cost_basis) * 100, 2) if cost_basis else 0.0
            )
            priced["quantity"] = round(holding["quantity"], 4)
            priced["realised_pnl"] = round(holding["realised_pnl"], 2)
            priced["dividend_income"] = round(holding["dividend_income"], 2)
            valued.append(priced)

        total_value = sum(h["market_value"] for h in valued)
        for holding in valued:
            holding["weight_percent"] = (
                round((holding["market_value"] / total_value) * 100, 2)
                if total_value else 0.0
            )

        return valued

    @staticmethod
    def summarise(
        valued_holdings: List[Dict],
        realised_pnl: float = 0.0,
        dividend_income: float = 0.0,
    ) -> Dict:
        """
        Portfolio totals.

        `total_return_percent` is measured against the cost of what is
        still held, and includes realised profit and dividends in the
        numerator. It is a simple return, not time-weighted: it ignores
        when money went in, so it is not comparable with a fund's
        published return. XIRR is listed as future work.
        """
        invested = sum(h["cost_basis"] for h in valued_holdings)
        current_value = sum(h["market_value"] for h in valued_holdings)
        unrealised = current_value - invested
        total_gain = unrealised + realised_pnl + dividend_income

        stale = [
            h for h in valued_holdings if h["price_source"] != PRICE_LIVE
        ]

        return {
            "num_holdings": len(valued_holdings),
            "invested_amount": round(invested, 2),
            "current_value": round(current_value, 2),
            "unrealised_pnl": round(unrealised, 2),
            "unrealised_pnl_percent": (
                round((unrealised / invested) * 100, 2) if invested else 0.0
            ),
            "realised_pnl": round(realised_pnl, 2),
            "dividend_income": round(dividend_income, 2),
            "total_gain": round(total_gain, 2),
            "total_return_percent": (
                round((total_gain / invested) * 100, 2) if invested else 0.0
            ),
            # Honesty flags, so the UI can say what it is showing.
            "holdings_priced_live": len(valued_holdings) - len(stale),
            "holdings_priced_from_last_trade": len(stale),
        }

    @staticmethod
    def to_diversification_holdings(valued_holdings: List[Dict]) -> List[Dict]:
        """
        Reshape holdings for the diversification analyzer.

        That module expects {name, value, sector, asset_type}. Sector
        comes from `value_holdings`, which resolves it from market data
        where it can. Anything still unresolved is passed through as
        "Unclassified" rather than guessed: a portfolio whose sectors are
        unknown should score as unknown, not as diversified.

        Worthless holdings are dropped because the analyzer requires a
        positive value for every holding.
        """
        return [
            {
                "name": h["asset_name"],
                "value": h["market_value"],
                "sector": h.get("sector") or UNCLASSIFIED_SECTOR,
                "asset_type": h["asset_type"],
            }
            for h in valued_holdings
            if h.get("market_value", 0) > 0
        ]

    @staticmethod
    def build_value_series(
        transactions: Iterable,
        price_history: Dict[str, Dict],
    ) -> Dict:
        """
        Reconstruct the portfolio's daily value as a TIME-WEIGHTED index.

        This is the input the risk analyzer needs, and the naive version
        of it is wrong. Simply totalling what the portfolio was worth each
        day makes every deposit look like a one-day gain: buy another
        50,000 rupees of stock and the raw series jumps 50,000, which the
        analyzer would read as a huge positive return and as volatility.
        Measured risk would then depend on how often the investor happened
        to add money.

        So each day's return is computed from PRICE MOVEMENT ONLY:
        yesterday's holdings are revalued at today's prices, and the
        day's transactions are applied afterwards. Chaining those returns
        gives a time-weighted index, the same convention funds use to
        report performance independently of investor cashflows.

        Dividends are added to the day's return, since they are a real
        gain that never shows up in a price series.

        Holdings with no price history (no ticker) are EXCLUDED rather
        than carried flat. A constant line has zero variance, so including
        one would mechanically drag measured volatility toward zero and
        make a portfolio look safer the less of it could be priced. The
        returned `coverage` says how much of the portfolio the series
        actually describes.

        Args:
            transactions: the full ledger
            price_history: symbol -> {date -> close}, dates as ISO strings

        The series is returned REBASED TO 100 on its first day. It is a
        performance index, not a balance: because cashflows are excluded,
        its level deliberately does not track what the portfolio is
        actually worth, and showing it in rupees invites exactly that
        misreading. Every metric the analyzer derives from it — returns,
        volatility, Sharpe, drawdown — depends only on ratios, so the
        base is free to be whatever is least misleading.

        Returns:
            dict with `series` ([{date, value}], ready for the analyzer),
            `coverage`, `excluded_holdings`, and `opening_value` (what the
            index's 100 represented in rupees on day one).
        """
        ordered = sorted(transactions, key=lambda t: (t.transaction_date, t.id or 0))
        if not ordered:
            return {"series": [], "opening_value": 0.0,
                    "coverage": PortfolioTracker._empty_coverage(),
                    "excluded_holdings": []}

        priced = {s.upper() for s in price_history if price_history[s]}

        def no_series() -> Dict:
            """Coverage is still reported when no series could be built, so the
            caller can say WHICH holdings were missing rather than just that
            something was."""
            return {
                "series": [],
                "opening_value": 0.0,
                "coverage": PortfolioTracker._series_coverage(ordered, priced),
                "excluded_holdings": sorted({
                    t.asset_name for t in ordered
                    if PortfolioTracker._position_key(t)[0] not in priced
                }),
            }

        # Trading dates come from the price data, so the series follows the
        # market calendar rather than inventing values for closed days.
        all_dates = sorted({d for s in priced for d in price_history[s]})
        start = min(t.transaction_date for t in ordered).isoformat()
        dates = [d for d in all_dates if d >= start]
        if not dates:
            return no_series()

        # Group transactions by date for replay.
        by_date: Dict[str, List] = {}
        for txn in ordered:
            by_date.setdefault(txn.transaction_date.isoformat(), []).append(txn)

        def price_on(symbol: str, date: str, last_known: Dict[str, float]):
            """Close on `date`, or the most recent close before it."""
            value = price_history.get(symbol, {}).get(date)
            if value and value > 0:
                last_known[symbol] = float(value)
            return last_known.get(symbol)

        quantities: Dict[str, float] = {}
        last_known: Dict[str, float] = {}
        series: List[Dict] = []
        nav = 0.0
        prev_value = 0.0

        # Any transaction dated before the first available price date is
        # applied up front, so its holding is present from day one.
        for date in sorted(d for d in by_date if d < dates[0]):
            for txn in by_date[date]:
                PortfolioTracker._apply_to_quantities(txn, quantities, priced)

        for date in dates:
            # Yesterday's holdings, revalued at today's prices. Today's
            # trades are deliberately not applied yet: including them
            # would fold a cashflow into the day's return.
            value_at_today_prices = sum(
                (price_on(symbol, date, last_known) or 0.0) * quantity
                for symbol, quantity in quantities.items()
            )

            if prev_value > 0:
                dividend = sum(
                    float(t.total_amount or 0.0)
                    for t in by_date.get(date, [])
                    if t.transaction_type == DIVIDEND
                    and PortfolioTracker._position_key(t)[0] in priced
                )
                daily_return = (value_at_today_prices + dividend) / prev_value - 1.0
                nav *= (1.0 + daily_return)
                series.append({"date": date, "value": round(nav, 2)})

            # Today's trades take effect from tomorrow's return onwards.
            for txn in by_date.get(date, []):
                PortfolioTracker._apply_to_quantities(txn, quantities, priced)

            prev_value = sum(
                (price_on(symbol, date, last_known) or 0.0) * quantity
                for symbol, quantity in quantities.items()
            )

            # Seed the index on the first day something is actually held,
            # so the series starts at the portfolio's real opening value.
            if nav <= 0 and prev_value > 0:
                nav = prev_value
                series.append({"date": date, "value": round(nav, 2)})

        # Rebase to 100 so the chart cannot be mistaken for a balance.
        opening = series[0]["value"] if series else 0.0
        if opening > 0:
            series = [
                {"date": p["date"], "value": round(p["value"] / opening * 100.0, 4)}
                for p in series
            ]

        return {
            "series": series,
            "opening_value": round(opening, 2),
            "coverage": PortfolioTracker._series_coverage(ordered, priced),
            "excluded_holdings": sorted({
                t.asset_name for t in ordered
                if PortfolioTracker._position_key(t)[0] not in priced
            }),
        }

    @staticmethod
    def _apply_to_quantities(txn, quantities: Dict[str, float], priced: set) -> None:
        """Apply one transaction to the running quantity map (priced symbols only)."""
        symbol = PortfolioTracker._position_key(txn)[0]
        if symbol not in priced:
            return
        quantity = float(txn.quantity or 0.0)
        if txn.transaction_type in PURCHASE_TYPES:
            quantities[symbol] = quantities.get(symbol, 0.0) + quantity
        elif txn.transaction_type == SELL:
            quantities[symbol] = max(0.0, quantities.get(symbol, 0.0) - quantity)

    @staticmethod
    def _empty_coverage() -> Dict:
        return {"priced_holdings": 0, "total_holdings": 0, "priced_value_percent": 0.0}

    @staticmethod
    def _series_coverage(transactions: List, priced: set) -> Dict:
        """How much of the portfolio's cost the price series actually covers."""
        cost_by_symbol: Dict[str, float] = {}
        for txn in transactions:
            if txn.transaction_type not in PURCHASE_TYPES:
                continue
            symbol = PortfolioTracker._position_key(txn)[0]
            cost_by_symbol[symbol] = (
                cost_by_symbol.get(symbol, 0.0)
                + float(txn.total_amount or 0.0) + float(txn.fees or 0.0)
            )

        total = sum(cost_by_symbol.values())
        covered = sum(v for s, v in cost_by_symbol.items() if s in priced)

        return {
            "priced_holdings": len([s for s in cost_by_symbol if s in priced]),
            "total_holdings": len(cost_by_symbol),
            "priced_value_percent": round((covered / total) * 100, 2) if total else 0.0,
        }

    @staticmethod
    def sector_coverage(valued_holdings: List[Dict]) -> Dict:
        """
        How much of the portfolio could actually be classified by sector.

        The diversification score is only as trustworthy as this number.
        A score computed over mostly-unclassified holdings says more
        about missing data than about the portfolio, and the UI needs to
        be able to say so.
        """
        total = sum(h.get("market_value", 0) for h in valued_holdings)
        unclassified = [
            h for h in valued_holdings
            if (h.get("sector") or UNCLASSIFIED_SECTOR) == UNCLASSIFIED_SECTOR
        ]
        unclassified_value = sum(h.get("market_value", 0) for h in unclassified)

        return {
            "total_holdings": len(valued_holdings),
            "classified_holdings": len(valued_holdings) - len(unclassified),
            "unclassified_holdings": len(unclassified),
            "unclassified_value": round(unclassified_value, 2),
            "classified_value_percent": (
                round(((total - unclassified_value) / total) * 100, 2) if total else 0.0
            ),
        }
