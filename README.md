# Weekly Strategic Insight Engine

**Version 1.2** | **LLM-Ready Automated Strategic Insights**

A fully automated system that ingests emails and meeting notes, applies deterministic analytics with HDBSCAN clustering, and optionally enhances findings with LLM analysis (Grok primary, OpenAI fallback). Delivers concise weekly strategic briefs via Slack.

## Features

- **Automated Event Ingestion**: FastAPI endpoints for Gmail and Read.ai integration via n8n
- **Deterministic Analytics**: Metrics computation, topic clustering (HDBSCAN), and rule-based findings
- **LLM Enhancement**: Optional Grok/OpenAI analysis with strict structured output (system works without LLM)
- **Weekly Reports**: Concise Markdown briefs (<800 words) with evidence-backed insights
- **Slack Delivery**: Automatic DM delivery with watchlist
- **Complete Audit Trail**: JSON bundles with all metrics, deltas, and thresholds
- **Docker Deployment**: Production-ready containerized deployment
- **Hostinger Compatible**: Deployment scripts for VPS hosting

## Architecture

```
┌─────────────┐     ┌──────────┐     ┌─────────────┐
│   Gmail     │────▶│   n8n    │────▶│  FastAPI    │
└─────────────┘     │ Workflows│     │  Ingestion  │
                    │          │     └──────┬──────┘
┌─────────────┐     │          │            │
│  Read.ai    │────▶│          │            │
└─────────────┘     └──────────┘            │
                                            ▼
                                   ┌────────────────┐
                                   │   PostgreSQL   │
                                   │   + pgvector   │
                                   └────────┬───────┘
                                            │
                    ┌───────────────────────┤
                    ▼                       ▼
            ┌───────────────┐      ┌──────────────┐
            │   Embedding   │      │  Clustering  │
            │  (all-MiniLM) │      │   (HDBSCAN)  │
            └───────────────┘      └──────┬───────┘
                                          │
                    ┌─────────────────────┤
                    ▼                     ▼
            ┌──────────────┐      ┌─────────────┐
            │   Metrics    │      │    Rules    │
            │  Calculator  │      │   Engine    │
            └──────┬───────┘      └──────┬──────┘
                   │                     │
                   └──────────┬──────────┘
                              ▼
                     ┌─────────────────┐
                     │  LLM Enhancement│
                     │  Grok / OpenAI  │
                     │   (Optional)    │
                     └────────┬────────┘
                              ▼
                     ┌─────────────────┐
                     │ Report Generator│
                     │  Brief/Watchlist│
                     └────────┬────────┘
                              ▼
                        ┌──────────┐
                        │  Slack   │
                        │    DM    │
                        └──────────┘
```

## Quick Start

### Prerequisites

