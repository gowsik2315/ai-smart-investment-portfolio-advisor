"""
Tests for the Stock Predictor's AI explanation.

Two things are pinned down:

1. The PROMPT. A small local model will happily call a historical
   frequency "a prediction", say a stock "will" rise, or slip into buy/sell
   advice. The rules in the prompt are the only guard, so which rules apply
   in which situation is tested as strictly as any calculation.

2. The ENDPOINT's behaviour around the LLM: it must degrade quietly when
   Ollama is down, cache only successes, and never serve an explanation
   that belongs to different numbers.

Ollama is stubbed throughout; no test touches the network.
"""

import pytest
from fastapi import HTTPException

import app.api.market as market
from app.ml.data import InvalidTickerError, PriceDataError
from app.ml.features import FEATURE_NAMES
from app.ml.trend_registry import TrendModelArtifact
from app.services.explanation_guard import BASE_RATE_CAVEAT, apply_outlook_guard
from app.services.ml_prediction_service import SOURCE_HISTORICAL, VolatilityForecast
from app.services.ollama_prompts import OllamaPrompts
from app.services.stock_trend_service import StockTrendService
from tests.conftest import make_ohlcv


GOOD_TEXT = "The data shows a 49.5% chance of closing higher. This is not a prediction."


class FixedProbModel:
    """Classifier that always answers with the same probability of a rise."""
    classes_ = [0, 1]

    def __init__(self, p_up):
        import numpy as np
        self._row = np.array([[1 - p_up, p_up]])

    def predict_proba(self, X):
        return self._row


def build_outlook(ticker="TEST.NS", model_p=None, metrics=None):
    """Build a real outlook dict offline, with or without a trained model."""
    service = StockTrendService()
    service._load_attempted = True
    service._artifact = (
        TrendModelArtifact(
            model=FixedProbModel(model_p), feature_names=FEATURE_NAMES,
            model_version="stub-v1", metrics=metrics or {},
        ) if model_p is not None else None
    )
    service._load_error = None if model_p is not None else "No artifact"

    vol = VolatilityForecast(
        ticker=ticker, volatility=0.25, source=SOURCE_HISTORICAL,
        historical_volatility=0.25, fallback_reason="no volatility model",
    )
    return service.outlook_from_history(
        ticker, make_ohlcv(n_days=900), make_ohlcv(n_days=900, seed=99), vol)


# ── The prompt ───────────────────────────────────────────────────────

class TestPromptRules:

    def test_base_rate_is_described_as_not_a_prediction(self):
        prompt = OllamaPrompts.stock_outlook_explanation(build_outlook())
        assert "NOT a prediction" in prompt
        assert "NOT a model" in prompt
        assert "do not describe it as a forecast" in prompt

    def test_model_prompt_does_not_claim_it_is_not_a_prediction(self):
        prompt = OllamaPrompts.stock_outlook_explanation(
            build_outlook(model_p=0.6, metrics={"brier_skill_score": 0.02}))
        assert "a trained model (stub-v1)" in prompt
        assert "NOT a prediction" not in prompt

    def test_model_prompt_asks_for_comparison_with_the_base_rate(self):
        prompt = OllamaPrompts.stock_outlook_explanation(
            build_outlook(model_p=0.6, metrics={"brier_skill_score": 0.02}))
        assert "less than 3 percentage points" in prompt
        assert "no meaningful edge" in prompt

    def test_a_model_that_failed_to_beat_history_must_be_called_out(self):
        prompt = OllamaPrompts.stock_outlook_explanation(
            build_outlook(model_p=0.6, metrics={"brier_skill_score": -0.001}))
        assert "did NOT beat the historical frequency" in prompt

    def test_a_model_that_beat_history_is_not_accused_of_failing(self):
        prompt = OllamaPrompts.stock_outlook_explanation(
            build_outlook(model_p=0.6, metrics={"brier_skill_score": 0.03}))
        assert "did NOT beat" not in prompt

    @pytest.mark.parametrize("model_p", [None, 0.55])
    def test_advice_and_certainty_are_always_forbidden(self, model_p):
        prompt = OllamaPrompts.stock_outlook_explanation(build_outlook(model_p=model_p))
        assert 'Never say the stock "will" rise or fall' in prompt
        assert "Never tell the reader to buy, sell or hold" in prompt

    def test_range_is_framed_as_carrying_no_direction(self):
        prompt = OllamaPrompts.stock_outlook_explanation(build_outlook())
        assert "says nothing about which direction" in prompt

    def test_probability_sentence_is_given_verbatim_for_the_model_to_copy(self):
        outlook = build_outlook()
        prompt = OllamaPrompts.stock_outlook_explanation(outlook)
        assert (f"The data shows a {outlook['probability_up'] * 100:.1f}% chance of closing "
                f"higher in 21 trading days, compared with {outlook['base_rate_up'] * 100:.1f}% historically.") in prompt
        assert 'never "will close higher"' in prompt

    def test_trend_is_framed_as_describing_the_past(self):
        prompt = OllamaPrompts.stock_outlook_explanation(build_outlook())
        assert "describes the past, not a forecast" in prompt


