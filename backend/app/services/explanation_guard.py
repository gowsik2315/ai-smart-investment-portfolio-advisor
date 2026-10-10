"""
Output guard for the Stock Predictor's AI explanation.

The prompt tells the model what it may not say, but a small local model
follows instructions loosely, and in a finance context "loosely" is not
good enough. This module checks what actually came back, deterministically,
so the two promises the page makes do not depend on the model complying:

  1. The explanation never gives buy/sell/hold advice or states a price
     move as certain.
  2. When the probability is only the historical base rate, the text says
     in plain words that it is not a prediction. If the model forgot, the
     sentence is appended.

A rejected explanation is discarded, never edited: rewriting model prose to
dodge a rule would put words in its mouth that nobody reviewed.
"""

from __future__ import annotations

import re
from typing import Dict, Optional, Tuple

# Direct advice, or a guarantee. Deliberately specific: single words like
# "buy" or "hold" also occur in harmless sentences ("threshold", "buyers").
_ADVICE = re.compile(
    r"\b("
    r"you should (?:buy|sell|hold|invest|avoid|wait)"
    r"|i (?:would )?(?:strongly )?recommend"
    r"|we (?:would )?(?:strongly )?recommend"
    r"|(?:good|great|bad|right|wrong|best) time to (?:buy|sell|invest)"
    r"|consider (?:buying|selling|holding)"
    r"|(?:buy|sell|hold) (?:this|the|these|that) (?:stock|share|shares)"
    r"|(?:buy|sell) now"
    r"|guarantee[ds]?"
    r"|risk[- ]free"
    r")\b",
    re.IGNORECASE,
)

# "no guarantee", "does not guarantee", "not risk-free": the assurance is
# being denied, which is exactly what a careful explanation should say.
_NEGATED_ASSURANCE = re.compile(
    r"(?:\b(?:not|never|no|without|nothing)\b|n['’]t)\s+(?:\w+\s+){0,2}(?:guarantee[ds]?|risk[- ]free)\b",
    re.IGNORECASE,
)

# A price move stated as certain. "will close higher" is NOT matched: that
# phrase appears legitimately when a probability is being described.
_CERTAINTY = re.compile(
    r"\b(?:stock|shares?|price|it)\s+(?:will|is going to|is certain to)\s+"
    r"(?:definitely\s+|certainly\s+|surely\s+)?"
    r"(?:rise|fall|go up|go down|increase|decrease|drop|gain|lose|rally|crash|surge|climb)\b",
    re.IGNORECASE,
)

# Any of these counts as saying the probability is not a forecast
_NOT_A_PREDICTION = re.compile(
    r"\bnot (?:a |an )?(?:prediction|forecast|predicting)\b"
    r"|\bno (?:trained )?model\b"
    r"|\bisn['’]t a (?:prediction|forecast)\b"
    r"|\bis not a (?:prediction|forecast)\b",
    re.IGNORECASE,
)

BASE_RATE_CAVEAT = (
    "Note: this probability is only how often this stock rose over "
    "21 trading days in the past. It is not a prediction."
)


def apply_outlook_guard(text: str, outlook: Dict) -> Tuple[Optional[str], Optional[str]]:
    """
    Check an explanation against the rules.

    Returns:
        (safe_text, None) when acceptable, with the base-rate caveat
        appended if it was missing; or (None, reason) when the text must
        be discarded.
    """
    cleaned = (text or "").strip()
    if not cleaned:
        return None, "empty explanation"

    # "does not guarantee future performance" is the standard, desirable
    # disclaimer, so a guarantee that is being DENIED must not be flagged.
    asserted = _NEGATED_ASSURANCE.sub("", cleaned)

    advice = _ADVICE.search(asserted)
    if advice:
        return None, f"contains advice or a guarantee ('{advice.group(0)}')"

    certain = _CERTAINTY.search(cleaned)
    if certain:
        return None, f"states a price move as certain ('{certain.group(0)}')"

    if outlook.get("probability_source") != "ml_predicted" and not _NOT_A_PREDICTION.search(cleaned):
        cleaned = f"{cleaned}\n\n{BASE_RATE_CAVEAT}"

    return cleaned, None
