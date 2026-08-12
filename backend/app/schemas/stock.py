"""
Stock Data Schemas
Pydantic models for stock market data
"""

from pydantic import BaseModel, Field
from typing import List, Optional


class StockInfoResponse(BaseModel):
    """Schema for stock information response"""
    ticker: str
    company_name: str
    current_price: float
    currency: str
    fifty_two_week_high: float
    fifty_two_week_low: float
    market_cap: float
    volume: int
    average_volume: int
    day_high: float
    day_low: float
    open_price: float
    previous_close: float
    change: float
    change_percent: float
    sector: str
    industry: str
    exchange: str
    website: Optional[str]
    description: Optional[str]


class HistoricalDataPoint(BaseModel):
    """Schema for historical data point"""
    date: str
    open: float
    high: float
    low: float
    close: float
    volume: int


class HistoricalDataResponse(BaseModel):
    """Schema for historical data response"""
    ticker: str
    period: str
    interval: str
    data: List[HistoricalDataPoint]


class StockSearchResult(BaseModel):
    """Schema for stock search result"""
    ticker: str
    name: str
    exchange: str


class StockSearchResponse(BaseModel):
    """Schema for stock search response"""
    query: str
    results: List[StockSearchResult]
