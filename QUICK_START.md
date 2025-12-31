# Quick Start Guide

Get the Weekly Strategic Insight Engine running in 15 minutes.

## Prerequisites Checklist

- [ ] Ubuntu/Debian server with SSH access
- [ ] Docker and Docker Compose installed
- [ ] PostgreSQL 16+ (or use Docker)
- [ ] n8n instance accessible
- [ ] Slack workspace with bot permissions

## Step 1: Deploy Application (5 minutes)

```bash
# SSH to your server
ssh user@your-hostinger-server

# Clone repository
cd /opt
sudo git clone <your-repo> strategic-insight
cd strategic-insight

# Configure environment
sudo cp .env.production .env
sudo nano .env
```

**Edit .env with**:
```bash
DB_PASSWORD=your_db_password
SLACK_BOT_TOKEN=xoxb-your-token
SLACK_USER_ID=U0123456
GROK_API_KEY=your-grok-key  # Optional
```

```bash
# Deploy
sudo chmod +x deployment/deploy_hostinger.sh
sudo deployment/deploy_hostinger.sh
```

## Step 2: Setup n8n Workflows (5 minutes)

```bash
# Automatic import
python deployment/n8n_setup.py
```

**Or manually**:
1. Go to https://n8n.srv996391.hstgr.cloud
2. Login with: frontendlabs.uk@gmail.com / 4rontEnd#labs
3. Import `n8n_workflows/gmail_to_insight_engine.json`
4. Import `n8n_workflows/readai_to_insight_engine.json`
5. Configure Gmail OAuth in workflow
6. Update API endpoint to `http://your-server-ip:8000/ingest/email`
7. Activate both workflows

## Step 3: Test System (5 minutes)

```bash
# Generate test data
docker exec insight-api python scripts/ingest_demo.py

# Check ingestion
curl http://localhost:8000/stats

# Run weekly processing
docker exec insight-processor python scripts/weekly_run.py
```

**Expected Result**: You should receive a Slack DM with the weekly brief!

## Verify Everything Works

```bash
# Check all containers
docker ps

# Should see:
# - insight-postgres (healthy)
# - insight-api (healthy)
# - insight-processor (running)

# Test API
curl http://localhost:8000/health
# {"status":"healthy","timestamp":"..."}

# Check database
docker exec insight-postgres psql -U insight_user -d strategic_insight -c "SELECT COUNT(*) FROM core_events;"
# Should show 80 test events

# View logs
docker-compose logs -f api
```

## Weekly Automation

The system automatically runs every Monday at 9 AM UTC.

**Manual trigger**:
```bash
docker exec insight-processor python scripts/weekly_run.py
```

## What's Next?

1. **Connect Gmail**: Wait for n8n to poll (hourly) or send test email
2. **Connect Read.ai**: Configure webhook in Read.ai settings
3. **Review First Brief**: Check Slack DM quality
4. **Tune Rules**: Adjust thresholds in `src/config.py` if needed
5. **Monitor**: `docker-compose logs -f`

## Common Issues

**"API not responding"**
```bash
docker-compose restart api
docker logs insight-api
```

**"No Slack message"**
```bash
# Verify tokens
cat .env | grep SLACK
docker-compose restart weekly-processor
```

**"Database connection failed"**
```bash
docker-compose restart postgres
# Wait 10 seconds
docker exec insight-postgres pg_isready
```

## Quick Commands Reference

```bash
# View all services
docker-compose ps

# Restart everything
docker-compose restart

# View live logs
docker-compose logs -f

# Stop everything
docker-compose down

# Start everything
docker-compose up -d

# Run weekly processing
docker exec insight-processor python scripts/weekly_run.py

# Check API stats
curl http://localhost:8000/stats

# Backup database
docker exec insight-postgres pg_dump -U insight_user strategic_insight > backup.sql
```

## Success Criteria

- [ ] All Docker containers running and healthy
- [ ] API responds to health check
- [ ] Test data ingested (80 events)
- [ ] Weekly processing completes without errors
- [ ] Slack DM received with brief
- [ ] n8n workflows active and executing

**All done? You're ready for production!**

For detailed setup, see [SETUP_GUIDE.md](SETUP_GUIDE.md)
For full documentation, see [README.md](README.md)
