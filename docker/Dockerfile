# Weekly Strategic Insight Engine - Docker Image
FROM python:3.11

# Set environment variables
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

# Install build dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    g++ \
    && rm -rf /var/lib/apt/lists/*

# Create app directory
WORKDIR /app

# Copy requirements first for better caching
COPY requirements.txt .

# Install PyTorch CPU version with pip cache enabled for better recovery
RUN --mount=type=cache,target=/root/.cache/pip \
    pip install --default-timeout=300 --retries 10 torch==2.1.0+cpu --index-url https://download.pytorch.org/whl/cpu

# Install remaining Python dependencies with pip cache
RUN --mount=type=cache,target=/root/.cache/pip \
    pip install --default-timeout=300 --retries 10 -r requirements.txt

# Install cron for scheduled tasks (after PyTorch to preserve cache)
RUN apt-get update && apt-get install -y --no-install-recommends cron \
    && rm -rf /var/lib/apt/lists/*

# Copy application code
COPY src/ ./src/
COPY api/ ./api/
COPY scripts/ ./scripts/
COPY schema.sql .

# Create logs directory
RUN mkdir -p /app/logs

# Expose API port
EXPOSE 8000

# Health check (using Python instead of curl)
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8000/health')" || exit 1

# Default command (can be overridden in docker-compose)
CMD ["python", "-m", "uvicorn", "api.main:app", "--host", "0.0.0.0", "--port", "8000"]
