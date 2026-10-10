"""
Price History Loader

Downloads daily OHLCV history from Yahoo Finance and caches it to parquet
on disk. yfinance is an unofficial scraper: it rate-limits, it returns
empty frames under load, and it occasionally changes column shape. Every
training run and every prediction request hitting it live would be both
slow and unreliable, so results are cached and served from disk by
default.

Used by training and by inference alike.
"""

from __future__ import annotations

import logging
import re
import time
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Dict, List, Optional

import pandas as pd

from app.ml.config import (
    CACHE_DIR,
    CACHE_TTL_HOURS,
    HISTORY_PERIOD,
)

logger = logging.getLogger(__name__)

# Canonical column set returned by every loader function here
OHLCV_COLUMNS = ["open", "high", "low", "close", "volume"]


class PriceDataError(RuntimeError):
    """Raised when usable price history cannot be obtained."""


class InvalidTickerError(PriceDataError):
    """Raised for a ticker that is not a plausible Yahoo Finance symbol."""


# Yahoo symbols are letters, digits and a few separators: RELIANCE.NS,
# M&M.NS, BAJAJ-AUTO.NS, ^NSEI, GC=F.
_TICKER_RE = re.compile(r"^[A-Z0-9^][A-Z0-9.\-&=^]{0,31}$")


def validate_ticker(ticker: str) -> str:
    """
    Normalise a ticker and reject anything that is not a plausible symbol.

    The ticker becomes part of a cache filename, so this is a security
    boundary and not just input hygiene. The previous sanitiser replaced
    '/' and '.' but not '\\' or ':'. On Windows, joining a path with a
    segment like 'C:\\Users\\x' yields an absolute path outside the cache
    directory, so a crafted ticker could make the cache write a parquet
    file anywhere the process can write.
    """
    cleaned = (ticker or "").strip().upper()
    if not _TICKER_RE.match(cleaned):
        raise InvalidTickerError(
            f"'{ticker}' is not a valid ticker symbol "
            f"(letters, digits and . - & = ^ only, up to 32 characters)"
        )
    return cleaned


def _cache_path(ticker: str, period: str) -> Path:
    """Filesystem-safe cache location for one ticker/period pair."""
    safe = validate_ticker(ticker).replace("^", "INDEX_").replace(".", "_")
    return CACHE_DIR / f"{safe}__{period}.parquet"


def _is_fresh(path: Path, ttl_hours: int) -> bool:
    """True if `path` exists and is younger than `ttl_hours`."""
    if not path.exists():
        return False
    age = datetime.now(timezone.utc) - datetime.fromtimestamp(
        path.stat().st_mtime, tz=timezone.utc
    )
    return age < timedelta(hours=ttl_hours)


def _normalise(raw: pd.DataFrame, ticker: str) -> pd.DataFrame:
    """
    Reduce a yfinance frame to lowercase OHLCV with a clean DatetimeIndex.

    Handles the MultiIndex columns yfinance returns when asked for more
    than one ticker, and the flat columns it returns for one.
    """
    if raw is None or raw.empty:
        raise PriceDataError(f"No price data returned for {ticker}")

    df = raw.copy()

    # Flatten ('Close', 'RELIANCE.NS') style columns
    if isinstance(df.columns, pd.MultiIndex):
        levels = df.columns.get_level_values(0)
        if ticker in df.columns.get_level_values(-1):
            df = df.xs(ticker, axis=1, level=-1)
        else:
            df.columns = levels

    df.columns = [str(c).lower().replace(" ", "_") for c in df.columns]

    missing = [c for c in OHLCV_COLUMNS if c not in df.columns]
    if missing:
        raise PriceDataError(
            f"{ticker}: price data missing required columns {missing} "
            f"(got {list(df.columns)})"
        )

    df = df[OHLCV_COLUMNS]

    # Index must be tz-naive dates for stable parquet round-tripping
    df.index = pd.to_datetime(df.index, errors="coerce")
    if getattr(df.index, "tz", None) is not None:
        df.index = df.index.tz_localize(None)
    df.index.name = "date"

    df = df[~df.index.isna()]
    df = df[~df.index.duplicated(keep="last")].sort_index()

    # A zero or negative price is bad data, not a market event; log
    # returns are undefined there.
    df = df[df["close"] > 0]
    df = df.dropna(subset=["open", "high", "low", "close"])

    if df.empty:
        raise PriceDataError(f"{ticker}: no usable rows after cleaning")

    return df