class TestPromptFacts:

    def test_the_numbers_come_from_the_outlook(self):
        outlook = build_outlook()
        prompt = OllamaPrompts.stock_outlook_explanation(outlook)
        end = outlook["expected_range"][-1]

        assert outlook["ticker"] in prompt
        assert f"{outlook['probability_up'] * 100:.1f}%" in prompt
        assert f"{outlook['base_rate_up'] * 100:.1f}%" in prompt
        assert f"{end['lower_68']:,.2f}" in prompt
        assert f"{end['upper_95']:,.2f}" in prompt
        assert outlook["as_of"] in prompt

    def test_the_difference_from_the_base_rate_is_computed_for_the_model(self):
        outlook = build_outlook(model_p=0.70)
        expected = (0.70 - outlook["base_rate_up"]) * 100
        assert f"difference {expected:+.1f} percentage points" in \
            OllamaPrompts.stock_outlook_explanation(outlook)

    def test_currency_follows_the_exchange(self):
        assert "₹" in OllamaPrompts.stock_outlook_explanation(build_outlook("TCS.NS"))
        us = OllamaPrompts.stock_outlook_explanation(build_outlook("AAPL"))
        assert "$" in us and "₹" not in us

    def test_volatility_source_is_stated_honestly(self):
        prompt = OllamaPrompts.stock_outlook_explanation(build_outlook())
        assert "not a forecast" in prompt


# ── The endpoint ─────────────────────────────────────────────────────

@pytest.fixture(autouse=True)
def clean_cache():
    market._outlook_explain_cache.clear()
    yield
    market._outlook_explain_cache.clear()


@pytest.fixture
def stubbed(monkeypatch):
    """Stub the outlook and Ollama; record how many times Ollama is asked."""
    state = {"outlook": build_outlook(), "calls": 0, "result": {"success": True, "explanation": GOOD_TEXT}}

    monkeypatch.setattr(market.stock_trend_service, "get_outlook", lambda t: state["outlook"])

    async def fake_generate(**kwargs):
        state["calls"] += 1
        state["last_kwargs"] = kwargs
        return state["result"]

    monkeypatch.setattr(market.ollama_service, "generate_explanation", fake_generate)
    return state


class TestExplainEndpoint:

    @pytest.mark.asyncio
    async def test_returns_the_explanation_with_provenance(self, stubbed):
        out = await market.explain_stock_outlook("TEST.NS", current_user_id=1)

        assert out.ai_available is True
        assert out.ai_explanation == GOOD_TEXT
        assert out.cached is False
        assert out.probability_source == "historical_base_rate"
        assert out.disclaimer

    @pytest.mark.asyncio
    async def test_prompt_and_low_temperature_reach_ollama(self, stubbed):
        await market.explain_stock_outlook("TEST.NS", current_user_id=1)

        kwargs = stubbed["last_kwargs"]
        assert "NOT a prediction" in kwargs["prompt"]
        assert kwargs["temperature"] <= 0.4

    @pytest.mark.asyncio
    async def test_second_request_is_served_from_cache(self, stubbed):
        await market.explain_stock_outlook("TEST.NS", current_user_id=1)
        again = await market.explain_stock_outlook("TEST.NS", current_user_id=1)

        assert stubbed["calls"] == 1
        assert again.cached is True
        assert again.ai_explanation == GOOD_TEXT

    @pytest.mark.asyncio
    async def test_a_failure_is_reported_and_never_cached(self, stubbed):
        stubbed["result"] = {"success": False, "explanation": "Unable to generate AI explanation at this time."}

        first = await market.explain_stock_outlook("TEST.NS", current_user_id=1)
        await market.explain_stock_outlook("TEST.NS", current_user_id=1)

        assert first.ai_available is False
        assert stubbed["calls"] == 2   # a failure must be retried, not remembered

    @pytest.mark.asyncio
    async def test_changed_numbers_never_get_a_stale_explanation(self, stubbed):
        await market.explain_stock_outlook("TEST.NS", current_user_id=1)

        stubbed["outlook"] = build_outlook(model_p=0.7, metrics={"brier_skill_score": 0.02})
        fresh = await market.explain_stock_outlook("TEST.NS", current_user_id=1)

        assert stubbed["calls"] == 2
        assert fresh.cached is False
        assert fresh.probability_source == "ml_predicted"

    @pytest.mark.asyncio
    async def test_cache_is_bounded(self, stubbed, monkeypatch):
        monkeypatch.setattr(market, "_OUTLOOK_EXPLAIN_MAX_ENTRIES", 3)
        for i in range(6):
            stubbed["outlook"] = dict(build_outlook(), ticker=f"T{i}.NS")
            await market.explain_stock_outlook(f"T{i}.NS", current_user_id=1)

        assert len(market._outlook_explain_cache) <= 3

    @pytest.mark.asyncio
    @pytest.mark.parametrize("error, code", [
        (InvalidTickerError("bad symbol"), 422),
        (PriceDataError("no data"), 503),
        (ValueError("too short"), 400),
    ])
    async def test_input_and_data_errors_map_to_http_statuses(self, monkeypatch, error, code):
        def boom(ticker):
            raise error
        monkeypatch.setattr(market.stock_trend_service, "get_outlook", boom)

        with pytest.raises(HTTPException) as exc:
            await market.explain_stock_outlook("X", current_user_id=1)
        assert exc.value.status_code == code


