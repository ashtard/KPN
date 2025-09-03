from __future__ import annotations

from fastapi.testclient import TestClient
from app.main import app
import pytest

client = TestClient(app)


@pytest.mark.parametrize(
    "text,expected",
    [
        ("Great service, thank you!", "positive"),
        ("This is terrible and I am unhappy", "negative"),
    ],
)
def test_sentiment(text: str, expected: str) -> None:
    """
    The endpoint should always return a normalized sentiment label and a score in [0,1].
    With the heuristic fallback, the labels should match the obvious polarity.
    With Transformers enabled, the pipeline returns POSITIVE/NEGATIVE which we normalize.
    """
    r = client.post("/ai/sentiment", json={"text": text})
    assert r.status_code == 200, r.text
    data = r.json()
    assert data["sentiment"] in {"positive", "neutral", "negative"}
    assert 0.0 <= data["score"] <= 1.0
    # For these two cases, both heuristic and HF model should match the polarity:
    assert data["sentiment"] == expected


def test_subject_line_generation() -> None:
    """
    The subject generator should produce a short, non-empty subject (<= 70 chars).
    """
    body = "Customer is interested in premium plan; follow up next Tuesday."
    r = client.post("/ai/subject", json={"body": body})
    assert r.status_code == 200, r.text
    data = r.json()
    assert isinstance(data["subject"], str)
    assert 0 < len(data["subject"]) <= 70
