"""
Market Data API Routes
Handles stock search and market data using Yahoo Finance
"""

from fastapi import APIRouter, Depends, HTTPException, status, Header
from sqlalchemy.orm import Session
from typing import Optional

from app.core.database import get_db
from app.core.dependencies import get_current_user
from app.core.security import get_current_user_id
from app.models.user import User
from app.schemas.stock import (
    StockInfoResponse,
    HistoricalDataResponse,
    StockSearchResponse,
    HistoricalDataPoint
)
from app.services.yahoo_finance_service import YahooFinanceService
from app.services.ollama_service import ollama_service
from app.services.ollama_prompts import OllamaPrompts


router = APIRouter()




@router.get("/search", response_model=StockSearchResponse)
async def search_stocks(
    query: str,
    limit: int = 10,
    current_user_id: int = Depends(get_current_user)
):
    """
    Search for stocks by ticker or company name
    
    Args:
        query: Search query (ticker or company name)
        limit: Maximum number of results (default: 10)
    
    Returns:
        List of matching stocks with ticker, name, and exchange
    """
    try:
        results = YahooFinanceService.search_stocks(query, limit)
        return {
            'query': query,
            'results': results
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Search failed: {str(e)}"
        )


@router.get("/stock/{ticker}", response_model=StockInfoResponse)
async def get_stock_info(
    ticker: str,
    current_user_id: int = Depends(get_current_user)
):
    """
    Get detailed stock information
    
    Args:
        ticker: Stock ticker symbol (e.g., 'AAPL', 'RELIANCE.NS')
    
    Returns:
        Detailed stock information including:
        - Company name
        - Current price
        - 52-week high/low
        - Market cap
        - Volume
        - Day high/low
        - Price change
        - Sector and industry
    """
    try:
        stock_info = YahooFinanceService.get_stock_info(ticker)
        return stock_info
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch stock data: {str(e)}"
        )


@router.get("/stock/{ticker}/history", response_model=HistoricalDataResponse)
async def get_stock_history(
    ticker: str,
    period: str = "1y",
    interval: str = "1d",
    current_user_id: int = Depends(get_current_user)
):
    """
    Get historical price data for a stock
    
    Args:
        ticker: Stock ticker symbol
        period: Data period (1d, 5d, 1mo, 3mo, 6mo, 1y, 2y, 5y, 10y, ytd, max)
        interval: Data interval (1d, 5d, 1wk, 1mo)
    
    Returns:
        Historical price data with date, open, high, low, close, volume
    """
    try:
        historical_data = YahooFinanceService.get_historical_data(
            ticker=ticker,
            period=period,
            interval=interval
        )
        
        return {
            'ticker': ticker.upper(),
            'period': period,
            'interval': interval,
            'data': historical_data
        }
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch historical data: {str(e)}"
        )


@router.get("/stock/{ticker}/explain")
async def explain_stock_trend(
    ticker: str,
    period: str = "1mo",
    current_user_id: int = Depends(get_current_user)
):
    """
    Get AI-powered explanation of stock trend
    
    Returns detailed AI-generated analysis of:
    - Price trend analysis
    - What the trend indicates
    - Key factors to consider
    - Whether it's a good time to research further
    """
    try:
        # Get stock info
        stock_info = YahooFinanceService.get_stock_info(ticker)
        
        # Get historical data
        historical_data = YahooFinanceService.get_historical_data(ticker, period=period)
        
        # Generate AI explanation prompt
        prompt = OllamaPrompts.stock_trend_explanation(
            ticker=ticker,
            company_name=stock_info.get('company_name', ticker),
            current_price=stock_info.get('current_price', 0),
            price_change_percent=stock_info.get('change_percent', 0),
            historical_data=historical_data,
            period=period
        )
        
        # Get AI explanation
        result = await ollama_service.generate_explanation(
            prompt=prompt,
            system_prompt=OllamaPrompts.SYSTEM_FINANCIAL_ADVISOR,
            temperature=0.7
        )
        
        return {
            "ticker": ticker,
            "company_name": stock_info.get('company_name', ticker),
            "current_price": stock_info.get('current_price', 0),
            "change_percent": stock_info.get('change_percent', 0),
            "period": period,
            "ai_explanation": result.get("explanation", "AI explanation unavailable"),
            "ai_available": result.get("success", False)
        }
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to generate explanation: {str(e)}"
        )
