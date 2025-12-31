"""Metrics calculation and delta analysis."""

from typing import Dict, List, Any
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from sqlalchemy import func
from collections import Counter
import logging

from src.models import CoreEvent, CoreTopic, CoreEventTopic
from src.config import get_settings

settings = get_settings()
logger = logging.getLogger(__name__)


def compute_urgency_distribution(events: List[CoreEvent]) -> Dict[str, int]:
    """
    Compute urgency distribution across low/medium/high buckets.

    Args:
        events: List of events

    Returns:
        Dictionary with counts for low, medium, high
    """
    distribution = {"low": 0, "medium": 0, "high": 0}

    for event in events:
        if event.urgency_score <= settings.urgency_low_max:
            distribution["low"] += 1
        elif event.urgency_score <= settings.urgency_medium_max:
            distribution["medium"] += 1
        else:
            distribution["high"] += 1

    return distribution


def compute_actor_load(events: List[CoreEvent]) -> Dict[str, int]:
    """
    Count events per actor.

    Args:
        events: List of events

    Returns:
        Dictionary mapping actor to event count
    """
    actor_counts = Counter(event.actor for event in events)
    return dict(actor_counts.most_common())


def compute_decision_counts(events: List[CoreEvent]) -> Dict[str, int]:
    """
    Count decisions by type.

    Args:
        events: List of events

    Returns:
        Dictionary with counts for made, deferred, none
    """
    decision_counts = Counter(event.decision for event in events)
    return {
        "made": decision_counts.get("made", 0),
        "deferred": decision_counts.get("deferred", 0),
        "none": decision_counts.get("none", 0)
    }


def compute_repeated_patterns(events: List[CoreEvent]) -> List[Dict[str, Any]]:
    """
    Identify threads with ≥3 messages (repeated patterns).

    Args:
        events: List of events

    Returns:
        List of dictionaries with thread info
    """
    thread_counts = Counter(
        event.thread_id for event in events
        if event.thread_id is not None
    )

    repeated = [
        {
            "thread_id": thread_id,
            "count": count,
            "subjects": list(set(
                e.subject for e in events
                if e.thread_id == thread_id
            ))[:3]  # Sample subjects
        }
        for thread_id, count in thread_counts.items()
        if count >= 3
    ]

    return sorted(repeated, key=lambda x: x["count"], reverse=True)


def compute_metrics(events: List[CoreEvent]) -> Dict[str, Any]:
    """
    Compute all metrics for a set of events.

    Args:
        events: List of events

    Returns:
        Dictionary containing all computed metrics
    """
    return {
        "total_events": len(events),
        "urgency_distribution": compute_urgency_distribution(events),
        "actor_load": compute_actor_load(events),
        "decision_counts": compute_decision_counts(events),
        "follow_up_count": sum(1 for e in events if e.follow_up_required),
        "repeated_patterns": compute_repeated_patterns(events)
    }


def compute_deltas(week_metrics: Dict[str, Any], baseline_metrics: Dict[str, Any]) -> Dict[str, Any]:
    """
    Compute deltas between week and baseline metrics.

    Args:
        week_metrics: Current week metrics
        baseline_metrics: 28-day baseline metrics

    Returns:
        Dictionary containing delta calculations
    """
    deltas = {
        "total_events_delta": week_metrics["total_events"] - baseline_metrics["total_events"],
        "total_events_pct_change": (
            ((week_metrics["total_events"] - baseline_metrics["total_events"]) / baseline_metrics["total_events"] * 100)
            if baseline_metrics["total_events"] > 0 else 0.0
        ),
        "urgency_shifts": {
            "high_delta": week_metrics["urgency_distribution"]["high"] - baseline_metrics["urgency_distribution"]["high"],
            "medium_delta": week_metrics["urgency_distribution"]["medium"] - baseline_metrics["urgency_distribution"]["medium"],
            "low_delta": week_metrics["urgency_distribution"]["low"] - baseline_metrics["urgency_distribution"]["low"],
        },
        "decision_shifts": {
            "made_delta": week_metrics["decision_counts"]["made"] - baseline_metrics["decision_counts"]["made"],
            "deferred_delta": week_metrics["decision_counts"]["deferred"] - baseline_metrics["decision_counts"]["deferred"],
        },
        "follow_up_delta": week_metrics["follow_up_count"] - baseline_metrics["follow_up_count"],
    }

    # Compute top movers in actor load
    week_actors = week_metrics["actor_load"]
    baseline_actors = baseline_metrics["actor_load"]

    actor_deltas = {}
    for actor in set(list(week_actors.keys()) + list(baseline_actors.keys())):
        week_count = week_actors.get(actor, 0)
        baseline_count = baseline_actors.get(actor, 0)
        actor_deltas[actor] = week_count - baseline_count

    top_movers = sorted(actor_deltas.items(), key=lambda x: abs(x[1]), reverse=True)[:5]
    deltas["top_actor_movers"] = [
        {"actor": actor, "delta": delta} for actor, delta in top_movers
    ]

    return deltas


def get_topic_metrics(db: Session, week_events: List[CoreEvent]) -> List[Dict[str, Any]]:
    """
    Get metrics for each topic detected this week.

    Args:
        db: Database session
        week_events: Events from current week

    Returns:
        List of topic metrics dictionaries
    """
    week_event_ids = {e.id for e in week_events}

    # Get all topic mappings for week events
    topic_data = db.query(
        CoreEventTopic.topic_id,
        func.count(CoreEventTopic.event_id).label('event_count')
    ).filter(
        CoreEventTopic.event_id.in_(week_event_ids)
    ).group_by(
        CoreEventTopic.topic_id
    ).all()

    topic_metrics = []

    for topic_id, event_count in topic_data:
        # Get topic info
        topic = db.query(CoreTopic).filter(CoreTopic.topic_id == topic_id).first()

        # Get events for this topic
        topic_event_ids = db.query(CoreEventTopic.event_id).filter(
            CoreEventTopic.topic_id == topic_id,
            CoreEventTopic.event_id.in_(week_event_ids)
        ).all()
        topic_event_ids = [eid[0] for eid in topic_event_ids]

        topic_events = [e for e in week_events if e.id in topic_event_ids]

        # Calculate topic-specific metrics
        avg_urgency = sum(e.urgency_score for e in topic_events) / len(topic_events)
        decision_counts = compute_decision_counts(topic_events)

        topic_metrics.append({
            "topic_id": str(topic_id),
            "event_count": event_count,
            "avg_urgency": round(avg_urgency, 2),
            "decisions_made": decision_counts["made"],
            "decisions_deferred": decision_counts["deferred"],
            "follow_up_required": sum(1 for e in topic_events if e.follow_up_required),
            "sample_subjects": list(set(e.subject for e in topic_events))[:3],
            "created_at": topic.created_at.isoformat(),
            "is_new": (datetime.utcnow() - topic.created_at) < timedelta(days=7)
        })

    return sorted(topic_metrics, key=lambda x: x["event_count"], reverse=True)