- Python 3.11+
- PostgreSQL 16+ with pgvector extension
- Docker & Docker Compose (for production)
- n8n instance (provided: https://n8n.srv996391.hstgr.cloud)

### Local Development Setup

1. **Clone and Install**
```bash
cd n8n_strategic_insight_engine
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

2. **Setup Database**
```bash
# Create PostgreSQL database
createdb strategic_insight

# Apply schema
psql strategic_insight < schema.sql
```

3. **Configure Environment**
```bash
cp .env.example .env
# Edit .env with your credentials
```

4. **Start API Server**
```bash
python api/main.py
# API available at http://localhost:8000
```

5. **Test with Synthetic Data**
```bash
# In another terminal
python scripts/ingest_demo.py
```

6. **Run Weekly Processing**
```bash
python scripts/weekly_run.py
```

## Production Deployment (Docker)

### Deploy to Hostinger VPS

1. **Upload Project**
```bash
# SCP or git clone to your Hostinger VPS
scp -r . user@your-server:/opt/strategic-insight/
```

2. **Configure Production Environment**
```bash
cd /opt/strategic-insight
cp .env.production .env
nano .env  # Add your actual credentials
```

3. **Run Deployment Script**
```bash
chmod +x deployment/deploy_hostinger.sh
sudo deployment/deploy_hostinger.sh
```

4. **Setup Systemd (Optional)**
```bash
chmod +x deployment/setup_systemd.sh
sudo deployment/setup_systemd.sh
```

### Manual Docker Deployment

```bash
# Build and start
docker-compose up -d

# Check status
docker-compose ps

# View logs
docker-compose logs -f

# Manual weekly run
docker exec insight-processor python scripts/weekly_run.py
```

## n8n Workflow Setup

### Automatic Import (Recommended)

```bash
python deployment/n8n_setup.py
```

### Manual Import

1. Log in to n8n: https://n8n.srv996391.hstgr.cloud
2. Import workflows from `n8n_workflows/` directory:
   - `gmail_to_insight_engine.json`
   - `readai_to_insight_engine.json`
3. Configure Gmail OAuth2 credentials
4. Update API endpoint URLs to point to your deployed API
5. Activate workflows

## Configuration

### Environment Variables

| Variable | Description | Required |
|----------|-------------|----------|
| `DATABASE_URL` | PostgreSQL connection string | Yes |
| `GROK_API_KEY` | Grok API key (primary LLM) | No* |
| `OPENAI_API_KEY` | OpenAI API key (fallback) | No* |
| `SLACK_BOT_TOKEN` | Slack bot token | Yes |
| `SLACK_USER_ID` | Slack user ID for DMs | Yes |
| `N8N_URL` | n8n instance URL | Yes |
| `N8N_EMAIL` | n8n login email | Yes |
| `N8N_PASSWORD` | n8n login password | Yes |

*System works fully without LLM keys (uses rule-based findings only)

### Processing Configuration

| Parameter | Default | Description |
|-----------|---------|-------------|
| `HDBSCAN_MIN_CLUSTER_SIZE` | 3 | Minimum events for cluster |
| `TOPIC_SIMILARITY_THRESHOLD` | 0.85 | Cosine similarity for topic matching |
| `URGENCY_LOW_MAX` | 3 | Max score for low urgency |
| `URGENCY_MEDIUM_MAX` | 7 | Max score for medium urgency |

## API Endpoints

### Ingestion

- `POST /ingest/email` - Ingest normalized email event
- `POST /ingest/meeting` - Ingest normalized meeting event

### Health & Stats

- `GET /health` - Health check
- `GET /stats` - Ingestion statistics

### Example Request

```bash
curl -X POST http://localhost:8000/ingest/email \
  -H "Content-Type: application/json" \
  -d '{
    "id": "gmail:abc123",
    "source": "email",
    "timestamp": "2025-12-20T10:30:00Z",
    "actor": "john@example.com",
    "direction": "inbound",
    "subject": "Q1 Budget Review",
    "text": "We need to discuss the budget...",
    "thread_id": "thread_456",
    "decision": "deferred",
    "action_owner": null,
    "follow_up_required": true,
    "urgency_score": 7,
    "sentiment": "unknown",
    "raw_ref": "msg_xyz789"
  }'
```

## Weekly Processing Logic

The system runs weekly processing every Monday at 9 AM UTC (configurable via cron):

1. **Time Windows**: Define 7-day week and 28-day baseline
2. **Load Events**: Query events from both windows
3. **Generate Embeddings**: Create 384-dim vectors (all-MiniLM-L6-v2)
4. **Cluster**: Apply HDBSCAN to week events only
5. **Topic Matching**: Match clusters to persistent topics (cosine ≥0.85)
6. **Metrics**: Compute counts, distributions, deltas
7. **Rule Engine**: Apply hard-coded detection rules
8. **LLM Enhancement**: Optional structured enhancement (Grok → OpenAI)
9. **Report Generation**: Create Markdown brief + watchlist + audit JSON
10. **Delivery**: Send via Slack DM

## Rule Engine Findings

Hard-coded rules detect:

- **Emerging Risk**: New high-urgency topic with no decisions
- **Avoided Decision**: Topic with ≥3 deferred decisions
- **Attention Sink**: Single actor >30% of events
- **Scope Creep**: Repeated thread (≥3) without action owner
- **Decision Pressure**: High follow-ups + deferred decisions

## Database Schema

### Core Tables

- `core_events` - Normalized events with embeddings
- `core_topics` - Persistent topics with centroids
- `core_event_topics` - Many-to-many mapping
- `out_weekly_briefs` - Generated reports

### Key Indexes

- HNSW index on topic centroids for fast vector search
- B-tree indexes on timestamp, actor, thread_id

## Output Format

### Weekly Brief (Markdown)

```markdown
# Weekly Strategic Brief
**Period:** 2025-12-20 to 2025-12-27

