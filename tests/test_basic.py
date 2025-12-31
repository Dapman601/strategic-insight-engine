"""Basic test suite for the Strategic Insight Engine."""

import pytest
from datetime import datetime
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.schemas import CanonicalEvent
from src.insight.modules.embeddings import generate_embedding, cosine_similarity
from src.insight.modules.metrics import compute_urgency_distribution, compute_actor_load


def test_canonical_event_validation():
    """Test canonical event schema validation."""
    # Valid event
    event_data = {
        "id": "test:123",
        "source": "email",
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "actor": "test@example.com",
        "direction": "inbound",
        "subject": "Test Subject",
        "text": "Test body text",
        "thread_id": None,
        "decision": "none",
        "action_owner": None,
        "follow_up_required": False,
        "urgency_score": 5,
        "sentiment": "unknown",
        "raw_ref": "ref123"
    }

    event = CanonicalEvent(**event_data)
    assert event.id == "test:123"
    assert event.urgency_score == 5

    # Invalid urgency score
    with pytest.raises(Exception):
        invalid_data = event_data.copy()
        invalid_data["urgency_score"] = 15
        CanonicalEvent(**invalid_data)


def test_embedding_generation():
    """Test embedding generation."""
    text = "This is a test message"
    embedding = generate_embedding(text)

    assert embedding is not None
    assert len(embedding) == 384  # all-MiniLM-L6-v2 dimension


def test_cosine_similarity():
    """Test cosine similarity calculation."""
    text1 = "Machine learning is fascinating"
    text2 = "AI and ML are interesting"
    text3 = "The weather is nice today"

    emb1 = generate_embedding(text1)
    emb2 = generate_embedding(text2)
    emb3 = generate_embedding(text3)

    # Similar texts should have higher similarity
    sim_similar = cosine_similarity(emb1, emb2)
    sim_different = cosine_similarity(emb1, emb3)

    assert sim_similar > sim_different
    assert 0 <= sim_similar <= 1
    assert 0 <= sim_different <= 1


def test_urgency_distribution():
    """Test urgency distribution calculation."""
    from src.models import CoreEvent

    events = [
        CoreEvent(
            id=f"test:{i}",
            source="email",
            timestamp=datetime.utcnow(),
            actor="test@example.com",
            direction="inbound",
            subject="Test",
            text="Test",
            decision="none",
            follow_up_required=False,
            urgency_score=score,
            raw_ref=f"ref{i}"
        )
        for i, score in enumerate([1, 3, 5, 7, 9, 2, 8, 4, 6, 10])
    ]

    distribution = compute_urgency_distribution(events)

    assert "low" in distribution
    assert "medium" in distribution
    assert "high" in distribution
    assert distribution["low"] == 2  # scores 1, 2, 3
    assert distribution["medium"] == 5  # scores 4, 5, 6, 7
    assert distribution["high"] == 3  # scores 8, 9, 10


def test_actor_load():
    """Test actor load calculation."""
    from src.models import CoreEvent

    events = [
        CoreEvent(
            id=f"test:{i}",
            source="email",
            timestamp=datetime.utcnow(),
            actor=actor,
            direction="inbound",
            subject="Test",
            text="Test",
            decision="none",
            follow_up_required=False,
            urgency_score=5,
            raw_ref=f"ref{i}"
        )
        for i, actor in enumerate(["alice@example.com"] * 5 + ["bob@example.com"] * 3 + ["charlie@example.com"] * 2)
    ]

    actor_load = compute_actor_load(events)

    assert actor_load["alice@example.com"] == 5
    assert actor_load["bob@example.com"] == 3
    assert actor_load["charlie@example.com"] == 2


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
