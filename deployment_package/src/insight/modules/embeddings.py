"""Embedding generation module using sentence-transformers."""

from sentence_transformers import SentenceTransformer
from functools import lru_cache
import numpy as np
from src.config import get_settings

settings = get_settings()


@lru_cache(maxsize=1)
def get_embedding_model() -> SentenceTransformer:
    """Get cached embedding model instance."""
    return SentenceTransformer(settings.embedding_model)


def generate_embedding(text: str) -> np.ndarray:
    """
    Generate 384-dimensional embedding for text using all-MiniLM-L6-v2.

    Args:
        text: Input text to embed

    Returns:
        384-dimensional numpy array
    """
    model = get_embedding_model()
    embedding = model.encode(text, convert_to_numpy=True, show_progress_bar=False)
    return embedding


def generate_embeddings_batch(texts: list[str]) -> np.ndarray:
    """
    Generate embeddings for multiple texts efficiently.

    Args:
        texts: List of texts to embed

    Returns:
        Array of shape (len(texts), 384)
    """
    model = get_embedding_model()
    embeddings = model.encode(texts, convert_to_numpy=True, show_progress_bar=False, batch_size=32)
    return embeddings


def cosine_similarity(a: np.ndarray, b: np.ndarray) -> float:
    """
    Calculate cosine similarity between two vectors.

    Args:
        a: First vector
        b: Second vector

    Returns:
        Cosine similarity score (0-1)
    """
    dot_product = np.dot(a, b)
    norm_a = np.linalg.norm(a)
    norm_b = np.linalg.norm(b)

    if norm_a == 0 or norm_b == 0:
        return 0.0

    return float(dot_product / (norm_a * norm_b))


def compute_centroid(embeddings: list[np.ndarray]) -> np.ndarray:
    """
    Compute centroid (mean) of multiple embeddings.

    Args:
        embeddings: List of embedding vectors

    Returns:
        Centroid vector
    """
    return np.mean(embeddings, axis=0)


def rolling_average_update(old_centroid: np.ndarray, new_embedding: np.ndarray, n_points: int) -> np.ndarray:
    """
    Update centroid using rolling average formula.

    Args:
        old_centroid: Existing centroid
        new_embedding: New embedding to incorporate
        n_points: Number of points before adding this one

    Returns:
        Updated centroid
    """
    updated = (old_centroid * n_points + new_embedding) / (n_points + 1)
    return updated
