"""
Yahoo Finance Service
Integrates with Yahoo Finance API using yfinance
"""

import yfinance as yf
from typing import Dict, List, Optional
from datetime import datetime, timedelta


class YahooFinanceService:
    """
    Service for fetching stock data from Yahoo Finance
    """
    
    @staticmethod
    def get_stock_info(ticker: str) -> Dict:
        """
        Get stock information for a given ticker
        
        Args:
            ticker: Stock ticker symbol (e.g., 'AAPL', 'RELIANCE.NS')
            
        Returns:
            dict with stock information
            
        Raises:
            ValueError: If ticker is invalid or data not available
        """
        try:
            # Create ticker object
            stock = yf.Ticker(ticker.upper())
            
            # Get stock info
            info = stock.info
            
            # Check if valid data returned
            if not info or 'currentPrice' not in info and 'regularMarketPrice' not in info:
                raise ValueError(f"No data available for ticker: {ticker}")
            
            # Extract required information
            result = {
                'ticker': ticker.upper(),
                'company_name': info.get('longName', info.get('shortName', ticker.upper())),
                'current_price': info.get('currentPrice') or info.get('regularMarketPrice', 0),
                'currency': info.get('currency', 'USD'),
                'fifty_two_week_high': info.get('fiftyTwoWeekHigh', 0),
                'fifty_two_week_low': info.get('fiftyTwoWeekLow', 0),
                'market_cap': info.get('marketCap', 0),
                'volume': info.get('volume', 0),
                'average_volume': info.get('averageVolume', 0),
                'day_high': info.get('dayHigh', 0),
                'day_low': info.get('dayLow', 0),
                'open_price': info.get('open', 0),
                'previous_close': info.get('previousClose', 0),
                'sector': info.get('sector', 'N/A'),
                'industry': info.get('industry', 'N/A'),
                'exchange': info.get('exchange', 'N/A'),
                'website': info.get('website', ''),
                'description': info.get('longBusinessSummary', '')[:500]  # Limit to 500 chars
            }
            
            # Calculate change and change percentage
            if result['previous_close'] and result['current_price']:
                result['change'] = result['current_price'] - result['previous_close']
                result['change_percent'] = (result['change'] / result['previous_close']) * 100
            else:
                result['change'] = 0
                result['change_percent'] = 0
            
            return result
            
        except Exception as e:
            raise ValueError(f"Error fetching data for {ticker}: {str(e)}")
    
    @staticmethod
    def get_historical_data(
        ticker: str,
        period: str = "1y",
        interval: str = "1d"
    ) -> List[Dict]:
        """
        Get historical price data for a stock
        
        Args:
            ticker: Stock ticker symbol
            period: Data period (1d, 5d, 1mo, 3mo, 6mo, 1y, 2y, 5y, 10y, ytd, max)
            interval: Data interval (1m, 2m, 5m, 15m, 30m, 60m, 90m, 1h, 1d, 5d, 1wk, 1mo, 3mo)
            
        Returns:
            List of dict with date, open, high, low, close, volume
        """
        try:
            stock = yf.Ticker(ticker.upper())
            
            # Get historical data
            hist = stock.history(period=period, interval=interval)
            
            if hist.empty:
                raise ValueError(f"No historical data available for {ticker}")
            
            # Convert to list of dicts
            historical_data = []
            for index, row in hist.iterrows():
                historical_data.append({
                    'date': index.strftime('%Y-%m-%d') if hasattr(index, 'strftime') else str(index),
                    'open': round(float(row['Open']), 2),
                    'high': round(float(row['High']), 2),
                    'low': round(float(row['Low']), 2),
                    'close': round(float(row['Close']), 2),
                    'volume': int(row['Volume'])
                })
            
            return historical_data
            
        except Exception as e:
            raise ValueError(f"Error fetching historical data for {ticker}: {str(e)}")
    
    @staticmethod
    def search_stocks(query: str, limit: int = 10) -> List[Dict]:
        """
        Search for stocks by name or ticker
        
        Args:
            query: Search query (company name or ticker)
            limit: Maximum number of results
            
        Returns:
            List of matching stocks
            
        Note: This is a simple implementation. For production, use a dedicated search API.
        """
        # Common Indian stock tickers
        indian_stocks = [
            {'ticker': 'RELIANCE.NS', 'name': 'Reliance Industries', 'exchange': 'NSE'},
            {'ticker': 'TCS.NS', 'name': 'Tata Consultancy Services', 'exchange': 'NSE'},
            {'ticker': 'HDFCBANK.NS', 'name': 'HDFC Bank', 'exchange': 'NSE'},
            {'ticker': 'INFY.NS', 'name': 'Infosys', 'exchange': 'NSE'},
            {'ticker': 'ICICIBANK.NS', 'name': 'ICICI Bank', 'exchange': 'NSE'},
            {'ticker': 'HINDUNILVR.NS', 'name': 'Hindustan Unilever', 'exchange': 'NSE'},
            {'ticker': 'ITC.NS', 'name': 'ITC Limited', 'exchange': 'NSE'},
            {'ticker': 'SBIN.NS', 'name': 'State Bank of India', 'exchange': 'NSE'},
            {'ticker': 'BHARTIARTL.NS', 'name': 'Bharti Airtel', 'exchange': 'NSE'},
            {'ticker': 'KOTAKBANK.NS', 'name': 'Kotak Mahindra Bank', 'exchange': 'NSE'},
            {'ticker': 'LT.NS', 'name': 'Larsen & Toubro', 'exchange': 'NSE'},
            {'ticker': 'AXISBANK.NS', 'name': 'Axis Bank', 'exchange': 'NSE'},
            {'ticker': 'WIPRO.NS', 'name': 'Wipro', 'exchange': 'NSE'},
            {'ticker': 'MARUTI.NS', 'name': 'Maruti Suzuki', 'exchange': 'NSE'},
            {'ticker': 'TITAN.NS', 'name': 'Titan Company', 'exchange': 'NSE'},
        ]
        
        # Common US stock tickers
        us_stocks = [
            {'ticker': 'AAPL', 'name': 'Apple Inc.', 'exchange': 'NASDAQ'},
            {'ticker': 'MSFT', 'name': 'Microsoft Corporation', 'exchange': 'NASDAQ'},
            {'ticker': 'GOOGL', 'name': 'Alphabet Inc.', 'exchange': 'NASDAQ'},
            {'ticker': 'AMZN', 'name': 'Amazon.com Inc.', 'exchange': 'NASDAQ'},
            {'ticker': 'TSLA', 'name': 'Tesla Inc.', 'exchange': 'NASDAQ'},
            {'ticker': 'META', 'name': 'Meta Platforms Inc.', 'exchange': 'NASDAQ'},
            {'ticker': 'NVDA', 'name': 'NVIDIA Corporation', 'exchange': 'NASDAQ'},
            {'ticker': 'JPM', 'name': 'JPMorgan Chase & Co.', 'exchange': 'NYSE'},
            {'ticker': 'V', 'name': 'Visa Inc.', 'exchange': 'NYSE'},
            {'ticker': 'WMT', 'name': 'Walmart Inc.', 'exchange': 'NYSE'},
        ]
        
        all_stocks = indian_stocks + us_stocks
        
        # Filter based on query
        query_lower = query.lower()
        results = [
            stock for stock in all_stocks
            if query_lower in stock['ticker'].lower() or query_lower in stock['name'].lower()
        ]
        
        return results[:limit]
    
    @staticmethod
    def format_number(value: float, is_currency: bool = True) -> str:
        """
        Format large numbers for display
        
        Args:
            value: Number to format
            is_currency: Whether to format as currency
            
        Returns:
            Formatted string
        """
        if value >= 1_00_00_000:  # 1 Crore
            return f"₹{value / 1_00_00_000:.2f}Cr" if is_currency else f"{value / 1_00_00_000:.2f}Cr"
        elif value >= 1_00_000:  # 1 Lakh
            return f"₹{value / 1_00_000:.2f}L" if is_currency else f"{value / 1_00_000:.2f}L"
        elif value >= 1000:
            return f"₹{value / 1000:.2f}K" if is_currency else f"{value / 1000:.2f}K"
        else:
            return f"₹{value:.2f}" if is_currency else f"{value:.2f}"
