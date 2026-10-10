"""
Tests for ticker validation in the price-history loader.

The ticker becomes part of a cache filename. The original sanitiser
replaced '/' and '.' but not '\\' or ':', and on Windows joining a path
with a segment such as 'C:\\Users\\x' produces an absolute path outside
the cache directory, so a crafted ticker could write a parquet file
anywhere the process could write. These tests keep that closed.
"""

import pydantic
import pytest

from app.ml.config import CACHE_DIR
from app.ml.data import InvalidTickerError, PriceDataError, _cache_path, validate_ticker
from app.schemas.ml_prediction import VolatilityPredictionRequest


class TestValidateTicker:

    @pytest.mark.parametrize("raw, expected", [
        ("RELIANCE.NS", "RELIANCE.NS"),
        ("  tcs.ns  ", "TCS.NS"),
        ("M&M.NS", "M&M.NS"),
        ("BAJAJ-AUTO.NS", "BAJAJ-AUTO.NS"),
        ("^NSEI", "^NSEI"),
        ("GC=F", "GC=F"),
        ("AAPL", "AAPL"),
    ])
    def test_real_symbols_are_accepted_and_normalised(self, raw, expected):
        assert validate_ticker(raw) == expected

    @pytest.mark.parametrize("raw", [
        "",
        "   ",
        "C:\\Users\\victim\\x",
        "C:\\Windows\\System32\\evil",
        "..\\..\\escape",
        "../etc/passwd",
        "a/b",
        "a\\b",
        "AB CD",
        "X\x00Y",
        "A" * 33,
        "-LEADING",
        ".LEADING",
    ])
    def test_unsafe_or_malformed_symbols_are_rejected(self, raw):
        with pytest.raises(InvalidTickerError):
            validate_ticker(raw)

    def test_invalid_ticker_is_a_price_data_error(self):
        """So existing callers that catch PriceDataError stay safe."""
        assert issubclass(InvalidTickerError, PriceDataError)


class TestCachePath:

    def test_valid_ticker_stays_inside_the_cache_directory(self):
        path = _cache_path("RELIANCE.NS", "3y")
        assert path.parent == CACHE_DIR
        assert path.name == "RELIANCE_NS__3y.parquet"

    def test_existing_cache_filenames_are_unchanged(self):
        """Renaming would orphan the cache already on disk."""
        assert _cache_path("^NSEI", "10y").name == "INDEX_NSEI__10y.parquet"

    @pytest.mark.parametrize("hostile", ["C:\\Windows\\evil", "..\\..\\x", "a/../../b"])
    def test_hostile_ticker_never_produces_a_path(self, hostile):
        with pytest.raises(InvalidTickerError):
            _cache_path(hostile, "3y")


class TestRequestSchema:

    def test_valid_request_is_normalised(self):
        assert VolatilityPredictionRequest(ticker=" infy.ns ").ticker == "INFY.NS"

    def test_hostile_ticker_is_a_validation_error_not_a_server_error(self):
        with pytest.raises(pydantic.ValidationError):
            VolatilityPredictionRequest(ticker="C:\\Windows\\evil")
