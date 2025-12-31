"""Weekly processing script - main orchestrator."""

import sys
import logging
from datetime import datetime, timedelta
from pathlib import Path
import numpy as np

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.database import get_db_context
from src.models import CoreEvent, OutWeeklyBrief
from src.insight.modules.embeddings import generate_embedding
from src.insight.modules.clustering import cluster_events, process_clusters_to_topics
from src.insight.modules.metrics import compute_metrics, compute_deltas, get_topic_metrics
from src.insight.modules.rules import apply_rules
from src.insight.modules.llm import enhance_with_llm
from src.insight.modules.reports import generate_markdown_brief, generate_watchlist, generate_audit_bundle
from src.insight.modules.slack import send_weekly_brief

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def generate_embeddings_for_missing(db):
    """Generate embeddings for events that don't have them."""
    events_without_embeddings = db.query(CoreEvent).filter(
        CoreEvent.embedding.is_(None)
    ).all()

    if not events_without_embeddings:
        logger.info("All events have embeddings")
        return

    logger.info(f"Generating embeddings for {len(events_without_embeddings)} events")

    for event in events_without_embeddings:
        text = f"{event.subject} {event.text}"
        embedding = generate_embedding(text)
        event.embedding = embedding.tolist()

    db.commit()
    logger.info(f"Generated {len(events_without_embeddings)} embeddings")


def run_weekly_processing():
    """Execute weekly processing pipeline."""
    logger.info("=" * 80)
    logger.info("WEEKLY STRATEGIC INSIGHT ENGINE - Processing Started")
    logger.info("=" * 80)

    try:
        with get_db_context() as db:
            # Step 1: Define time windows (UTC)
            now = datetime.utcnow()
            week_end = now.replace(hour=0, minute=0, second=0, microsecond=0)
            week_start = week_end - timedelta(days=7)
            baseline_start = week_start - timedelta(days=28)

            logger.info(f"Time windows:")
            logger.info(f"  Week: {week_start} to {week_end}")
            logger.info(f"  Baseline: {baseline_start} to {week_start}")

            # Step 2: Load events
            week_events = db.query(CoreEvent).filter(
                CoreEvent.timestamp >= week_start,
                CoreEvent.timestamp < week_end
            ).all()

            baseline_events = db.query(CoreEvent).filter(
                CoreEvent.timestamp >= baseline_start,
                CoreEvent.timestamp < week_start
            ).all()

            logger.info(f"Loaded {len(week_events)} week events, {len(baseline_events)} baseline events")

            if len(week_events) == 0:
                logger.warning("No events in current week, skipping processing")
                return

            # Step 3: Generate embeddings if missing
            generate_embeddings_for_missing(db)

            # Reload events with embeddings
            week_events = db.query(CoreEvent).filter(
                CoreEvent.timestamp >= week_start,
                CoreEvent.timestamp < week_end
            ).all()

            # Step 4: Cluster week events
            logger.info("Clustering week events...")
            week_embeddings = np.array([event.embedding for event in week_events])
            labels = cluster_events(week_embeddings)

            # Step 5: Process clusters to topics
            logger.info("Processing clusters to topics...")
            event_topic_map = process_clusters_to_topics(week_events, labels, db)

            # Step 6: Compute metrics
            logger.info("Computing metrics...")
            week_metrics = compute_metrics(week_events)
            baseline_metrics = compute_metrics(baseline_events)
            deltas = compute_deltas(week_metrics, baseline_metrics)

            # Step 7: Get topic metrics
            logger.info("Getting topic metrics...")
            topic_metrics = get_topic_metrics(db, week_events)

            # Step 8: Apply rules
            logger.info("Applying rule engine...")
            findings = apply_rules(week_metrics, baseline_metrics, deltas, topic_metrics)
            findings_dict = [f.to_dict() for f in findings]

            logger.info(f"Generated {len(findings)} findings:")
            for finding in findings:
                logger.info(f"  - [{finding.severity}] {finding.finding_type}: {finding.description}")

            # Step 9: Enhance with LLM
            logger.info("Attempting LLM enhancement...")
            llm_output, llm_used, llm_model, llm_response_id = enhance_with_llm(
                week_metrics, baseline_metrics, deltas, topic_metrics, findings_dict
            )

            if llm_used:
                logger.info(f"LLM enhancement successful with {llm_model}")
            else:
                logger.info("Proceeding without LLM enhancement")

            # Step 10: Generate reports
            logger.info("Generating reports...")

            markdown_brief = generate_markdown_brief(
                week_start, week_end, week_metrics, deltas, topic_metrics,
                findings_dict, llm_output
            )

            watchlist = generate_watchlist(topic_metrics, findings_dict, llm_output)

            audit = generate_audit_bundle(
                week_start, week_end, baseline_start, week_metrics,
                baseline_metrics, deltas, topic_metrics, findings_dict,
                llm_used, llm_model, llm_response_id
            )

            # Step 11: Store in database
            logger.info("Storing weekly brief...")

            brief = OutWeeklyBrief(
                week_start=week_start.date(),
                week_end=week_end.date(),
                markdown=markdown_brief,
                watchlist_json=watchlist,
                audit_json=audit,
                openai_used=llm_used,
                openai_model=llm_model,
                openai_response_id=llm_response_id
            )

            # Check if brief already exists
            existing_brief = db.query(OutWeeklyBrief).filter(
                OutWeeklyBrief.week_start == week_start.date()
            ).first()

            if existing_brief:
                logger.info("Updating existing brief")
                existing_brief.week_end = week_end.date()
                existing_brief.markdown = markdown_brief
                existing_brief.watchlist_json = watchlist
                existing_brief.audit_json = audit
                existing_brief.openai_used = llm_used
                existing_brief.openai_model = llm_model
                existing_brief.openai_response_id = llm_response_id
            else:
                logger.info("Creating new brief")
                db.add(brief)

            db.commit()

            # Step 12: Send to Slack
            logger.info("Sending to Slack...")
            slack_success = send_weekly_brief(
                markdown_brief,
                watchlist,
                week_start.strftime('%Y-%m-%d'),
                week_end.strftime('%Y-%m-%d')
            )

            if slack_success:
                logger.info("Slack delivery successful")
            else:
                logger.warning("Slack delivery failed (check configuration)")

            logger.info("=" * 80)
            logger.info("WEEKLY PROCESSING COMPLETED SUCCESSFULLY")
            logger.info("=" * 80)

            # Print summary
            print("\n" + "=" * 80)
            print("WEEKLY BRIEF GENERATED")
            print("=" * 80)
            print(markdown_brief)
            print("\n" + "=" * 80)
            print("WATCHLIST")
            print("=" * 80)
            for item in watchlist:
                print(f"- {item}")
            print("=" * 80 + "\n")

    except Exception as e:
        logger.error(f"Error in weekly processing: {e}", exc_info=True)
        raise


if __name__ == "__main__":
    run_weekly_processing()