# ── The guard ────────────────────────────────────────────────────────

BASE = {"probability_source": "historical_base_rate"}
MODEL = {"probability_source": "ml_predicted"}


class TestGuardRejects:

    @pytest.mark.parametrize("text", [
        "You should buy this stock now.",
        "I recommend holding on to it.",
        "This is a good time to buy.",
        "Consider selling before the drop.",
        "Sell now and avoid losses.",
        "A guaranteed gain over the month.",
        "It is a risk-free opportunity.",
    ])
    def test_advice_and_guarantees_are_rejected(self, text):
        safe, reason = apply_outlook_guard(text + " This is not a prediction.", BASE)
        assert safe is None and reason

    @pytest.mark.parametrize("text", [
        "The stock will rise next month.",
        "The price will definitely fall.",
        "Shares will surge after earnings.",
        "It will crash in the coming weeks.",
    ])
    def test_price_moves_stated_as_certain_are_rejected(self, text):
        safe, reason = apply_outlook_guard(text, BASE)
        assert safe is None and "certain" in reason

    def test_empty_text_is_rejected(self):
        assert apply_outlook_guard("   ", BASE)[0] is None


class TestGuardAccepts:

    @pytest.mark.parametrize("text", [
        "This analysis does not guarantee future performance.",
        "There is no guarantee the stock will follow its past.",
        "Past results offer no guarantees.",
        "The range is not risk-free information, and it can be wrong.",
        "Nothing here is guaranteed to hold; it can't guarantee a result.",
        "There is a 49.5% chance of closing higher in 21 trading days.",
        "The stock has a probability that it will close higher, matching its history.",
        "The threshold for a bullish signal is the 50-day average.",
        "Buyers and sellers were active; volume is above its average.",
    ])
    def test_ordinary_probability_language_is_not_a_false_positive(self, text):
        safe, reason = apply_outlook_guard(text + " It is not a prediction.", BASE)
        assert reason is None and safe is not None


class TestBaseRateCaveat:

    def test_missing_caveat_is_appended_for_the_base_rate(self):
        safe, _ = apply_outlook_guard("The trend is bearish and the range is wide.", BASE)
        assert safe.endswith(BASE_RATE_CAVEAT)

    @pytest.mark.parametrize("phrase", [
        "This is not a prediction.", "It is not a forecast.",
        "No model is loaded.", "That isn't a prediction.",
    ])
    def test_existing_caveat_is_not_duplicated(self, phrase):
        safe, _ = apply_outlook_guard(f"The trend is bearish. {phrase}", BASE)
        assert BASE_RATE_CAVEAT not in safe

    def test_a_model_probability_gets_no_base_rate_caveat(self):
        safe, _ = apply_outlook_guard("The model sees a 60% chance of closing higher.", MODEL)
        assert BASE_RATE_CAVEAT not in safe

    def test_accepted_text_is_otherwise_untouched(self):
        safe, _ = apply_outlook_guard("  A fine explanation. Not a prediction.  ", BASE)
        assert safe == "A fine explanation. Not a prediction."


class TestEndpointWithTheGuard:

    @pytest.mark.asyncio
    async def test_missing_caveat_is_appended_before_the_user_sees_it(self, stubbed):
        stubbed["result"] = {"success": True, "explanation": "The trend is bearish."}
        out = await market.explain_stock_outlook("TEST.NS", current_user_id=1)

        assert out.ai_available is True
        assert out.ai_explanation.endswith(BASE_RATE_CAVEAT)

    @pytest.mark.asyncio
    async def test_advice_is_discarded_and_not_cached(self, stubbed):
        stubbed["result"] = {"success": True, "explanation": "You should buy this stock now."}

        first = await market.explain_stock_outlook("TEST.NS", current_user_id=1)
        await market.explain_stock_outlook("TEST.NS", current_user_id=1)

        assert first.ai_available is False
        assert "discarded" in first.ai_explanation
        assert "buy" not in first.ai_explanation
        assert stubbed["calls"] == 2          # rejected text must never be remembered
        assert market._outlook_explain_cache == {}
