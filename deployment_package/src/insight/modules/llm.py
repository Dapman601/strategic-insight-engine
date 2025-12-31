"""LLM enhancement layer with Grok primary and OpenAI fallback."""

import json
import logging
from typing import Dict, Any, Tuple
import httpx
from openai import OpenAI

from src.config import get_settings
from src.schemas import LLMEnhancedOutput

settings = get_settings()
logger = logging.getLogger(__name__)


# Strict JSON schema for OpenAI structured output
ENHANCEMENT_SCHEMA = {
    "type": "object",
    "properties": {
        "signals": {
            "type": "array",
            "items": {"type": "string"},
            "description": "Key signals detected from the data"
        },
        "drift": {
            "type": "array",
            "items": {"type": "string"},
            "description": "Strategic drift indicators"
        },
        "decision_pressure": {
            "type": "array",
            "items": {"type": "string"},
            "description": "Decision pressure points identified"
        },
        "recommended_actions": {
            "type": "array",
            "items": {"type": "string"},
            "description": "Recommended actions based on analysis"
        },
        "watchlist": {
            "type": "array",
            "items": {"type": "string"},
            "description": "Items to watch going forward"
        }
    },
    "required": ["signals", "drift", "decision_pressure", "recommended_actions", "watchlist"],
    "additionalProperties": False
}


def prepare_facts_payload(
    week_metrics: Dict[str, Any],
    baseline_metrics: Dict[str, Any],
    deltas: Dict[str, Any],
    topic_metrics: list[Dict[str, Any]],
    findings: list[Dict[str, Any]]
) -> str:
    """
    Prepare facts-only payload for LLM (no raw text).

    Args:
        week_metrics: Current week metrics
        baseline_metrics: 28-day baseline metrics
        deltas: Delta calculations
        topic_metrics: Topic-level metrics
        findings: Rule engine findings

    Returns:
        JSON string of structured facts
    """
    facts = {
        "time_windows": {
            "current_week": "Last 7 days",
            "baseline": "Previous 28 days"
        },
        "metrics": {
            "week": week_metrics,
            "baseline": baseline_metrics
        },
        "deltas": deltas,
        "topics": topic_metrics,
        "rule_findings": findings
    }

    return json.dumps(facts, indent=2)


def call_grok_api(facts_payload: str) -> Tuple[LLMEnhancedOutput | None, str | None, str | None]:
    """
    Call Grok API for enhancement.

    Args:
        facts_payload: JSON facts string

    Returns:
        (Enhanced output or None, model name, response ID)
    """
    if not settings.grok_api_key:
        logger.warning("Grok API key not configured")
        return None, None, None

    try:
        system_prompt = """You are an executive strategic analyst. Analyze the provided metrics and findings to identify:
1. Key signals (emerging patterns, shifts in activity)
2. Strategic drift (deviation from expected patterns)
3. Decision pressure points (where decisions are needed)
4. Recommended actions (specific, actionable steps)
5. Watchlist items (things to monitor)

Provide ONLY factual, evidence-backed insights. No speculation or assumptions.
Output must be valid JSON matching the required schema."""

        user_prompt = f"""Analyze these weekly strategic metrics and provide insights:

{facts_payload}

Return a JSON object with arrays for: signals, drift, decision_pressure, recommended_actions, and watchlist."""

        # Call Grok API (OpenAI-compatible endpoint)
        with httpx.Client(timeout=30.0) as client:
            response = client.post(
                f"{settings.grok_api_url}/chat/completions",
                headers={
                    "Authorization": f"Bearer {settings.grok_api_key}",
                    "Content-Type": "application/json"
                },
                json={
                    "model": settings.grok_model,
                    "messages": [
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": user_prompt}
                    ],
                    "response_format": {"type": "json_object"},
                    "temperature": 0.3
                }
            )

        if response.status_code != 200:
            logger.error(f"Grok API error: {response.status_code} - {response.text}")
            return None, None, None

        result = response.json()
        content = result["choices"][0]["message"]["content"]
        response_id = result.get("id")

        # Parse and validate
        parsed = json.loads(content)
        enhanced = LLMEnhancedOutput(**parsed)

        logger.info("Grok API enhancement successful")
        return enhanced, settings.grok_model, response_id

    except Exception as e:
        logger.error(f"Grok API call failed: {e}")
        return None, None, None


def call_openai_api(facts_payload: str) -> Tuple[LLMEnhancedOutput | None, str | None, str | None]:
    """
    Call OpenAI API with strict structured output.

    Args:
        facts_payload: JSON facts string

    Returns:
        (Enhanced output or None, model name, response ID)
    """
    if not settings.openai_api_key:
        logger.warning("OpenAI API key not configured")
        return None, None, None

    try:
        client = OpenAI(api_key=settings.openai_api_key)

        system_prompt = """You are an executive strategic analyst. Analyze the provided metrics and findings to identify:
1. Key signals (emerging patterns, shifts in activity)
2. Strategic drift (deviation from expected patterns)
3. Decision pressure points (where decisions are needed)
4. Recommended actions (specific, actionable steps)
5. Watchlist items (things to monitor)

Provide ONLY factual, evidence-backed insights. No speculation or assumptions."""

        user_prompt = f"""Analyze these weekly strategic metrics and provide insights:

{facts_payload}"""

        response = client.chat.completions.create(
            model=settings.openai_model,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            response_format={
                "type": "json_schema",
                "json_schema": {
                    "name": "strategic_enhancement",
                    "strict": True,
                    "schema": ENHANCEMENT_SCHEMA
                }
            },
            temperature=0.3
        )

        content = response.choices[0].message.content
        parsed = json.loads(content)

        # Validate with Pydantic
        enhanced = LLMEnhancedOutput(**parsed)

        logger.info("OpenAI API enhancement successful")
        return enhanced, settings.openai_model, response.id

    except Exception as e:
        logger.error(f"OpenAI API call failed: {e}")
        return None, None, None


def enhance_with_llm(
    week_metrics: Dict[str, Any],
    baseline_metrics: Dict[str, Any],
    deltas: Dict[str, Any],
    topic_metrics: list[Dict[str, Any]],
    findings: list[Dict[str, Any]]
) -> Tuple[LLMEnhancedOutput | None, bool, str | None, str | None]:
    """
    Enhance findings with LLM (Grok primary, OpenAI fallback).

    Args:
        week_metrics: Current week metrics
        baseline_metrics: 28-day baseline metrics
        deltas: Delta calculations
        topic_metrics: Topic-level metrics
        findings: Rule engine findings

    Returns:
        (Enhanced output or None, LLM used bool, model name, response ID)
    """
    facts_payload = prepare_facts_payload(
        week_metrics, baseline_metrics, deltas, topic_metrics, findings
    )

    # Try Grok first
    logger.info("Attempting Grok API enhancement...")
    enhanced, model, response_id = call_grok_api(facts_payload)

    if enhanced:
        return enhanced, True, model, response_id

    # Fallback to OpenAI
    logger.info("Grok failed, attempting OpenAI fallback...")
    enhanced, model, response_id = call_openai_api(facts_payload)

    if enhanced:
        return enhanced, True, model, response_id

    # No LLM available
    logger.warning("Both LLM providers failed, proceeding without enhancement")
    return None, False, None, None