def download_history(
    ticker: str,
    period: str = HISTORY_PERIOD,
    max_retries: int = 3,
) -> pd.DataFrame:
    """
    Fetch history for one ticker directly from Yahoo, with retries.

    Prefer `load_history`, which consults the cache first.
    """
    # Imported lazily so that importing this module never requires network
    # libraries to initialise.
    import yfinance as yf

    last_error: Optional[Exception] = None

    for attempt in range(max_retries):
        try:
            raw = yf.Ticker(ticker).history(
                period=period,
                interval="1d",
                auto_adjust=True,
            )
            return _normalise(raw, ticker)
        except Exception as exc:  # noqa: BLE001 - yfinance raises broadly
            last_error = exc
            if attempt < max_retries - 1:
                backoff = 2 ** attempt
                logger.warning(
                    "Download failed for %s (attempt %d/%d): %s - retrying in %ds",
                    ticker, attempt + 1, max_retries, exc, backoff,
                )
                time.sleep(backoff)

    raise PriceDataError(
        f"Could not download {ticker} after {max_retries} attempts: {last_error}"
    )


def load_history(
    ticker: str,
    period: str = HISTORY_PERIOD,
    use_cache: bool = True,
    refresh: bool = False,
) -> pd.DataFrame:
    """
    Load daily OHLCV history for one ticker, preferring the disk cache.

    Args:
        ticker: Yahoo symbol, e.g. 'RELIANCE.NS' or '^NSEI'
        period: yfinance period string, e.g. '10y'
        use_cache: Read from and write to the parquet cache
        refresh: Ignore a fresh cache entry and re-download

    Returns:
        DataFrame indexed by date with columns open/high/low/close/volume

    Raises:
        PriceDataError: if no usable data can be obtained from either
            the network or a stale cache entry
    """
    path = _cache_path(ticker, period)

    if use_cache and not refresh and _is_fresh(path, CACHE_TTL_HOURS):
        try:
            return pd.read_parquet(path)
        except Exception as exc:  # noqa: BLE001 - corrupt cache is recoverable
            logger.warning("Cache read failed for %s (%s); re-downloading", ticker, exc)

    try:
        df = download_history(ticker, period=period)
    except PriceDataError:
        # Network unavailable or rate-limited. A stale cache entry beats
        # no data at all — volatility features are not sensitive to
        # being a few days behind.
        if use_cache and path.exists():
            logger.warning("Download failed for %s; serving stale cache", ticker)
            try:
                return pd.read_parquet(path)
            except Exception:  # noqa: BLE001
                pass
        raise

    if use_cache:
        try:
            CACHE_DIR.mkdir(parents=True, exist_ok=True)
            df.to_parquet(path)
        except Exception as exc:  # noqa: BLE001 - caching is best-effort
            logger.warning("Cache write failed for %s: %s", ticker, exc)

    return df


def load_many(
    tickers: List[str],
    period: str = HISTORY_PERIOD,
    use_cache: bool = True,
    refresh: bool = False,
    skip_failures: bool = True,
) -> Dict[str, pd.DataFrame]:
    """
    Load history for several tickers.

    Args:
        skip_failures: log and omit tickers that fail rather than aborting
            the whole batch. Useful when building a training set, where
            losing one name out of ten is acceptable.

    Returns:
        Mapping of ticker -> OHLCV DataFrame, for tickers that succeeded.
    """
    out: Dict[str, pd.DataFrame] = {}
    failed: List[str] = []

    for ticker in tickers:
        try:
            out[ticker] = load_history(
                ticker, period=period, use_cache=use_cache, refresh=refresh
            )
        except PriceDataError as exc:
            if not skip_failures:
                raise
            logger.error("Skipping %s: %s", ticker, exc)
            failed.append(ticker)

    if failed:
        logger.warning("%d/%d tickers failed: %s", len(failed), len(tickers), failed)

    if not out:
        raise PriceDataError(f"No price data could be loaded for any of {tickers}")

    return out


def cache_status() -> List[Dict]:
    """Describe what is currently cached. Useful for diagnostics."""
    if not CACHE_DIR.exists():
        return []

    rows = []
    for path in sorted(CACHE_DIR.glob("*.parquet")):
        stat = path.stat()
        rows.append({
            "file": path.name,
            "size_kb": round(stat.st_size / 1024, 1),
            "modified": datetime.fromtimestamp(stat.st_mtime, tz=timezone.utc).isoformat(),
            "fresh": _is_fresh(path, CACHE_TTL_HOURS),
        })
    return rows
