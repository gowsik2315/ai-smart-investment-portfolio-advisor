"""
Market Data API Routes
Handles stock search and market data using Yahoo Finance
"""

import logging
import time
from typing import Dict, Optional, Tuple

from fastapi import APIRouter, Depends, HTTPException, status, Header
from fastapi.concurrency import run_in_threadpool
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.dependencies import get_current_user
from app.core.security import get_current_user_id
from app.ml.data import InvalidTickerError, PriceDataError
from app.models.user import User
from app.schemas.ml_prediction import TrendExplanationResponse
from app.schemas.stock import (
    StockInfoResponse,
    HistoricalDataResponse,
    StockSearchResponse,
    HistoricalDataPoint
)
from app.services.explanation_guard import apply_outlook_guard
from app.services.stock_trend_service import stock_trend_service
from app.services.yahoo_finance_service import YahooFinanceService
from app.services.ollama_service import ollama_service
from app.services.ollama_prompts import OllamaPrompts

logger = logging.getLogger(__name__)

router = APIRouter()

# A Stock Predictor explanation depends only on the outlook's numbers, and
# on CPU the 3B model needs ~40-100s to write one. Successful explanations
# are therefore cached in memory, keyed on everything the prompt uses, so
# re-opening the same stock does not wait for the model again.
_OUTLOOK_EXPLAIN_TTL_SECONDS = 6 * 3600
_OUTLOOK_EXPLAIN_MAX_ENTRIES = 128
_outlook_explain_cache: Dict[Tuple, Tuple[float, str]] = {}


def _outlook_cache_key(outlook: Dict) -> Tuple:
    return (
        outlook["ticker"],
        outlook["as_of"],
        outlook["probability_source"],
        outlook.get("model_version"),
        round(outlook["probability_up"], 4),
        round(outlook["volatility"], 4),
    )




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


@router.get("/stock/{ticker}/outlook/explain", response_model=TrendExplanationResponse)
async def explain_stock_outlook(
    ticker: str,
    current_user_id: int = Depends(get_current_user)
):
    """
    AI-generated plain-language explanation of the Stock Predictor outlook.

    This is Ollama prose, not a model output, and it lives here rather than
    under /api/ml/* so that distinction survives in the API surface. The
    numbers it explains come from `/api/ml/trend-outlook/{ticker}`.

    The prompt forbids calling the historical base rate a prediction,
    saying the stock "will" move, and buy/sell advice. A failed or disabled
    Ollama is reported through `ai_available`, not an error status, so the
    page degrades the way the other modules do.
    """
    try:
        outlook = await run_in_threadpool(stock_trend_service.get_outlook, ticker)
    except InvalidTickerError as e:
        raise HTTPException(status_code=422, detail=str(e))
    except PriceDataError as e:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"Price data unavailable for {ticker}: {e}",
        )
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

    base = {
        "ticker": outlook["ticker"],
        "as_of": outlook["as_of"],
        "probability_source": outlook["probability_source"],
        "disclaimer": outlook["disclaimer"],
    }

    key = _outlook_cache_key(outlook)
    hit = _outlook_explain_cache.get(key)
    if hit and (time.monotonic() - hit[0]) < _OUTLOOK_EXPLAIN_TTL_SECONDS:
        return TrendExplanationResponse(
            **base, ai_explanation=hit[1], ai_available=True, cached=True
        )

    result = await ollama_service.generate_explanation(
        prompt=OllamaPrompts.stock_outlook_explanation(outlook),
        system_prompt=OllamaPrompts.SYSTEM_FINANCIAL_ADVISOR,
        temperature=0.3,   # lower than elsewhere: this one must stay factual
        max_tokens=400,
    )

    if not result.get("success"):
        return TrendExplanationResponse(
            **base,
            ai_explanation=result.get("explanation", "AI explanation unavailable"),
            ai_available=False,
            cached=False,
        )

    # The prompt asks the model to follow the rules; this checks that it did.
    safe_text, rejection = apply_outlook_guard(result["explanation"], outlook)
    if safe_text is None:
        logger.warning(
            "Discarded outlook explanation for %s: %s | text: %.300s",
            outlook["ticker"], rejection, result["explanation"],
        )
        return TrendExplanationResponse(
            **base,
            ai_explanation=(
                "The generated explanation broke the wording rules for this module "
                "and was discarded. Try again."
            ),
            ai_available=False,
            cached=False,
        )

    if len(_outlook_explain_cache) >= _OUTLOOK_EXPLAIN_MAX_ENTRIES:
        _outlook_explain_cache.pop(next(iter(_outlook_explain_cache)))
    _outlook_explain_cache[key] = (time.monotonic(), safe_text)

    return TrendExplanationResponse(
        **base, ai_explanation=safe_text, ai_available=True, cached=False,
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
