"""
Portfolio Tracking Schemas
Pydantic models for portfolios, transactions and derived holdings
"""

from datetime import date, datetime
from typing import List, Optional

from pydantic import BaseModel, Field, field_validator

TRANSACTION_TYPES = ["Buy", "Sell", "SIP", "Dividend"]
ASSET_TYPES = ["Stocks", "Mutual Funds", "Bonds", "Gold", "ETF", "Other"]
PORTFOLIO_TYPES = ["Custom", "Recommended", "Current"]


# ── Portfolio ────────────────────────────────────────────────────────

class PortfolioCreate(BaseModel):
    """Schema for creating a portfolio"""
    portfolio_name: str = Field(..., min_length=1, max_length=100)
    portfolio_type: str = Field(default="Custom")
    notes: Optional[str] = Field(None, max_length=500)

    @field_validator("portfolio_type")
    @classmethod
    def validate_portfolio_type(cls, v: str) -> str:
        if v not in PORTFOLIO_TYPES:
            raise ValueError(f"Portfolio type must be one of {PORTFOLIO_TYPES}")
        return v


class PortfolioUpdate(BaseModel):
    """Schema for updating a portfolio"""
    portfolio_name: Optional[str] = Field(None, min_length=1, max_length=100)
    notes: Optional[str] = Field(None, max_length=500)
    is_active: Optional[bool] = None


class PortfolioResponse(BaseModel):
    """Portfolio record as stored"""
    id: int
    user_id: int
    portfolio_name: str
    portfolio_type: str
    is_active: bool
    total_value: Optional[float] = None
    invested_amount: Optional[float] = None
    current_amount: Optional[float] = None
    current_return: Optional[float] = None
    risk_level: Optional[str] = None
    notes: Optional[str] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


# ── Transactions ─────────────────────────────────────────────────────

class TransactionCreate(BaseModel):
    """Schema for recording a transaction"""
    transaction_type: str = Field(..., description="Buy, Sell, SIP or Dividend")
    asset_type: str = Field(..., description="Stocks, Mutual Funds, Bonds, Gold, ETF, Other")
    asset_name: str = Field(..., min_length=1, max_length=120)
    asset_symbol: Optional[str] = Field(
        None, max_length=24,
        description="Ticker for live pricing, e.g. RELIANCE.NS. Optional.",
    )
    quantity: float = Field(..., gt=0, description="Units bought or sold")
    price_per_unit: float = Field(..., gt=0, description="Price per unit")
    fees: float = Field(default=0.0, ge=0, description="Brokerage and charges")
    transaction_date: date = Field(..., description="Date of the transaction")
    notes: Optional[str] = Field(None, max_length=300)

    @field_validator("transaction_type")
    @classmethod
    def validate_transaction_type(cls, v: str) -> str:
        if v not in TRANSACTION_TYPES:
            raise ValueError(f"Transaction type must be one of {TRANSACTION_TYPES}")
        return v

    @field_validator("asset_type")
    @classmethod
    def validate_asset_type(cls, v: str) -> str:
        if v not in ASSET_TYPES:
            raise ValueError(f"Asset type must be one of {ASSET_TYPES}")
        return v

    @field_validator("transaction_date")
    @classmethod
    def validate_not_future(cls, v: date) -> date:
        if v > date.today():
            raise ValueError("Transaction date cannot be in the future")
        return v

    @field_validator("asset_symbol")
    @classmethod
    def normalise_symbol(cls, v: Optional[str]) -> Optional[str]:
        if v is None:
            return None
        cleaned = v.strip().upper()
        return cleaned or None


class TransactionResponse(BaseModel):
    """Transaction record as stored"""
    id: int
    user_id: int
    portfolio_id: Optional[int] = None
    transaction_type: str
    asset_type: str
    asset_name: str
    asset_symbol: Optional[str] = None
    quantity: Optional[float] = None
    price_per_unit: float
    total_amount: float
    fees: Optional[float] = None
    transaction_date: date
    notes: Optional[str] = None
    created_at: Optional[datetime] = None

    class Config:
        from_attributes = True


# ── Derived holdings ─────────────────────────────────────────────────

class HoldingResponse(BaseModel):
    """A position derived from the transaction ledger"""
    asset_name: str
    asset_symbol: Optional[str] = None
    asset_type: str
    sector: Optional[str] = Field(
        None,
        description="Resolved from market data; 'Unclassified' when it could not be determined",
    )
    quantity: float
    average_cost: float
    cost_basis: float
    current_price: float
    price_source: str = Field(
        ...,
        description="'live' or 'last_transaction_price' when pricing was unavailable",
    )
    market_value: float
    unrealised_pnl: float
    unrealised_pnl_percent: float
    realised_pnl: float
    dividend_income: float
    weight_percent: float
    transaction_count: int


class PortfolioSummary(BaseModel):
    """Totals across a set of holdings"""
    num_holdings: int
    invested_amount: float
    current_value: float
    unrealised_pnl: float
    unrealised_pnl_percent: float
    realised_pnl: float
    dividend_income: float
    total_gain: float
    total_return_percent: float
    holdings_priced_live: int
    holdings_priced_from_last_trade: int


class PortfolioDetailResponse(BaseModel):
    """A portfolio with its derived holdings and totals"""
    portfolio: PortfolioResponse
    summary: PortfolioSummary
    holdings: List[HoldingResponse]
    transaction_count: int


class PortfolioOverviewResponse(BaseModel):
    """Aggregate across every portfolio the user owns (dashboard)"""
    summary: PortfolioSummary
    holdings: List[HoldingResponse]
    num_portfolios: int
