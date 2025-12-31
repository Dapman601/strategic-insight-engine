"""SQLAlchemy models for the database schema."""

from sqlalchemy import (
    Column, String, Text, Boolean, Integer, DateTime, Date,
    ForeignKey, CheckConstraint, Index
)
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship
from pgvector.sqlalchemy import Vector
from datetime import datetime
import uuid

from src.database import Base


class CoreEvent(Base):
    """Normalized event from email or meeting source."""
    __tablename__ = "core_events"

    id = Column(String, primary_key=True)
    source = Column(String, nullable=False)
    timestamp = Column(DateTime(timezone=True), nullable=False)
    actor = Column(Text, nullable=False)
    direction = Column(String, nullable=False)
    subject = Column(Text)
    text = Column(Text, nullable=False)
    thread_id = Column(String)
    decision = Column(String, nullable=False)
    action_owner = Column(Text)
    follow_up_required = Column(Boolean, nullable=False)
    urgency_score = Column(Integer, nullable=False)
    sentiment = Column(String, nullable=False, default='unknown')
    raw_ref = Column(Text, nullable=False)
    embedding = Column(Vector(384))
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow)
    updated_at = Column(DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    event_topics = relationship("CoreEventTopic", back_populates="event", cascade="all, delete-orphan")

    __table_args__ = (
        CheckConstraint("source IN ('email', 'meeting')", name='check_source'),
        CheckConstraint("direction IN ('inbound', 'outbound', 'internal', 'unknown')", name='check_direction'),
        CheckConstraint("decision IN ('made', 'deferred', 'none')", name='check_decision'),
        CheckConstraint("urgency_score BETWEEN 0 AND 10", name='check_urgency_score'),
        Index('idx_core_events_timestamp', 'timestamp'),
        Index('idx_core_events_source', 'source'),
        Index('idx_core_events_thread_id', 'thread_id'),
        Index('idx_core_events_actor', 'actor'),
        Index('idx_core_events_urgency', 'urgency_score'),
    )


class CoreTopic(Base):
    """Persistent topic identified through clustering."""
    __tablename__ = "core_topics"

    topic_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    centroid = Column(Vector(384), nullable=False)
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow)
    last_seen_at = Column(DateTime(timezone=True), default=datetime.utcnow)
    n_points = Column(Integer, nullable=False, default=0)

    # Relationships
    event_topics = relationship("CoreEventTopic", back_populates="topic", cascade="all, delete-orphan")

    __table_args__ = (
        Index('idx_core_topics_last_seen', 'last_seen_at'),
    )


class CoreEventTopic(Base):
    """Many-to-many relationship between events and topics."""
    __tablename__ = "core_event_topics"

    event_id = Column(String, ForeignKey('core_events.id', ondelete='CASCADE'), primary_key=True)
    topic_id = Column(UUID(as_uuid=True), ForeignKey('core_topics.topic_id', ondelete='CASCADE'), primary_key=True)

    # Relationships
    event = relationship("CoreEvent", back_populates="event_topics")
    topic = relationship("CoreTopic", back_populates="event_topics")


class OutWeeklyBrief(Base):
    """Generated weekly strategic insight report."""
    __tablename__ = "out_weekly_briefs"

    week_start = Column(Date, primary_key=True)
    week_end = Column(Date, nullable=False)
    markdown = Column(Text, nullable=False)
    watchlist_json = Column(JSONB, nullable=False)
    audit_json = Column(JSONB, nullable=False)
    openai_used = Column(Boolean, nullable=False, default=False)
    openai_model = Column(Text)
    openai_response_id = Column(Text)
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow)
