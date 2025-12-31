"""FastAPI application for event ingestion."""

from fastapi import FastAPI, Depends, HTTPException, status
from sqlalchemy.orm import Session
from datetime import datetime
import logging

from src.database import get_db
from src.schemas import CanonicalEvent, IngestResponse
from src.models import CoreEvent
from src.insight.modules.embeddings import generate_embedding

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Create FastAPI app
app = FastAPI(
    title="Weekly Strategic Insight Engine",
    description="Event ingestion API for strategic insights",
    version="1.2"
)


@app.get("/")
def root():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "service": "Weekly Strategic Insight Engine",
        "version": "1.2"
    }


@app.get("/health")
def health_check():
    """Detailed health check."""
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat()
    }


@app.post("/ingest/email", response_model=IngestResponse)
def ingest_email(event: CanonicalEvent, db: Session = Depends(get_db)):
    """
    Ingest and normalize email event.

    Args:
        event: Canonical event schema
        db: Database session

    Returns:
        Ingestion response with event ID
    """
    try:
        # Check if event already exists
        existing_event = db.query(CoreEvent).filter(CoreEvent.id == event.id).first()

        if existing_event:
            # Update existing event
            logger.info(f"Updating existing email event: {event.id}")

            existing_event.source = event.source
            existing_event.timestamp = event.timestamp
            existing_event.actor = event.actor
            existing_event.direction = event.direction
            existing_event.subject = event.subject
            existing_event.text = event.text
            existing_event.thread_id = event.thread_id
            existing_event.decision = event.decision
            existing_event.action_owner = event.action_owner
            existing_event.follow_up_required = event.follow_up_required
            existing_event.urgency_score = event.urgency_score
            existing_event.sentiment = event.sentiment
            existing_event.raw_ref = event.raw_ref
            existing_event.updated_at = datetime.utcnow()

            # Generate new embedding
            embedding = generate_embedding(f"{event.subject} {event.text}")
            existing_event.embedding = embedding.tolist()

        else:
            # Create new event
            logger.info(f"Creating new email event: {event.id}")

            # Generate embedding
            embedding = generate_embedding(f"{event.subject} {event.text}")

            new_event = CoreEvent(
                id=event.id,
                source=event.source,
                timestamp=event.timestamp,
                actor=event.actor,
                direction=event.direction,
                subject=event.subject,
                text=event.text,
                thread_id=event.thread_id,
                decision=event.decision,
                action_owner=event.action_owner,
                follow_up_required=event.follow_up_required,
                urgency_score=event.urgency_score,
                sentiment=event.sentiment,
                raw_ref=event.raw_ref,
                embedding=embedding.tolist()
            )

            db.add(new_event)

        db.commit()

        return IngestResponse(ok=True, id=event.id)

    except Exception as e:
        logger.error(f"Error ingesting email event: {e}")
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to ingest event: {str(e)}"
        )


@app.post("/ingest/meeting", response_model=IngestResponse)
def ingest_meeting(event: CanonicalEvent, db: Session = Depends(get_db)):
    """
    Ingest and normalize meeting event.

    Args:
        event: Canonical event schema
        db: Database session

    Returns:
        Ingestion response with event ID
    """
    try:
        # Check if event already exists
        existing_event = db.query(CoreEvent).filter(CoreEvent.id == event.id).first()

        if existing_event:
            # Update existing event
            logger.info(f"Updating existing meeting event: {event.id}")

            existing_event.source = event.source
            existing_event.timestamp = event.timestamp
            existing_event.actor = event.actor
            existing_event.direction = event.direction
            existing_event.subject = event.subject
            existing_event.text = event.text
            existing_event.thread_id = event.thread_id
            existing_event.decision = event.decision
            existing_event.action_owner = event.action_owner
            existing_event.follow_up_required = event.follow_up_required
            existing_event.urgency_score = event.urgency_score
            existing_event.sentiment = event.sentiment
            existing_event.raw_ref = event.raw_ref
            existing_event.updated_at = datetime.utcnow()

            # Generate new embedding
            embedding = generate_embedding(f"{event.subject} {event.text}")
            existing_event.embedding = embedding.tolist()

        else:
            # Create new event
            logger.info(f"Creating new meeting event: {event.id}")

            # Generate embedding
            embedding = generate_embedding(f"{event.subject} {event.text}")

            new_event = CoreEvent(
                id=event.id,
                source=event.source,
                timestamp=event.timestamp,
                actor=event.actor,
                direction=event.direction,
                subject=event.subject,
                text=event.text,
                thread_id=event.thread_id,
                decision=event.decision,
                action_owner=event.action_owner,
                follow_up_required=event.follow_up_required,
                urgency_score=event.urgency_score,
                sentiment=event.sentiment,
                raw_ref=event.raw_ref,
                embedding=embedding.tolist()
            )

            db.add(new_event)

        db.commit()

        return IngestResponse(ok=True, id=event.id)

    except Exception as e:
        logger.error(f"Error ingesting meeting event: {e}")
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to ingest event: {str(e)}"
        )


@app.get("/stats")
def get_stats(db: Session = Depends(get_db)):
    """Get ingestion statistics."""
    try:
        total_events = db.query(CoreEvent).count()
        email_events = db.query(CoreEvent).filter(CoreEvent.source == 'email').count()
        meeting_events = db.query(CoreEvent).filter(CoreEvent.source == 'meeting').count()

        return {
            "total_events": total_events,
            "email_events": email_events,
            "meeting_events": meeting_events
        }

    except Exception as e:
        logger.error(f"Error getting stats: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get stats: {str(e)}"
        )


if __name__ == "__main__":
    import uvicorn
    from src.config import get_settings

    settings = get_settings()
    uvicorn.run(
        "api.main:app",
        host=settings.api_host,
        port=settings.api_port,
        reload=settings.api_reload
    )
