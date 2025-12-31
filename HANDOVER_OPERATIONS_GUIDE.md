# Strategic Insight Engine - Operations & Handover Guide

**Version:** 1.0
**Last Updated:** December 30, 2025
**Production Environment:** Hostinger VPS (72.62.132.205)

---

## 📋 Table of Contents

1. [System Overview](#system-overview)
2. [Daily Operations](#daily-operations)
3. [Monitoring & Health Checks](#monitoring--health-checks)
4. [Troubleshooting Guide](#troubleshooting-guide)
5. [Maintenance Tasks](#maintenance-tasks)
6. [Emergency Procedures](#emergency-procedures)
7. [Configuration Management](#configuration-management)
8. [Backup & Recovery](#backup--recovery)
9. [Scaling & Optimization](#scaling--optimization)
10. [Contact Information](#contact-information)

---

## 🎯 System Overview

### What Does It Do?
The Strategic Insight Engine automatically:
1. **Collects** communication data from Gmail and Read.ai meetings
2. **Analyzes** patterns using machine learning (clustering, embeddings)
3. **Detects** decision pressure, drift, and anomalies
4. **Generates** weekly strategic briefs every Monday at 9 AM UTC
5. **Delivers** insights via Slack to user U01K29DED53

### Key Components
- **API Server** (insight-api): Ingests events via REST endpoints
- **Database** (insight-postgres): Stores events with vector embeddings
- **Processor** (insight-processor): Runs weekly analysis and cron jobs
- **n8n Workflows**: Orchestrates data collection from Gmail and Read.ai

### Production URLs
| Service | URL |
|---------|-----|
| API Health | http://72.62.132.205:8000/health |
| API Stats | http://72.62.132.205:8000/stats |
| API Docs | http://72.62.132.205:8000/docs |
| n8n | https://n8n.srv996391.hstgr.cloud |

---

## 📅 Daily Operations

### Morning Check (5 minutes)
Every morning, verify system health:

```bash
# 1. SSH to VPS
ssh root@72.62.132.205

# 2. Check all containers are running
cd /opt/strategic-insight
docker-compose ps

# Expected output:
# NAME                STATUS              PORTS
# insight-postgres    Up (healthy)        5432/tcp
# insight-api         Up (healthy)        0.0.0.0:8000->8000/tcp
# insight-processor   Up                  -

# 3. Check API health
curl http://localhost:8000/health

# Expected: {"status":"healthy","timestamp":"..."}

# 4. Check event count
curl http://localhost:8000/stats

# Shows: {"total_events":X,"email_events":Y,"meeting_events":Z}
```

### Weekly Brief Check (Monday mornings)
After 9 AM UTC on Mondays:

```bash
# 1. Check if weekly processing ran
docker logs insight-processor --tail=100 | grep "WEEKLY PROCESSING COMPLETED"

# 2. Check Slack delivery
docker logs insight-processor --tail=50 | grep "Slack message sent successfully"

# 3. Verify brief in database
docker exec insight-postgres psql -U insight_user -d strategic_insight -c \
  "SELECT week_start, week_end, created_at FROM out_weekly_briefs ORDER BY created_at DESC LIMIT 1;"

# 4. Check your Slack for the weekly brief message
```

### Event Ingestion Verification
Check that events are being ingested:

```bash
# Check recent events (last 24 hours)
docker exec insight-postgres psql -U insight_user -d strategic_insight -c \
  "SELECT id, source, subject, timestamp FROM core_events
   WHERE timestamp > NOW() - INTERVAL '24 hours'
   ORDER BY timestamp DESC LIMIT 10;"

# Check Gmail ingestion (should see new events hourly)
docker exec insight-postgres psql -U insight_user -d strategic_insight -c \
  "SELECT COUNT(*) FROM core_events
   WHERE source = 'email' AND timestamp > NOW() - INTERVAL '1 day';"

# Check Read.ai ingestion (varies based on meetings)
docker exec insight-postgres psql -U insight_user -d strategic_insight -c \
  "SELECT COUNT(*) FROM core_events
   WHERE source = 'meeting' AND timestamp > NOW() - INTERVAL '7 days';"
```

---

## 📊 Monitoring & Health Checks

### System Health Indicators

#### 1. Container Health
```bash
# Check all containers are running
docker-compose ps

# If any container is down, restart it:
docker-compose restart <container-name>

# Check container logs
docker-compose logs -f api        # API logs
docker-compose logs -f processor  # Weekly processing logs
docker-compose logs -f postgres   # Database logs
```

#### 2. API Health
```bash
# Quick health check
curl http://localhost:8000/health

# Detailed stats
curl http://localhost:8000/stats

# Check from external network (from your local machine)
curl http://72.62.132.205:8000/health
```

#### 3. Database Health
```bash
# Check PostgreSQL is running
docker exec insight-postgres pg_isready -U insight_user

# Check database size
docker exec insight-postgres psql -U insight_user -d strategic_insight -c \
  "SELECT pg_size_pretty(pg_database_size('strategic_insight'));"

# Check table sizes
docker exec insight-postgres psql -U insight_user -d strategic_insight -c \
  "SELECT schemaname, tablename,
   pg_size_pretty(pg_total_relation_size(schemaname||'.'||tablename)) AS size
   FROM pg_tables WHERE schemaname = 'public' ORDER BY pg_total_relation_size(schemaname||'.'||tablename) DESC;"
```

#### 4. Disk Space
```bash
# Check available disk space
df -h /opt/strategic-insight

# Check Docker space usage
docker system df

# Clean up if needed (removes old images)
docker system prune -a --filter "until=168h"
```

#### 5. Weekly Processing Status
```bash
# Check cron job is configured
docker exec insight-processor crontab -l

# Check last weekly processing log
docker exec insight-processor tail -100 /app/logs/weekly.log

# Manually trigger weekly processing (for testing)
docker exec insight-processor python scripts/weekly_run.py
```

### Automated Monitoring Script

Save this as `/opt/strategic-insight/monitor.sh`:

```bash
#!/bin/bash

echo "=== Strategic Insight Engine Health Check ==="
echo "Time: $(date)"
echo ""

# Check containers
echo "[1/5] Container Status:"
docker-compose ps
echo ""

# Check API
echo "[2/5] API Health:"
curl -s http://localhost:8000/health | python3 -m json.tool
echo ""

# Check stats
echo "[3/5] Event Statistics:"
curl -s http://localhost:8000/stats | python3 -m json.tool
echo ""

# Check database
echo "[4/5] Database Status:"
docker exec insight-postgres pg_isready -U insight_user
echo ""

# Check disk space
echo "[5/5] Disk Space:"
df -h /opt/strategic-insight
echo ""

echo "=== Health Check Complete ==="
```

Make it executable:
```bash
chmod +x /opt/strategic-insight/monitor.sh
```

Run it daily:
```bash
/opt/strategic-insight/monitor.sh
```

---

## 🔧 Troubleshooting Guide

### Problem 1: No Events Being Ingested

**Symptoms:**
- Event count not increasing
- No new emails/meetings in database

**Diagnosis:**
```bash
# Check n8n workflows are active
# Visit: https://n8n.srv996391.hstgr.cloud
# Login: frontendlabs.uk@gmail.com / 4rontEnd#labs
# Verify: "Gmail to Insight Engine" and "Read.ai to Insight Engine" show as ACTIVE

# Check recent n8n executions
# In n8n UI: Click "Executions" tab
# Should see recent runs (Gmail: every hour, Read.ai: when meetings occur)

# Check API is accessible
curl http://72.62.132.205:8000/health
```

**Solutions:**
1. **If n8n workflow is inactive:**
   - Log into n8n
   - Open the workflow
   - Click "Active" toggle to enable

2. **If API is not responding:**
   ```bash
   docker-compose restart api
   docker-compose logs api
   ```

3. **If Gmail not polling:**
   - Check Gmail OAuth token hasn't expired
   - Re-authenticate Gmail credential in n8n if needed

---

### Problem 2: Weekly Brief Not Sent

**Symptoms:**
- Monday came and went, no Slack message
- No entry in out_weekly_briefs table

**Diagnosis:**
```bash
# Check cron is running
docker exec insight-processor crontab -l

# Check last run
docker exec insight-processor cat /app/logs/weekly.log | tail -50

# Check processor container is up
docker ps | grep insight-processor
```

**Solutions:**
1. **If cron not configured:**
   ```bash
   docker-compose restart processor
   ```

2. **If processing failed:**
   ```bash
   # Check error logs
   docker exec insight-processor cat /app/logs/weekly.log

   # Run manually to see error
   docker exec insight-processor python scripts/weekly_run.py
   ```

3. **If Slack token expired:**
   - Check .env file has correct SLACK_BOT_TOKEN
   - Regenerate token if needed in Slack App settings

---

### Problem 3: Container Won't Start

**Symptoms:**
- `docker-compose ps` shows container as "Exited"
- Container keeps restarting

**Diagnosis:**
```bash
# Check logs for the failed container
docker-compose logs <container-name>

# Check last 50 lines
docker-compose logs --tail=50 <container-name>
```

**Solutions:**
1. **Database connection issues:**
   ```bash
   # Verify .env has correct DATABASE_URL
   cat .env | grep DATABASE_URL

   # Should be: postgresql://insight_user:ChangeThisPassword123@postgres:5432/strategic_insight

   # If wrong, fix it:
   nano .env

   # Restart containers
   docker-compose down
   docker-compose up -d
   ```

2. **Port already in use:**
   ```bash
   # Check what's using port 8000
   netstat -tulpn | grep 8000

   # Kill the process or change port in docker-compose.yml
   ```

3. **Out of memory:**
   ```bash
   # Check system memory
   free -h

   # If low, restart containers one by one
   docker-compose restart postgres
   sleep 10
   docker-compose restart api
   docker-compose restart processor
   ```

---

### Problem 4: High CPU or Memory Usage

**Symptoms:**
- Server feels slow
- API responses delayed

**Diagnosis:**
```bash
# Check container resource usage
docker stats

# Check what's consuming resources
top
htop  # if installed
```

**Solutions:**
1. **Embeddings generation using too much CPU:**
   - Normal during weekly processing
   - Wait for processing to complete
   - If persistent, check for stuck processes

2. **Memory leak:**
   ```bash
   # Restart containers
   docker-compose restart
   ```

3. **Too many events:**
   ```bash
   # Check event count
   docker exec insight-postgres psql -U insight_user -d strategic_insight -c \
     "SELECT COUNT(*) FROM core_events;"

   # If > 100,000 events, consider archiving old data
   ```

---

### Problem 5: Slack Messages Not Delivered

**Symptoms:**
- Processing completes but no Slack message
- Logs show "Slack delivery failed"

**Diagnosis:**
```bash
# Check Slack configuration
cat .env | grep SLACK

# Should have:
# SLACK_BOT_TOKEN=xoxb-...
# SLACK_USER_ID=U01K29DED53

# Test Slack connection manually
docker exec insight-processor python -c "
from slack_sdk import WebClient
import os
client = WebClient(token='[REDACTED - See .env file]')
response = client.chat_postMessage(channel='U01K29DED53', text='Test message')
print('Success!' if response['ok'] else 'Failed')
"
```

**Solutions:**
1. **Token expired:**
   - Regenerate bot token in Slack App settings
   - Update SLACK_BOT_TOKEN in .env
   - Restart processor: `docker-compose restart processor`

2. **Wrong user ID:**
   - Verify your Slack user ID
   - Update SLACK_USER_ID in .env

3. **Bot not in workspace:**
   - Reinstall Slack app to workspace
   - Ensure bot has chat:write permissions

---

## 🔄 Maintenance Tasks

### Weekly Maintenance (15 minutes)

**Every Monday after brief is sent:**

1. **Verify Brief Quality**
   ```bash
   # Check latest brief
   docker exec insight-postgres psql -U insight_user -d strategic_insight -c \
     "SELECT markdown FROM out_weekly_briefs ORDER BY created_at DESC LIMIT 1;" \
     -t -A > latest_brief.txt

   cat latest_brief.txt
   ```

2. **Review Metrics**
   ```bash
   # Check event distribution
   docker exec insight-postgres psql -U insight_user -d strategic_insight -c \
     "SELECT source, COUNT(*) FROM core_events GROUP BY source;"

   # Check topic count
   docker exec insight-postgres psql -U insight_user -d strategic_insight -c \
     "SELECT COUNT(*) FROM core_topics;"
   ```

3. **Check Logs for Errors**
   ```bash
   docker-compose logs --tail=200 | grep -i error
   docker-compose logs --tail=200 | grep -i warning
   ```

### Monthly Maintenance (30 minutes)

**First Monday of each month:**

1. **Database Cleanup**
   ```bash
   # Archive old briefs (keep last 12 months)
   docker exec insight-postgres psql -U insight_user -d strategic_insight -c \
     "DELETE FROM out_weekly_briefs WHERE created_at < NOW() - INTERVAL '12 months';"

   # Vacuum database
   docker exec insight-postgres psql -U insight_user -d strategic_insight -c "VACUUM ANALYZE;"
   ```

2. **Update Dependencies**
   ```bash
   # Pull latest Docker images (if needed)
   cd /opt/strategic-insight
   docker-compose pull

   # Rebuild with latest packages
   docker-compose build --no-cache
   docker-compose up -d
   ```

3. **Review Disk Usage**
   ```bash
   # Check disk space
   df -h

   # Clean Docker if needed
   docker system prune -a --filter "until=720h"  # Remove images older than 30 days
   ```

4. **Backup Database** (See Backup section below)

### Quarterly Maintenance (1 hour)

**Every 3 months:**

1. **Performance Review**
   - Check average processing time for weekly runs
   - Review database query performance
   - Optimize if needed

2. **Security Updates**
   ```bash
   # Update VPS packages
   apt update && apt upgrade -y

   # Restart containers
   cd /opt/strategic-insight
   docker-compose restart
   ```

3. **Credential Rotation**
   - Rotate database password
   - Regenerate Slack bot token
   - Update Gmail OAuth tokens

---

## 🆘 Emergency Procedures

### Emergency 1: Complete System Down

**Steps:**
1. **Don't Panic** - Data is in database, nothing is lost
2. **Check VPS is reachable:**
   ```bash
   ping 72.62.132.205
   ssh root@72.62.132.205
   ```
3. **If VPS is down:** Contact Hostinger support
4. **If VPS is up, restart everything:**
   ```bash
   cd /opt/strategic-insight
   docker-compose down
   docker-compose up -d

   # Wait 30 seconds
   docker-compose ps
   ```
5. **Verify functionality:**
   ```bash
   curl http://localhost:8000/health
   curl http://localhost:8000/stats
   ```

### Emergency 2: Data Loss Suspected

**Steps:**
1. **Immediately stop writes:**
   ```bash
   docker-compose stop api
   ```
2. **Check database:**
   ```bash
   docker exec insight-postgres psql -U insight_user -d strategic_insight -c \
     "SELECT COUNT(*) FROM core_events;"
   ```
3. **If data is intact:** Restart API
   ```bash
   docker-compose start api
   ```
4. **If data is missing:** Restore from backup (see Backup section)

### Emergency 3: Security Breach Suspected

**Steps:**
1. **Immediately stop all services:**
   ```bash
   docker-compose down
   ```
2. **Change all passwords:**
   - VPS root password
   - Database password
   - n8n password
   - Slack bot token
3. **Review logs for unauthorized access:**
   ```bash
   # Check SSH login attempts
   grep "Failed password" /var/log/auth.log

   # Check API access logs
   docker-compose logs api | grep -E "POST|PUT|DELETE"
   ```
4. **Restore from known good backup**
5. **Restart with new credentials**

### Emergency Contact Numbers
- **VPS Provider (Hostinger):** Check your hosting panel
- **Slack Workspace Admin:** [Your admin contact]
- **System Developer:** [Your contact]

---

## ⚙️ Configuration Management

### Environment Variables (.env)

**Location:** `/opt/strategic-insight/.env`

**Critical Variables:**
```bash
# Database
DATABASE_URL=postgresql://insight_user:ChangeThisPassword123@postgres:5432/strategic_insight
DB_PASSWORD=ChangeThisPassword123

# API
API_HOST=0.0.0.0
API_PORT=8000

# Slack
SLACK_BOT_TOKEN=[REDACTED - See .env file]
SLACK_USER_ID=U01K29DED53

# n8n
N8N_URL=https://n8n.srv996391.hstgr.cloud
N8N_EMAIL=frontendlabs.uk@gmail.com
N8N_PASSWORD=4rontEnd#labs

# Optional: LLM Enhancement
# OPENAI_API_KEY=sk-...
# GROK_API_KEY=xai-...
```

**To Update Configuration:**
```bash
# 1. Edit .env file
nano /opt/strategic-insight/.env

# 2. Restart affected containers
docker-compose restart api processor

# 3. Verify changes
docker-compose logs api | head -20
```

### n8n Workflow Configuration

**Access:** https://n8n.srv996391.hstgr.cloud

**Workflows to Manage:**
1. **Gmail to Insight Engine** (ID: YUjszHZs59XBKaNN)
   - Trigger: Gmail (polls every hour)
   - Credential: Gmail OAuth "Miva" (ID: dDUEFsj2S2JKsQDb)
   - API URL: http://72.62.132.205:8000/ingest/email

2. **Read.ai to Insight Engine** (ID: Zu6VBTt6PRqX7qNH)
   - Trigger: Webhook /webhook/readai-webhook
   - API URL: http://72.62.132.205:8000/ingest/meeting

**To Update Workflow:**
1. Log into n8n
2. Click workflow name
3. Make changes
4. Click "Save"
5. Ensure "Active" toggle is ON

### Cron Schedule

**Location:** Inside insight-processor container

**Current Schedule:**
```
0 9 * * 1 cd /app && python scripts/weekly_run.py >> /app/logs/weekly.log 2>&1
```

**To Modify:**
```bash
# 1. Edit crontab in container
docker exec -it insight-processor crontab -e

# 2. Cron syntax: minute hour day month day-of-week command
# Examples:
# 0 9 * * 1     = Every Monday at 9 AM
# 0 6 * * *     = Every day at 6 AM
# 0 9 * * 1,4   = Every Monday and Thursday at 9 AM

# 3. Save and exit
```

---

## 💾 Backup & Recovery

### Database Backup

**Manual Backup:**
```bash
# Create backup
docker exec insight-postgres pg_dump -U insight_user strategic_insight > \
  backup_$(date +%Y%m%d_%H%M%S).sql

# Compress backup
gzip backup_*.sql

# Transfer to local machine (from your computer)
scp root@72.62.132.205:/opt/strategic-insight/backup_*.sql.gz .
```

**Automated Backup Script:**

Save as `/opt/strategic-insight/backup.sh`:

```bash
#!/bin/bash

BACKUP_DIR="/opt/strategic-insight/backups"
DATE=$(date +%Y%m%d_%H%M%S)
BACKUP_FILE="$BACKUP_DIR/strategic_insight_$DATE.sql"

# Create backup directory
mkdir -p $BACKUP_DIR

# Create backup
docker exec insight-postgres pg_dump -U insight_user strategic_insight > $BACKUP_FILE

# Compress
gzip $BACKUP_FILE

# Delete backups older than 30 days
find $BACKUP_DIR -name "*.sql.gz" -mtime +30 -delete

echo "Backup completed: ${BACKUP_FILE}.gz"
```

Make executable:
```bash
chmod +x /opt/strategic-insight/backup.sh
```

**Schedule Daily Backups:**
```bash
# Add to VPS crontab (not container)
crontab -e

# Add this line:
0 2 * * * /opt/strategic-insight/backup.sh >> /opt/strategic-insight/logs/backup.log 2>&1
```

### Database Restore

**From Backup:**
```bash
# 1. Stop API to prevent writes
docker-compose stop api

# 2. Restore database
gunzip -c backup_20251230_020000.sql.gz | \
  docker exec -i insight-postgres psql -U insight_user -d strategic_insight

# 3. Verify data
docker exec insight-postgres psql -U insight_user -d strategic_insight -c \
  "SELECT COUNT(*) FROM core_events;"

# 4. Restart API
docker-compose start api
```

### Complete System Backup

**What to Backup:**
1. Database (see above)
2. `.env` file
3. `docker-compose.yml`
4. n8n workflow configurations (export from n8n UI)

**Backup Everything:**
```bash
# Create backup archive
cd /opt
tar -czf strategic-insight-full-backup-$(date +%Y%m%d).tar.gz strategic-insight/

# Download to local machine
scp root@72.62.132.205:/opt/strategic-insight-full-backup-*.tar.gz .
```

### Disaster Recovery

**Complete System Restore:**
```bash
# 1. Upload backup to new VPS
scp strategic-insight-full-backup-20251230.tar.gz root@NEW_IP:/opt/

# 2. Extract
cd /opt
tar -xzf strategic-insight-full-backup-20251230.tar.gz

# 3. Start services
cd strategic-insight
docker-compose up -d

# 4. Verify
curl http://localhost:8000/health
```

---

## 📈 Scaling & Optimization

### When to Scale

**Signs you need more resources:**
- API response time > 2 seconds consistently
- Weekly processing takes > 5 minutes
- Database size > 10GB
- VPS CPU usage > 80% regularly

### Vertical Scaling (Upgrade VPS)

**Hostinger VPS Tiers:**
1. Contact Hostinger support
2. Upgrade to higher tier (more CPU/RAM)
3. System will auto-restart
4. No code changes needed

### Horizontal Scaling (Multiple Instances)

**Not currently implemented, but possible:**
- Run multiple API instances behind load balancer
- Use managed PostgreSQL instead of Docker
- Separate processing into dedicated machine

### Performance Optimization

**Database Optimization:**
```bash
# Create additional indexes if queries are slow
docker exec insight-postgres psql -U insight_user -d strategic_insight

# Example: Index on timestamp for faster queries
CREATE INDEX IF NOT EXISTS idx_events_timestamp ON core_events(timestamp);

# Vacuum regularly
VACUUM ANALYZE;
```

**Reduce Event Retention:**
```bash
# Archive events older than 1 year
docker exec insight-postgres psql -U insight_user -d strategic_insight -c \
  "DELETE FROM core_events WHERE timestamp < NOW() - INTERVAL '1 year';"
```

---

## 📞 Contact Information

### Key Accounts & Access

| System | URL/Host | Username | Notes |
|--------|----------|----------|-------|
| VPS | 72.62.132.205 | root | Hostinger VPS |
| n8n | n8n.srv996391.hstgr.cloud | frontendlabs.uk@gmail.com | Workflow automation |
| Gmail | - | frontendlabs.uk@gmail.com | Source account |
| Slack | - | U01K29DED53 | Delivery channel |
| Read.ai | - | [Your account] | Meeting transcripts |

### Support Contacts

**Hostinger Support:**
- Website: https://www.hostinger.com/
- Contact via hosting panel

**Technical Questions:**
- Refer to deployment documentation
- Check logs first: `docker-compose logs`

### Important Files Locations

**On VPS:**
- Application: `/opt/strategic-insight/`
- Logs: `/opt/strategic-insight/logs/`
- Backups: `/opt/strategic-insight/backups/`
- Config: `/opt/strategic-insight/.env`

**On Local Machine:**
- Source Code: `C:\Users\DELL\Documents\n8n_strategic_insight_engine\`
- Documentation: Same directory
- Deployment Guide: `VPS_DEPLOYMENT_GUIDE.md`

---

## 📚 Additional Resources

### Command Reference

**Quick Commands:**
```bash
# SSH to VPS
ssh root@72.62.132.205

# Navigate to app
cd /opt/strategic-insight

# View status
docker-compose ps

# View logs
docker-compose logs -f

# Restart all services
docker-compose restart

# Stop all services
docker-compose down

# Start all services
docker-compose up -d

# Update and rebuild
docker-compose build --no-cache
docker-compose up -d

# Check API health
curl http://localhost:8000/health

# Check stats
curl http://localhost:8000/stats

# Manual weekly run
docker exec insight-processor python scripts/weekly_run.py

# Database access
docker exec -it insight-postgres psql -U insight_user -d strategic_insight
```

### Log Files

**Application Logs:**
```bash
# API logs
docker-compose logs api

# Processor logs
docker-compose logs processor

# Weekly processing logs
docker exec insight-processor cat /app/logs/weekly.log

# All logs
docker-compose logs --tail=100
```

### Documentation Files

1. **DEPLOYMENT_SUMMARY.md** - This file, overview of deployment
2. **VPS_DEPLOYMENT_GUIDE.md** - Step-by-step deployment instructions
3. **README.md** - Project overview and setup
4. **schema.sql** - Database schema definition

---

## ✅ Operational Checklist

### Daily ☀️
- [ ] Check containers are running: `docker-compose ps`
- [ ] Verify API health: `curl http://localhost:8000/health`
- [ ] Check event ingestion: `curl http://localhost:8000/stats`

### Weekly (Monday) 📅
- [ ] Verify weekly brief was sent to Slack
- [ ] Check brief quality and relevance
- [ ] Review any errors in logs
- [ ] Confirm event counts are increasing

### Monthly 📆
- [ ] Review disk space: `df -h`
- [ ] Check database size
- [ ] Verify backups are created
- [ ] Clean old Docker images: `docker system prune`

### Quarterly 🗓️
- [ ] Update system packages: `apt update && apt upgrade`
- [ ] Review and rotate credentials
- [ ] Performance review
- [ ] Test backup restoration

---

**Document Version:** 1.0
**Last Updated:** December 30, 2025
**Next Review Date:** March 30, 2026
**Status:** ✅ System Operational
