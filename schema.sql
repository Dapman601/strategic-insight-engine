-- Weekly Strategic Insight Engine Database Schema
-- Version 1.2
-- PostgreSQL with pgvector extension

-- Enable pgvector extension for vector operations
CREATE EXTENSION IF NOT EXISTS vector;

-- Core events table: stores all normalized events from emails and meetings
CREATE TABLE IF NOT EXISTS core_events (
  id TEXT PRIMARY KEY,
  source TEXT NOT NULL CHECK (source IN ('email', 'meeting')),
  timestamp TIMESTAMPTZ NOT NULL,
  actor TEXT NOT NULL,
  direction TEXT NOT NULL CHECK (direction IN ('inbound', 'outbound', 'internal', 'unknown')),
  subject TEXT,
  text TEXT NOT NULL,
  thread_id TEXT,
  decision TEXT NOT NULL CHECK (decision IN ('made', 'deferred', 'none')),
  action_owner TEXT,
  follow_up_required BOOLEAN NOT NULL,
  urgency_score INTEGER NOT NULL CHECK (urgency_score BETWEEN 0 AND 10),
  sentiment TEXT NOT NULL DEFAULT 'unknown',
  raw_ref TEXT NOT NULL,
  embedding VECTOR(384),
  created_at TIMESTAMPTZ DEFAULT NOW(),
  updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Topics table: stores persistent topics identified through clustering
CREATE TABLE IF NOT EXISTS core_topics (
  topic_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  centroid VECTOR(384) NOT NULL,
  created_at TIMESTAMPTZ DEFAULT NOW(),
  last_seen_at TIMESTAMPTZ DEFAULT NOW(),
  n_points INTEGER NOT NULL DEFAULT 0
);

-- Event-Topic mapping table: many-to-many relationship
CREATE TABLE IF NOT EXISTS core_event_topics (
  event_id TEXT REFERENCES core_events(id) ON DELETE CASCADE,
  topic_id UUID REFERENCES core_topics(topic_id) ON DELETE CASCADE,
  PRIMARY KEY (event_id, topic_id)
);

-- Weekly briefs output table: stores generated reports
CREATE TABLE IF NOT EXISTS out_weekly_briefs (
  week_start DATE PRIMARY KEY,
  week_end DATE NOT NULL,
  markdown TEXT NOT NULL,
  watchlist_json JSONB NOT NULL,
  audit_json JSONB NOT NULL,
  openai_used BOOLEAN NOT NULL DEFAULT FALSE,
  openai_model TEXT,
  openai_response_id TEXT,
  created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Indexes for performance
CREATE INDEX IF NOT EXISTS idx_core_events_timestamp ON core_events(timestamp);
CREATE INDEX IF NOT EXISTS idx_core_events_source ON core_events(source);
CREATE INDEX IF NOT EXISTS idx_core_events_thread_id ON core_events(thread_id) WHERE thread_id IS NOT NULL;
CREATE INDEX IF NOT EXISTS idx_core_events_actor ON core_events(actor);
CREATE INDEX IF NOT EXISTS idx_core_events_urgency ON core_events(urgency_score);
CREATE INDEX IF NOT EXISTS idx_core_topics_last_seen ON core_topics(last_seen_at);

-- HNSW index for fast vector similarity search
CREATE INDEX IF NOT EXISTS idx_core_topics_centroid ON core_topics USING hnsw (centroid vector_cosine_ops);

-- Function to update updated_at timestamp automatically
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
   NEW.updated_at = NOW();
   RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Trigger to auto-update updated_at on core_events
CREATE TRIGGER update_core_events_updated_at
  BEFORE UPDATE ON core_events
  FOR EACH ROW
  EXECUTE FUNCTION update_updated_at_column();

-- Comments for documentation
COMMENT ON TABLE core_events IS 'Normalized events from email and meeting sources';
COMMENT ON TABLE core_topics IS 'Persistent topics identified through HDBSCAN clustering';
COMMENT ON TABLE core_event_topics IS 'Many-to-many mapping between events and topics';
COMMENT ON TABLE out_weekly_briefs IS 'Generated weekly strategic insight reports';

COMMENT ON COLUMN core_events.embedding IS '384-dimensional vector from all-MiniLM-L6-v2 model';
COMMENT ON COLUMN core_topics.centroid IS 'Rolling average centroid of topic cluster in 384-dimensional space';
COMMENT ON COLUMN core_topics.n_points IS 'Count of events associated with this topic';
