"""Pydantic schemas for API validation and serialization."""

from pydantic import BaseModel, Field, field_validator
from datetime import datetime
from typing import Literal


class CanonicalEvent(BaseModel):
    """Strict canonical event schema - no deviations allowed."""

    id: str = Field(..., description="Unique identifier, e.g., 'gmail:abc123' or 'read_ai:meet456'")
    source: Literal['email', 'meeting'] = Field(..., description="Event source type")
    timestamp: datetime = Field(..., description="Event timestamp in UTC")
    actor: str = Field(..., description="Person or comma-separated participants")
    direction: Literal['inbound', 'outbound', 'internal', 'unknown'] = Field(..., description="Communication direction")
    subject: str = Field(..., description="Email subject or meeting title")
    text: str = Field(..., description="Body or summary with optional transcript excerpt")
    thread_id: str | None = Field(None, description="Thread identifier for grouping")
    decision: Literal['made', 'deferred', 'none'] = Field(..., description="Decision status")
    action_owner: str | None = Field(None, description="Person responsible for action")
    follow_up_required: bool = Field(..., description="Whether follow-up is needed")
    urgency_score: int = Field(..., ge=0, le=10, description="Urgency level from 0 to 10")
    sentiment: Literal['unknown'] = Field(default='unknown', description="Fixed value, no sentiment analysis")
    raw_ref: str = Field(..., description="Original message ID or URL")

    @field_validator('timestamp')
    @classmethod
    def timestamp_must_be_utc(cls, v: datetime) -> datetime:
        """Ensure timestamp is UTC."""
        if v.tzinfo is None:
            raise ValueError('timestamp must include timezone information')
        return v

    class Config:
        json_schema_extra = {
            "example": {
                "id": "gmail:abc123",
                "source": "email",
                "timestamp": "2025-12-20T10:30:00Z",
                "actor": "john.doe@example.com",
                "direction": "inbound",
                "subject": "Q1 Budget Review",
                "text": "We need to discuss the budget allocation for Q1...",
                "thread_id": "thread_456",
                "decision": "deferred",
                "action_owner": "jane.smith@example.com",
                "follow_up_required": True,
                "urgency_score": 7,
                "sentiment": "unknown",
                "raw_ref": "msg_xyz789"
            }
        }


class IngestResponse(BaseModel):
    """Response model for ingestion endpoints."""
    ok: bool
    id: str


class LLMEnhancedOutput(BaseModel):
    """Structured output from LLM enhancement (strict schema)."""

    signals: list[str] = Field(..., description="Key signals detected")
    drift: list[str] = Field(..., description="Strategic drift indicators")
    decision_pressure: list[str] = Field(..., description="Decision pressure points")
    recommended_actions: list[str] = Field(..., description="Recommended actions")
    watchlist: list[str] = Field(..., description="Items to watch")

    class Config:
        extra = 'forbid'  # No additional properties allowed


class WeeklyBriefOutput(BaseModel):
    """Output model for weekly brief generation."""

    week_start: datetime
    week_end: datetime
    markdown: str
    watchlist: list[str]
    audit: dict
    llm_used: bool
    llm_model: str | None = None
