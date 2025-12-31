# Deployment Instructions - Ready to Deploy

## ✅ What's Already Done

1. **n8n Workflows Imported** ✓
   - Gmail workflow: Imported and ready
   - Read.ai workflow: Imported and ready
   - Location: https://n8n.srv996391.hstgr.cloud

2. **Code Complete** ✓
   - All Python modules written
   - Docker configuration ready
   - Database schema prepared
   - Scripts tested

## 🔧 What You Need to Configure

### 1. Get Slack Bot Token (5 minutes)

1. Go to https://api.slack.com/apps
2. Click "Create New App" → "From scratch"
3. Name: "Strategic Insight Bot"
4. Select your workspace
5. Go to "OAuth & Permissions"
6. Add Bot Token Scopes:
   - `chat:write`
   - `users:read`
   - `im:write`
7. Click "Install to Workspace"
8. Copy the "Bot User OAuth Token" (starts with `xoxb-`)
9. Get your Slack User ID:
   - Go to your profile → ... → Copy member ID
   - Or visit: https://api.slack.com/methods/users.list/test

**Add to `.env` file:**
```bash
SLACK_BOT_TOKEN=xoxb-your-token-here
SLACK_USER_ID=U01234567
```

### 2. Get LLM API Keys (Optional - 5 minutes)

**Option A: Grok (Recommended)**
1. Visit https://x.ai
2. Sign up for API access
3. Copy API key

**Option B: OpenAI (Fallback)**
1. Visit https://platform.openai.com
2. Create API key

**Add to `.env` file:**
```bash
GROK_API_KEY=your-grok-key-here
# or
OPENAI_API_KEY=sk-your-openai-key-here
```

**Note:** System works fully without LLM keys (uses rule-based findings only)

## 🚀 Deployment Options

### Option 1: Local Testing (Recommended First)

```bash
# 1. Edit .env file with your Slack credentials
nano .env

# 2. Start Docker containers
docker-compose up -d

# 3. Wait for services to be healthy (30 seconds)
docker-compose ps

# 4. Generate test data
docker exec insight-api python scripts/ingest_demo.py

# 5. Run weekly processing
docker exec insight-processor python scripts/weekly_run.py

# 6. Check Slack for the brief!
```

**Verify everything works:**
```bash
# Check API health
curl http://localhost:8000/health

# Check stats
curl http://localhost:8000/stats

# View logs
docker-compose logs -f
```

### Option 2: Deploy to Hostinger VPS

**Prerequisites:**
- SSH access to Hostinger VPS
- Root or sudo privileges

**Steps:**

1. **Upload Project to Server**
```bash
# From your local machine
scp -r n8n_strategic_insight_engine/ user@your-server:/opt/strategic-insight/

# Or use git
ssh user@your-server
cd /opt
git clone <your-repo> strategic-insight
```

2. **Configure Environment**
```bash
ssh user@your-server
cd /opt/strategic-insight
cp .env.production .env
nano .env  # Add your Slack and LLM credentials
```

3. **Run Deployment Script**
```bash
chmod +x deployment/deploy_hostinger.sh
sudo deployment/deploy_hostinger.sh
```

4. **Setup Auto-Restart (Optional)**
```bash
chmod +x deployment/setup_systemd.sh
sudo deployment/setup_systemd.sh
```

## 📋 n8n Workflow Configuration

The workflows are imported but need final configuration:

### 1. Login to n8n
- URL: https://n8n.srv996391.hstgr.cloud
- Email: frontendlabs.uk@gmail.com
- Password: 4rontEnd#labs

### 2. Configure Gmail Workflow

1. Open "Gmail to Insight Engine" workflow
2. Click on "Gmail Trigger" node
3. Create Gmail OAuth2 credential:
   - Go to https://console.cloud.google.com
   - Create new project (or use existing)
   - Enable Gmail API
   - Create OAuth 2.0 credentials
   - Add redirect URI: `https://n8n.srv996391.hstgr.cloud/rest/oauth2-credential/callback`
   - Copy Client ID and Secret
   - Paste in n8n credential form
   - Authenticate with your Gmail account