## Executive Summary
- **Total Events:** 45 (+12, +36.4%)
- **High Urgency:** 8 events
- **Decisions Made:** 5
...

## Signals
- Key signal 1
- Key signal 2

## Drift
- Strategic drift indicator 1

## Decision Pressure
- Pressure point 1

## Recommended Actions
- Action 1
- Action 2
```

### Watchlist (JSON Array)

```json
[
  "Emerging Risk: 5 high-urgency events, no decisions",
  "Topic with 3 deferred decisions: Budget planning, Q1 review"
]
```

### Audit Bundle (JSON)

Complete reproducible data including:
- Time windows
- Metrics (week + baseline)
- Deltas
- Topics with sample subjects
- Rule findings
- Thresholds
- LLM metadata

## Testing

### Run Test Suite

```bash
# Start API
python api/main.py

# Generate synthetic data (80 events)
python scripts/ingest_demo.py

# Run weekly processing
python scripts/weekly_run.py
```

## Troubleshooting

### Common Issues

**Embeddings not generating**
- Check sentence-transformers installation
- Verify model downloads to `~/.cache/torch/sentence_transformers/`

**HDBSCAN clustering fails**
- Ensure at least 3 events in week window
- Check min_cluster_size configuration

**LLM enhancement fails**
- System continues with rule-based findings
- Verify API keys in .env
- Check API endpoint connectivity

**Slack delivery fails**
- Verify SLACK_BOT_TOKEN and SLACK_USER_ID
- Check bot permissions (chat:write)
- Ensure bot is added to workspace

### Docker Issues

```bash
# View logs
docker-compose logs -f api
docker-compose logs -f postgres

# Restart services
docker-compose restart

# Rebuild from scratch
docker-compose down -v
docker-compose up -d --build
```

## Maintenance

### Database Backups

```bash
# Backup
docker exec insight-postgres pg_dump -U insight_user strategic_insight > backup.sql

# Restore
docker exec -i insight-postgres psql -U insight_user strategic_insight < backup.sql
```

### Log Rotation

Logs are stored in `./logs/`:
- `weekly.log` - Weekly processing logs
- Docker logs managed by Docker daemon

### Updating

```bash
# Pull latest code
git pull

# Rebuild and restart
docker-compose down
docker-compose up -d --build
```

## Security Considerations

- Store credentials in `.env` (never commit)
- Use strong database passwords
- Restrict API access with firewall rules
- Enable HTTPS with reverse proxy (nginx/traefik)
- Rotate API keys regularly
- Review Slack bot permissions

## Cost Optimization

**LLM Usage**:
- Grok: Primary (cost-effective)
- OpenAI: Fallback only
- System fully functional without either

**Database**:
- Weekly cleanup of old events (optional)
- Archive briefs older than 90 days

## Support & Contributing

- Issues: File issues for bugs or feature requests
- Documentation: See `docs/` for detailed specs
- SOW Reference: See project SOW for complete specification

## License

Proprietary - All rights reserved

## Credits

**Developed for**: Strategic Insight Automation
**Version**: 1.2
**Date**: December 2025

---

**Next Steps After Deployment**:
1. Configure n8n workflows
2. Set up Slack bot
3. Configure LLM API keys
4. Test with synthetic data
5. Monitor first weekly run
6. Review and adjust rules as needed
