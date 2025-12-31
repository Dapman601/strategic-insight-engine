"""Topic clustering and detection using HDBSCAN."""

import numpy as np
import hdbscan
from sqlalchemy.orm import Session
from typing import List, Dict, Tuple
from uuid import UUID
import logging

from src.models import CoreEvent, CoreTopic, CoreEventTopic
from src.insight.modules.embeddings import cosine_similarity, compute_centroid, rolling_average_update
from src.config import get_settings

settings = get_settings()
logger = logging.getLogger(__name__)


def cluster_events(embeddings: np.ndarray, min_cluster_size: int = None) -> np.ndarray:
    """
    Cluster embeddings using HDBSCAN.

    Args:
        embeddings: Array of shape (n_events, 384)
        min_cluster_size: Minimum cluster size (defaults to config)

    Returns:
        Array of cluster labels (-1 for noise)
    """
    if min_cluster_size is None:
        min_cluster_size = settings.hdbscan_min_cluster_size

    if len(embeddings) < min_cluster_size:
        logger.warning(f"Not enough events ({len(embeddings)}) for clustering (min: {min_cluster_size})")
        return np.array([-1] * len(embeddings))

    clusterer = hdbscan.HDBSCAN(
        min_cluster_size=min_cluster_size,
        metric='euclidean',
        cluster_selection_method='eom'
    )

    labels = clusterer.fit_predict(embeddings)

    n_clusters = len(set(labels)) - (1 if -1 in labels else 0)
    n_noise = list(labels).count(-1)
    logger.info(f"HDBSCAN: {n_clusters} clusters, {n_noise} noise points")

    return labels


def match_to_existing_topic(
    embedding: np.ndarray,
    db: Session,
    threshold: float = None
) -> Tuple[CoreTopic | None, float]:
    """
    Find existing topic that matches embedding above threshold.

    Args:
        embedding: Event embedding to match
        db: Database session
        threshold: Similarity threshold (defaults to config)

    Returns:
        (Matching topic or None, best similarity score)
    """
    if threshold is None:
        threshold = settings.topic_similarity_threshold

    topics = db.query(CoreTopic).all()

    if not topics:
        return None, 0.0

    best_topic = None
    best_similarity = 0.0

    for topic in topics:
        centroid_array = np.array(topic.centroid)
        similarity = cosine_similarity(embedding, centroid_array)

        if similarity > best_similarity:
            best_similarity = similarity
            best_topic = topic

    if best_similarity >= threshold:
        return best_topic, best_similarity
    else:
        return None, best_similarity


def process_clusters_to_topics(
    events: List[CoreEvent],
    labels: np.ndarray,
    db: Session
) -> Dict[str, UUID]:
    """
    Process cluster labels and map events to topics.

    Args:
        events: List of events (must have embeddings)
        labels: Cluster labels from HDBSCAN
        db: Database session

    Returns:
        Dictionary mapping event_id to topic_id
    """
    event_topic_map = {}

    # Group events by cluster
    clusters = {}
    for i, (event, label) in enumerate(zip(events, labels)):
        if label == -1:  # Skip noise
            continue

        if label not in clusters:
            clusters[label] = []
        clusters[label].append(event)

    logger.info(f"Processing {len(clusters)} clusters")

    # Process each cluster
    for cluster_id, cluster_events in clusters.items():
        # Compute cluster centroid
        embeddings = [np.array(e.embedding) for e in cluster_events]
        cluster_centroid = compute_centroid(embeddings)

        # Try to match to existing topic
        matched_topic, similarity = match_to_existing_topic(cluster_centroid, db)

        if matched_topic:
            # Update existing topic with rolling average
            logger.info(f"Cluster {cluster_id} matched to existing topic {matched_topic.topic_id} (sim: {similarity:.3f})")

            new_centroid = rolling_average_update(
                np.array(matched_topic.centroid),
                cluster_centroid,
                matched_topic.n_points
            )

            matched_topic.centroid = new_centroid.tolist()
            matched_topic.n_points += len(cluster_events)
            matched_topic.last_seen_at = max(e.timestamp for e in cluster_events)

            topic_id = matched_topic.topic_id
        else:
            # Create new topic
            logger.info(f"Cluster {cluster_id} creating new topic")

            new_topic = CoreTopic(
                centroid=cluster_centroid.tolist(),
                n_points=len(cluster_events),
                last_seen_at=max(e.timestamp for e in cluster_events)
            )
            db.add(new_topic)
            db.flush()  # Get topic_id

            topic_id = new_topic.topic_id

        # Map all events in cluster to this topic
        for event in cluster_events:
            event_topic_map[event.id] = topic_id

            # Create event-topic mapping
            mapping = CoreEventTopic(event_id=event.id, topic_id=topic_id)
            db.add(mapping)

    db.commit()
    logger.info(f"Mapped {len(event_topic_map)} events to topics")

    return event_topic_map