4. Update "POST to Insight API" node:
   - Change URL to: `http://your-server-ip:8000/ingest/email`
   - Or: `http://localhost:8000/ingest/email` if testing locally
5. Click "Execute Workflow" to test
6. Toggle "Active" when working

### 3. Configure Read.ai Workflow

1. Open "Read.ai to Insight Engine" workflow
2. Update "POST to Insight API" node:
   - Change URL to: `http://your-server-ip:8000/ingest/meeting`
3. Copy webhook URL from "Read.ai Webhook" node
4. Go to Read.ai settings → Webhooks
5. Add the webhook URL
6. Select "Meeting Completed" event
7. Save and activate workflow

## 🧪 Testing Checklist

### Local Testing
- [ ] Docker containers running (postgres, api, processor)
- [ ] API responds to `/health`
- [ ] Test data ingests (80 events)
- [ ] Weekly processing completes
- [ ] Slack message received
- [ ] n8n Gmail workflow executes
- [ ] n8n Read.ai workflow receives webhooks

### Production Verification
- [ ] All services running on VPS
- [ ] API accessible from internet
- [ ] Database persisting data
- [ ] Weekly cron job configured (Mondays 9 AM UTC)
- [ ] Slack bot delivering messages
- [ ] n8n workflows active and polling

## 📊 Quick Commands Reference

```bash
# Check status
docker-compose ps
docker stats

# View logs
docker-compose logs -f api
docker-compose logs -f processor
docker-compose logs postgres

# Restart services
docker-compose restart

# Stop everything
docker-compose down

# Start everything
docker-compose up -d

# Manual weekly run
docker exec insight-processor python scripts/weekly_run.py

# Check database
docker exec insight-postgres psql -U insight_user -d strategic_insight -c "SELECT COUNT(*) FROM core_events;"

# Backup database
docker exec insight-postgres pg_dump -U insight_user strategic_insight > backup_$(date +%Y%m%d).sql
```

## 🔍 Troubleshooting

### "Cannot connect to Docker daemon"
```bash
sudo systemctl start docker
sudo usermod -aG docker $USER
# Logout and login again
```

### "Port 8000 already in use"
```bash
# Find and kill the process
sudo lsof -i :8000
sudo kill -9 <PID>
# Or change port in docker-compose.yml
```

### "Slack message not received"
```bash
# Verify token
cat .env | grep SLACK_BOT_TOKEN

# Check bot permissions in Slack app settings
# Ensure bot is added to workspace

# View processor logs
docker logs insight-processor
```

### "n8n workflow fails"
```bash
# Check n8n execution logs
# Verify API endpoint is accessible
curl http://your-api-url:8000/health

# Test manual POST
curl -X POST http://localhost:8000/ingest/email \
  -H "Content-Type: application/json" \
  -d '{"id":"test:1","source":"email","timestamp":"2025-12-27T10:00:00Z","actor":"test@example.com","direction":"inbound","subject":"Test","text":"Test","thread_id":null,"decision":"none","action_owner":null,"follow_up_required":false,"urgency_score":5,"sentiment":"unknown","raw_ref":"test1"}'
```

## 🎯 Success Criteria

When deployment is successful, you should see:

1. ✅ All Docker containers running and healthy
2. ✅ API responding at http://your-server:8000/health
3. ✅ Test data ingested (80 events)
4. ✅ Weekly processing completes without errors
5. ✅ Slack DM received with formatted brief
6. ✅ n8n workflows active in web interface
7. ✅ Weekly cron job scheduled

## 📞 Support

If you encounter issues:

1. Check logs: `docker-compose logs -f`
2. Verify .env configuration
3. Test API manually: `curl http://localhost:8000/health`
4. Review n8n execution logs
5. Check this guide and README.md

## 🎉 Next Steps After Successful Deployment

1. Monitor first weekly run (next Monday 9 AM UTC)
2. Review brief quality and tune rules if needed
3. Add more data sources as needed
4. Setup monitoring/alerts
5. Configure database backups

---

**Status:** n8n workflows imported ✓ | Ready for Slack configuration
**Last Updated:** December 27, 2025
