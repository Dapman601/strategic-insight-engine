# Strategic Insight Engine - Quick Reference Card

**Production URL:** http://72.62.132.205:8000
**VPS Access:** `ssh root@72.62.132.205`
**App Directory:** `/opt/strategic-insight`

---

## 🚀 Common Commands

### Access VPS
```bash
ssh root@72.62.132.205
cd /opt/strategic-insight
```

### Check System Status
```bash
# Container status
docker-compose ps

# API health
curl http://localhost:8000/health

# Event statistics
curl http://localhost:8000/stats

# All service logs (live)
docker-compose logs -f
```

### Restart Services
```bash
# Restart all
docker-compose restart

# Restart specific service
docker-compose restart api
docker-compose restart processor
docker-compose restart postgres

# Full rebuild
docker-compose down
docker-compose up -d
```

### View Logs
```bash
# Live logs (all services)
docker-compose logs -f

# Last 100 lines (specific service)
docker-compose logs --tail=100 api
docker-compose logs --tail=100 processor

# Weekly processing log
docker exec insight-processor cat /app/logs/weekly.log

# Search for errors
docker-compose logs | grep -i error
```

### Database Access
```bash
# Connect to database
docker exec -it insight-postgres psql -U insight_user -d strategic_insight

# Quick queries
docker exec insight-postgres psql -U insight_user -d strategic_insight -c \
  "SELECT COUNT(*) FROM core_events;"

docker exec insight-postgres psql -U insight_user -d strategic_insight -c \
  "SELECT id, subject, timestamp FROM core_events ORDER BY timestamp DESC LIMIT 5;"

docker exec insight-postgres psql -U insight_user -d strategic_insight -c \
  "SELECT week_start, week_end FROM out_weekly_briefs ORDER BY created_at DESC LIMIT 3;"
```

### Manual Operations
```bash
# Trigger weekly processing manually
docker exec insight-processor python scripts/weekly_run.py

# Generate synthetic test data
docker exec insight-processor python scripts/ingest_demo.py

# Check cron schedule
docker exec insight-processor crontab -l
```

---

## 🔍 Troubleshooting Quick Fixes

### API Not Responding
```bash
docker-compose restart api
docker-compose logs api
```

### No Events Being Ingested
```bash
# Check n8n workflows are active
# Visit: https://n8n.srv996391.hstgr.cloud
# Login: frontendlabs.uk@gmail.com / 4rontEnd#labs

# Check API is reachable
curl http://72.62.132.205:8000/health
```

### Weekly Brief Not Sent
```bash
# Check processor is running
docker ps | grep processor

# Check last run
docker exec insight-processor cat /app/logs/weekly.log | tail -50

# Run manually to debug
docker exec insight-processor python scripts/weekly_run.py
```

### Container Won't Start
```bash
# Check logs
docker-compose logs <container-name>

# Rebuild container
docker-compose down
docker-compose build --no-cache <container-name>
docker-compose up -d
```

### Out of Disk Space
```bash
# Check space
df -h

# Clean Docker
docker system prune -a

# Clean old logs
docker exec insight-processor rm -f /app/logs/*.log.*
```

---

## 💾 Backup & Restore

### Quick Backup
```bash
# Database backup
docker exec insight-postgres pg_dump -U insight_user strategic_insight > \
  backup_$(date +%Y%m%d).sql
gzip backup_*.sql

# Download to local
# (Run from your computer)
scp root@72.62.132.205:/opt/strategic-insight/backup_*.sql.gz .
```

### Quick Restore
```bash
# Stop writes
docker-compose stop api

# Restore
gunzip -c backup_20251230.sql.gz | \
  docker exec -i insight-postgres psql -U insight_user -d strategic_insight

# Restart
docker-compose start api
```

---

## 📊 Key Metrics to Monitor

### Healthy System
- ✅ All 3 containers "Up"
- ✅ API responds with {"status":"healthy"}
- ✅ Event count increasing daily
- ✅ Weekly brief sent every Monday
- ✅ Disk usage < 80%

### Warning Signs
- ⚠️ Container status "Restarting"
- ⚠️ API response time > 2 seconds
- ⚠️ No new events in 24 hours
- ⚠️ Disk usage > 80%
- ⚠️ Memory usage > 90%

---

## 🔐 Important URLs & Credentials

### Production Services
| Service | URL/Access |
|---------|-----------|
| API | http://72.62.132.205:8000 |
| API Docs | http://72.62.132.205:8000/docs |
| n8n | https://n8n.srv996391.hstgr.cloud |
| VPS | ssh root@72.62.132.205 |

### Credentials
| System | Username | Password/Token |
|--------|----------|----------------|
| VPS | root | [Your SSH password] |
| n8n | frontendlabs.uk@gmail.com | 4rontEnd#labs |
| Database | insight_user | ChangeThisPassword123 |
| Slack Bot | - | [REDACTED - See .env file] |
| Slack User ID | - | U01K29DED53 |

---

## 📅 Scheduled Tasks

### Cron Jobs
| Schedule | Task | Command |
|----------|------|---------|
| Mon 9AM UTC | Weekly Brief | python scripts/weekly_run.py |
| Daily 2AM | Database Backup | /opt/strategic-insight/backup.sh |

### n8n Workflows
| Workflow | Trigger | Frequency |
|----------|---------|-----------|
| Gmail to Insight | Poll | Every 1 hour |
| Read.ai to Insight | Webhook | On meeting complete |

---

## 🆘 Emergency Contacts

**System Issues:**
1. Check logs: `docker-compose logs`
2. Restart services: `docker-compose restart`
3. Review troubleshooting guide

**VPS Down:**
- Contact Hostinger support via hosting panel

**Data Loss:**
- Stop writes: `docker-compose stop api`
- Restore from backup (see above)
- Contact system administrator

---

## 📱 Mobile Quick Check

**From phone browser:**
```
Health: http://72.62.132.205:8000/health
Stats: http://72.62.132.205:8000/stats
```

**Expected:**
```json
{"status":"healthy","timestamp":"2025-..."}
{"total_events":100,"email_events":60,"meeting_events":40}
```

---

## 🎯 Weekly Brief Schedule

**When:** Every Monday at 9:00 AM UTC

**Time Zones:**
- 9:00 AM UTC
- 4:00 AM EST
- 1:00 AM PST
- 10:00 AM CET

**Delivery:** Slack DM to U01K29DED53

**What to Check:**
1. Brief arrived in Slack
2. Date range is correct (last 7 days)
3. Event count seems reasonable
4. Insights are meaningful

---

## 📞 Support Escalation

**Level 1: Self-Service**
- Check this guide
- Review logs
- Restart services

**Level 2: Documentation**
- HANDOVER_OPERATIONS_GUIDE.md
- VPS_DEPLOYMENT_GUIDE.md
- DEPLOYMENT_SUMMARY.md

**Level 3: External Support**
- Hostinger VPS support
- n8n community forums
- Slack API documentation

---

## ✅ Daily Checklist (2 minutes)

```bash
# 1. SSH to VPS
ssh root@72.62.132.205

# 2. Check all services
cd /opt/strategic-insight && docker-compose ps

# 3. Quick health check
curl http://localhost:8000/health && curl http://localhost:8000/stats

# 4. Check for errors
docker-compose logs --tail=50 | grep -i error

# 5. Done!
exit
```

---

**Print this page and keep it handy! 🖨️**

**Last Updated:** December 30, 2025
**Version:** 1.0
