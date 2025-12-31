"""Report generation module for Markdown briefs, watchlists, and audit bundles."""

from typing import Dict, Any, List
from datetime import datetime
import json
import logging

from src.schemas import LLMEnhancedOutput

logger = logging.getLogger(__name__)


def generate_markdown_brief(
    week_start: datetime,
    week_end: datetime,
    week_metrics: Dict[str, Any],
    deltas: Dict[str, Any],
    topic_metrics: List[Dict[str, Any]],
    findings: List[Dict[str, Any]],
    llm_output: LLMEnhancedOutput | None = None
) -> str:
    """
    Generate concise Markdown strategic brief (<800 words).

    Args:
        week_start: Week start date
        week_end: Week end date
        week_metrics: Current week metrics
        deltas: Delta calculations
        topic_metrics: Topic-level metrics
        findings: Rule engine findings
        llm_output: Optional LLM-enhanced insights

    Returns:
        Markdown formatted brief
    """
    lines = []

    # Header
    lines.append(f"# Weekly Strategic Brief")
    lines.append(f"**Period:** {week_start.strftime('%Y-%m-%d')} to {week_end.strftime('%Y-%m-%d')}")
    lines.append("")

    # Executive Summary
    lines.append("## Executive Summary")
    lines.append(f"- **Total Events:** {week_metrics['total_events']} ({deltas['total_events_delta']:+d}, {deltas['total_events_pct_change']:+.1f}%)")
    lines.append(f"- **High Urgency:** {week_metrics['urgency_distribution']['high']} events")
    lines.append(f"- **Decisions Made:** {week_metrics['decision_counts']['made']}")
    lines.append(f"- **Decisions Deferred:** {week_metrics['decision_counts']['deferred']}")
    lines.append(f"- **Topics Identified:** {len(topic_metrics)}")
    lines.append(f"- **Critical Findings:** {sum(1 for f in findings if f['severity'] == 'high')}")
    lines.append("")

    # Signals Section
    lines.append("## Signals")
    if llm_output and llm_output.signals:
        for signal in llm_output.signals:
            lines.append(f"- {signal}")
    else:
        # Fallback to rule-based signals
        high_findings = [f for f in findings if f['severity'] == 'high']
        if high_findings:
            for finding in high_findings[:3]:
                lines.append(f"- **{finding['type'].replace('_', ' ').title()}:** {finding['description']}")
        else:
            lines.append("- No critical signals detected")
    lines.append("")

    # Drift Section
    lines.append("## Drift")
    if llm_output and llm_output.drift:
        for drift_item in llm_output.drift:
            lines.append(f"- {drift_item}")
    else:
        # Fallback to delta-based drift
        if abs(deltas['total_events_pct_change']) > 20:
            lines.append(f"- Event volume shifted {deltas['total_events_pct_change']:+.1f}% from baseline")

        if deltas['urgency_shifts']['high_delta'] > 0:
            lines.append(f"- High-urgency events increased by {deltas['urgency_shifts']['high_delta']}")

        if deltas['decision_shifts']['deferred_delta'] > 2:
            lines.append(f"- Decision deferrals up by {deltas['decision_shifts']['deferred_delta']}")

        if not (abs(deltas['total_events_pct_change']) > 20 or deltas['urgency_shifts']['high_delta'] > 0):
            lines.append("- Activity patterns stable relative to baseline")
    lines.append("")

    # Decision Pressure Section
    lines.append("## Decision Pressure")
    if llm_output and llm_output.decision_pressure:
        for pressure in llm_output.decision_pressure:
            lines.append(f"- {pressure}")
    else:
        # Fallback to rule findings
        decision_findings = [f for f in findings if f['type'] in ['decision_pressure', 'avoided_decision']]
        if decision_findings:
            for finding in decision_findings[:3]:
                lines.append(f"- {finding['description']}")
        else:
            lines.append("- No significant decision pressure detected")
    lines.append("")

    # Recommended Actions Section
    lines.append("## Recommended Actions")
    if llm_output and llm_output.recommended_actions:
        for action in llm_output.recommended_actions:
            lines.append(f"- {action}")
    else:
        # Fallback to rule-based recommendations
        for finding in findings[:5]:
            if finding['severity'] == 'high':
                lines.append(f"- Address {finding['type'].replace('_', ' ')}: {finding['description']}")
        if not findings:
            lines.append("- Continue current trajectory, maintain monitoring")
    lines.append("")

    # Footer
    lines.append("---")
    lines.append(f"*Generated: {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S UTC')}*")
    if llm_output:
        lines.append("*Enhanced with LLM analysis*")

    return "\n".join(lines)


