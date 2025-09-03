from __future__ import annotations
from functools import lru_cache
from typing import Literal
from fastapi import APIRouter
from pydantic import BaseModel, Field
from app.util.settings import settings

router = APIRouter(prefix="/ai", tags=["ai"])


class Feedback(BaseModel):
    text: str = Field(..., min_length=1, description="Short feedback or note text")


class SentimentResult(BaseModel):
    sentiment: Literal["positive", "neutral", "negative"]
    score: float


class EmailBody(BaseModel):
    body: str = Field(..., min_length=1, description="Draft email body or note")


class SubjectSuggestion(BaseModel):
    subject: str


 #Heuristic (fallback)
_POSITIVE = {"good", "great", "happy", "love", "excellent", "positive", "satisfied", "thanks", "thank you"}
_NEGATIVE = {"bad", "angry", "hate", "terrible", "awful", "negative", "unhappy", "frustrated", "complaint"}

def _simple_sentiment(text: str) -> tuple[str, float]:
    t = text.lower()
    pos_hits = sum(1 for w in _POSITIVE if w in t)
    neg_hits = sum(1 for w in _NEGATIVE if w in t)
    if pos_hits > neg_hits:
        return "positive", 0.9
    if neg_hits > pos_hits:
        return "negative", 0.9
    return "neutral", 0.5


# Optional Transformers loader
@lru_cache(maxsize=1)
def _get_sentiment_pipeline_or_none():
    """Return a HF pipeline or None if unavailable/misconfigured or disabled."""
    if not settings.AI_USE_TRANSFORMERS:
        return None
    try:
        from transformers import pipeline
        return pipeline("sentiment-analysis", device=-1)  # CPU
    except Exception:
        return None


def _normalize(label: str, score: float) -> tuple[str, float]:
    lab = label.strip().lower()
    if lab.startswith("pos"):
        return "positive", float(score)
    if lab.startswith("neg"):
        return "negative", float(score)
    return "neutral", float(score)


# Subject helper
def _compress_to_subject(body: str) -> str:
    """
    Very small heuristic compressor:
    - take first sentence or ~8 words
    - strip trailing punctuation
    - capitalize mildly
    - ensure ≤ 70 chars
    """
    raw = body.strip().replace("\n", " ")
    first = raw.split(".")[0] if "." in raw else " ".join(raw.split()[:8])
    candidate = first.strip(" .!?:;").capitalize()
    if len(candidate) > 70:
        candidate = candidate[:67].rstrip() + "..."
    return candidate or "Customer update"


# Endpoints
@router.post("/sentiment", response_model=SentimentResult)
def analyze_sentiment(payload: Feedback):
    clf = _get_sentiment_pipeline_or_none()
    if clf is None:
        s, sc = _simple_sentiment(payload.text)
        return SentimentResult(sentiment=s, score=sc)
    raw = clf(payload.text)[0]
    s, sc = _normalize(raw["label"], raw["score"])
    return SentimentResult(sentiment=s, score=sc)


@router.post("/subject", response_model=SubjectSuggestion)
def suggest_subject(payload: EmailBody):
    return SubjectSuggestion(subject=_compress_to_subject(payload.body))
