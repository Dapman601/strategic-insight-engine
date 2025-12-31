"""Hard-coded rule engine for identifying findings."""

from typing import List, Dict, Any
from src.config import get_settings

settings = get_settings()


class Finding:
    """Represents a finding identified by the rule engine."""

    def __init__(
        self,
        finding_type: str,
        severity: str,
        description: str,
        evidence: List[str],
        topic_id: str | None = None
    ):
        self.finding_type = finding_type
        self.severity = severity
        self.description = description
        self.evidence = evidence
        self.topic_id = topic_id

    def to_dict(self) -> Dict[str, Any]:
        return {
            "type": self.finding_type,
            "severity": self.severity,
            "description": self.description,
            "evidence": self.evidence,
            "topic_id": self.topic_id
        }


def rule_emerging_risk(
    topic_metrics: List[Dict[str, Any]],
    deltas: Dict[str, Any]
) -> List[Finding]:
    """
    Rule: Emerging Risk
    Trigger: Topic frequency ↑ + urgency ↑ + no decisions made

    Args:
        topic_metrics: List of topic metrics
        deltas: Delta calculations

    Returns:
        List of findings
    """
    findings = []

    for topic in topic_metrics:
        # Check if topic has high urgency, multiple events, and no decisions
        if (
            topic["event_count"] >= 3 and
            topic["avg_urgency"] >= settings.urgency_medium_max and
            topic["decisions_made"] == 0 and
            topic["is_new"]
        ):
            findings.append(Finding(
                finding_type="emerging_risk",
                severity="high",
                description=f"New high-urgency topic with {topic['event_count']} events but no decisions made",
                evidence=topic["sample_subjects"],
                topic_id=topic["topic_id"]
            ))

    return findings


def rule_avoided_decision(topic_metrics: List[Dict[str, Any]]) -> List[Finding]:
    """
    Rule: Avoided Decision
    Trigger: Deferred decisions ≥3 in topic

    Args:
        topic_metrics: List of topic metrics

    Returns:
        List of findings
    """
    findings = []

    for topic in topic_metrics:
        if topic["decisions_deferred"] >= 3:
            findings.append(Finding(
                finding_type="avoided_decision",
                severity="medium",
                description=f"Topic has {topic['decisions_deferred']} deferred decisions",
                evidence=topic["sample_subjects"],
                topic_id=topic["topic_id"]
            ))

    return findings


def rule_attention_sink(
    week_metrics: Dict[str, Any],
    deltas: Dict[str, Any]
) -> List[Finding]:
    """
    Rule: Attention Sink
    Trigger: Single actor >30% of inbound events

    Args:
        week_metrics: Current week metrics
        deltas: Delta calculations

    Returns:
        List of findings
    """
    findings = []

    total_events = week_metrics["total_events"]
    if total_events == 0:
        return findings

    threshold = 0.30
    actor_load = week_metrics["actor_load"]

    for actor, count in actor_load.items():
        percentage = count / total_events

        if percentage > threshold:
            findings.append(Finding(
                finding_type="attention_sink",
                severity="medium",
                description=f"{actor} represents {percentage*100:.1f}% of all events ({count}/{total_events})",
                evidence=[
                    f"Total events from {actor}: {count}",
                    f"Percentage: {percentage*100:.1f}%"
                ]
            ))

    return findings


def rule_scope_creep(
    week_metrics: Dict[str, Any],
    topic_metrics: List[Dict[str, Any]]
) -> List[Finding]:
    """
    Rule: Scope Creep
    Trigger: Repeated thread (≥3 messages) with no action owner

    Args:
        week_metrics: Current week metrics
        topic_metrics: List of topic metrics

    Returns:
        List of findings
    """
    findings = []

    repeated_patterns = week_metrics["repeated_patterns"]

    for pattern in repeated_patterns:
        if pattern["count"] >= 3:
            findings.append(Finding(
                finding_type="scope_creep",
                severity="low",
                description=f"Thread '{pattern['thread_id']}' has {pattern['count']} messages, potential scope creep",
                evidence=pattern["subjects"]
            ))

    return findings


def rule_decision_pressure(
    topic_metrics: List[Dict[str, Any]],
    deltas: Dict[str, Any]
) -> List[Finding]:
    """
    Rule: Decision Pressure
    Trigger: High follow-up requirement + deferred decisions

    Args:
        topic_metrics: List of topic metrics
        deltas: Delta calculations

    Returns:
        List of findings
    """
    findings = []

    for topic in topic_metrics:
        if (
            topic["follow_up_required"] >= 2 and
            topic["decisions_deferred"] >= 1 and
            topic["avg_urgency"] >= settings.urgency_low_max
        ):
            findings.append(Finding(
                finding_type="decision_pressure",
                severity="high",
                description=f"Topic requires {topic['follow_up_required']} follow-ups with {topic['decisions_deferred']} deferred decisions",
                evidence=topic["sample_subjects"],
                topic_id=topic["topic_id"]
            ))

    return findings


def apply_rules(
    week_metrics: Dict[str, Any],
    baseline_metrics: Dict[str, Any],
    deltas: Dict[str, Any],
    topic_metrics: List[Dict[str, Any]]
) -> List[Finding]:
    """
    Apply all hard-coded rules to identify findings.

    Args:
        week_metrics: Current week metrics
        baseline_metrics: 28-day baseline metrics
        deltas: Delta calculations
        topic_metrics: List of topic metrics

    Returns:
        List of all findings from all rules
    """
    all_findings = []

    # Apply each rule
    all_findings.extend(rule_emerging_risk(topic_metrics, deltas))
    all_findings.extend(rule_avoided_decision(topic_metrics))
    all_findings.extend(rule_attention_sink(week_metrics, deltas))
    all_findings.extend(rule_scope_creep(week_metrics, topic_metrics))
    all_findings.extend(rule_decision_pressure(topic_metrics, deltas))

    return all_findings