def generate_watchlist(
    topic_metrics: List[Dict[str, Any]],
    findings: List[Dict[str, Any]],
    llm_output: LLMEnhancedOutput | None = None
) -> List[str]:
    """
    Generate watchlist of topics and concerns.

    Args:
        topic_metrics: Topic-level metrics
        findings: Rule engine findings
        llm_output: Optional LLM-enhanced insights

    Returns:
        List of watchlist items
    """
    watchlist = []

    # Add LLM watchlist if available
    if llm_output and llm_output.watchlist:
        watchlist.extend(llm_output.watchlist)

    # Add high-severity findings
    for finding in findings:
        if finding['severity'] == 'high':
            item = f"{finding['type'].replace('_', ' ').title()}: {finding['description']}"
            if item not in watchlist:
                watchlist.append(item)

    # Add high-activity new topics
    for topic in topic_metrics:
        if topic['is_new'] and topic['event_count'] >= 5:
            item = f"New high-activity topic: {topic['event_count']} events, avg urgency {topic['avg_urgency']}"
            if item not in watchlist:
                watchlist.append(item)

    # Add topics with deferred decisions
    for topic in topic_metrics:
        if topic['decisions_deferred'] >= 2:
            item = f"Topic with {topic['decisions_deferred']} deferred decisions: {', '.join(topic['sample_subjects'][:2])}"
            if item not in watchlist:
                watchlist.append(item)

    return watchlist[:10]  # Limit to top 10


def generate_audit_bundle(
    week_start: datetime,
    week_end: datetime,
    baseline_start: datetime,
    week_metrics: Dict[str, Any],
    baseline_metrics: Dict[str, Any],
    deltas: Dict[str, Any],
    topic_metrics: List[Dict[str, Any]],
    findings: List[Dict[str, Any]],
    llm_used: bool,
    llm_model: str | None,
    llm_response_id: str | None
) -> Dict[str, Any]:
    """
    Generate complete audit bundle with all data.

    Args:
        week_start: Week start date
        week_end: Week end date
        baseline_start: Baseline start date
        week_metrics: Current week metrics
        baseline_metrics: 28-day baseline metrics
        deltas: Delta calculations
        topic_metrics: Topic-level metrics
        findings: Rule engine findings
        llm_used: Whether LLM was used
        llm_model: LLM model name if used
        llm_response_id: LLM response ID if used

    Returns:
        Complete audit data dictionary
    """
    return {
        "version": "1.2",
        "generated_at": datetime.utcnow().isoformat(),
        "time_windows": {
            "week_start": week_start.isoformat(),
            "week_end": week_end.isoformat(),
            "baseline_start": baseline_start.isoformat()
        },
        "metrics": {
            "week": week_metrics,
            "baseline": baseline_metrics
        },
        "deltas": deltas,
        "topics": topic_metrics,
        "findings": findings,
        "thresholds": {
            "hdbscan_min_cluster_size": 3,
            "topic_similarity_threshold": 0.85,
            "urgency_low_max": 3,
            "urgency_medium_max": 7
        },
        "llm_enhancement": {
            "used": llm_used,
            "model": llm_model,
            "response_id": llm_response_id
        }
    }
