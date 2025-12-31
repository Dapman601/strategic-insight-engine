# Setup Guide - Weekly Strategic Insight Engine

Complete step-by-step setup instructions for deployment.

## Table of Contents

1. [Server Setup](#server-setup)
2. [Database Configuration](#database-configuration)
3. [Application Deployment](#application-deployment)
4. [n8n Integration](#n8n-integration)
5. [Slack Configuration](#slack-configuration)
6. [LLM API Setup](#llm-api-setup)
7. [Testing & Verification](#testing--verification)

---

## Server Setup

### Hostinger VPS Requirements

- **OS**: Ubuntu 20.04+ or Debian 11+
- **RAM**: Minimum 2GB (4GB recommended)
- **Storage**: 20GB+
- **CPU**: 2+ cores

### Initial Server Configuration

```bash
# Update system
sudo apt update && sudo apt upgrade -y

# Install essential tools
sudo apt install -y git curl wget nano htop

# Install Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh
sudo usermod -aG docker $USER

# Install Docker Compose
sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose

# Verify installations
docker --version
docker-compose --version
```

---

## Database Configuration

### PostgreSQL with pgvector

The Docker setup includes PostgreSQL automatically. For manual setup:

```bash
# Add PostgreSQL repository
sudo apt install -y postgresql-common
sudo /usr/share/postgresql-common/pgdg/apt.postgresql.org.sh

# Install PostgreSQL 16
sudo apt install -y postgresql-16 postgresql-16-pgvector

# Start PostgreSQL
sudo systemctl enable postgresql
sudo systemctl start postgresql

# Create database and user
sudo -u postgres psql << EOF
CREATE DATABASE strategic_insight;
CREATE USER insight_user WITH ENCRYPTED PASSWORD 'your_secure_password';
GRANT ALL PRIVILEGES ON DATABASE strategic_insight TO insight_user;
\c strategic_insight
CREATE EXTENSION vector;
EOF

# Apply schema
psql -U insight_user -d strategic_insight -f schema.sql
```

---

## Application Deployment

### Option 1: Docker Deployment (Recommended)

```bash
# Clone repository
cd /opt
sudo git clone <your-repo-url> strategic-insight
cd strategic-insight

# Configure environment
sudo cp .env.production .env
sudo nano .env  # Edit with your credentials

# Deploy
sudo chmod +x deployment/deploy_hostinger.sh
sudo deployment/deploy_hostinger.sh

# Setup systemd for auto-restart
sudo chmod +x deployment/setup_systemd.sh
sudo deployment/setup_systemd.sh
```

### Option 2: Manual Python Deployment

```bash
# Create app directory
sudo mkdir -p /opt/strategic-insight
cd /opt/strategic-insight

# Create virtual environment
python3.11 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Configure environment
cp .env.example .env
nano .env  # Edit with your credentials

# Start API
python api/main.py &

# Setup cron for weekly processing
crontab -e
# Add: 0 9 * * 1 cd /opt/strategic-insight && /opt/strategic-insight/venv/bin/python scripts/weekly_run.py >> /opt/strategic-insight/logs/weekly.log 2>&1
```

### Verify Deployment

```bash
# Check Docker containers
docker ps

# Test API
curl http://localhost:8000/health

# View logs
docker-compose logs -f api
```

---

## n8n Integration

### n8n is Already Running

Your n8n instance: https://n8n.srv996391.hstgr.cloud

**Credentials**:
- Email: frontendlabs.uk@gmail.com
- Password: 4rontEnd#labs

### Import Workflows

#### Automatic Import

```bash
python deployment/n8n_setup.py
```

#### Manual Import

1. **Login to n8n**: https://n8n.srv996391.hstgr.cloud

2. **Import Gmail Workflow**:
   - Click "Workflows" → "Import from File"
   - Select `n8n_workflows/gmail_to_insight_engine.json`
   - Click "Import"

3. **Import Read.ai Workflow**:
   - Click "Workflows" → "Import from File"
   - Select `n8n_workflows/readai_to_insight_engine.json`
   - Click "Import"

4. **Configure Gmail OAuth**:
   - In Gmail Trigger node, click "Create New Credential"
   - Select "OAuth2"
   - Follow Google OAuth setup:
     - Go to https://console.cloud.google.com
     - Create OAuth 2.0 credentials
     - Add authorized redirect URI: `https://n8n.srv996391.hstgr.cloud/rest/oauth2-credential/callback`
     - Copy Client ID and Secret to n8n
   - Authenticate with your Gmail account

5. **Update API Endpoints**:
   - In "POST to Insight API" nodes
   - Update URL to: `http://your-server-ip:8000/ingest/email`
   - Or use domain if configured

6. **Activate Workflows**:
   - Toggle "Active" switch on each workflow
   - Gmail workflow will poll every hour
   - Read.ai webhook will be available at: `https://n8n.srv996391.hstgr.cloud/webhook/readai-webhook`

### Configure Read.ai Webhook

1. Log in to Read.ai
2. Go to Settings → Integrations → Webhooks
3. Add webhook URL: `https://n8n.srv996391.hstgr.cloud/webhook/readai-webhook`
4. Select events: "Meeting Completed"
5. Save

---

## Slack Configuration

### Create Slack Bot

1. **Create Slack App**:
   - Go to https://api.slack.com/apps
   - Click "Create New App" → "From scratch"
   - Name: "Strategic Insight Bot"
   - Select your workspace

2. **Configure Bot Permissions**:
   - Go to "OAuth & Permissions"
   - Add scopes:
     - `chat:write`
     - `users:read`
     - `im:write`
   - Click "Install to Workspace"
   - Copy "Bot User OAuth Token" (starts with `xoxb-`)

3. **Get Your Slack User ID**:
   - Go to your Slack profile
   - Click "..." → "Copy member ID"
   - Or use: https://api.slack.com/methods/users.list/test

4. **Add to .env**:
```bash
SLACK_BOT_TOKEN=xoxb-your-token-here
SLACK_USER_ID=U01234567
```

5. **Restart Application**:
```bash
docker-compose restart api weekly-processor
```

### Test Slack Integration

```bash
# Run a test weekly processing
docker exec insight-processor python scripts/weekly_run.py
```

You should receive a DM from the bot with the weekly brief.

---

## LLM API Setup

### Option 1: Grok API (Recommended)

1. **Get Grok API Key**:
   - Visit https://x.ai
   - Sign up for API access
   - Copy API key

2. **Add to .env**:
```bash
GROK_API_KEY=your-grok-key-here
GROK_API_URL=https://api.x.ai/v1
GROK_MODEL=grok-beta
```

### Option 2: OpenAI API (Fallback)

1. **Get OpenAI API Key**:
   - Visit https://platform.openai.com
   - Create API key

2. **Add to .env**:
```bash
OPENAI_API_KEY=sk-your-key-here
OPENAI_MODEL=gpt-4o
```

### Option 3: No LLM (Rule-Based Only)

The system works fully without LLM enhancement. Simply omit the API keys:

```bash
GROK_API_KEY=
OPENAI_API_KEY=
```

Reports will use rule-based findings only.

---

## Testing & Verification

### 1. Test API Ingestion

```bash
# Start API if not running
python api/main.py

# In another terminal, run demo ingestion
python scripts/ingest_demo.py

# Check stats
curl http://localhost:8000/stats
```

Expected output:
```json
{
  "total_events": 80,
  "email_events": 50,
  "meeting_events": 30
}
```

### 2. Test Weekly Processing

```bash
# Run weekly processing
python scripts/weekly_run.py

# Or with Docker
docker exec insight-processor python scripts/weekly_run.py
```

Expected output:
- Processing logs showing clustering, metrics, findings
- Markdown brief printed to console
- Watchlist items
- Slack DM received (if configured)

### 3. Test n8n Workflows

#### Gmail Workflow:
1. Send yourself a test email
2. Wait for n8n to poll (every hour) or manually execute
3. Check n8n execution log
4. Verify event in database:
```bash
docker exec insight-postgres psql -U insight_user -d strategic_insight -c "SELECT COUNT(*) FROM core_events WHERE source='email';"
```

#### Read.ai Workflow:
1. Complete a test meeting with Read.ai
2. Check n8n webhook execution
3. Verify event in database:
```bash
docker exec insight-postgres psql -U insight_user -d strategic_insight -c "SELECT COUNT(*) FROM core_events WHERE source='meeting';"
```

### 4. Verify Weekly Cron Job

```bash
# Check cron is running (Docker)
docker exec insight-processor ps aux | grep cron

# View cron schedule
docker exec insight-processor crontab -l

# Check weekly.log
docker exec insight-processor tail -f /app/logs/weekly.log
```

---

## Firewall Configuration

### Allow Required Ports

```bash
# Docker services
sudo ufw allow 8000/tcp  # API
sudo ufw allow 5432/tcp  # PostgreSQL (only if external access needed)

# If using reverse proxy
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp

# Enable firewall
sudo ufw enable
```

### Setup Reverse Proxy (Optional)

For HTTPS and domain access:

```bash
# Install nginx
sudo apt install -y nginx certbot python3-certbot-nginx

# Create nginx config
sudo nano /etc/nginx/sites-available/insight-api

# Add:
server {
    listen 80;
    server_name api.yourdomain.com;

    location / {
        proxy_pass http://localhost:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}

# Enable site
sudo ln -s /etc/nginx/sites-available/insight-api /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx

# Get SSL certificate
sudo certbot --nginx -d api.yourdomain.com
```

---

## Monitoring & Maintenance

### Check Service Status

```bash
# Docker
docker-compose ps
docker stats

# Systemd
sudo systemctl status strategic-insight

# View logs
docker-compose logs -f
tail -f logs/weekly.log
```

### Database Maintenance

```bash
# Backup database
docker exec insight-postgres pg_dump -U insight_user strategic_insight > backup_$(date +%Y%m%d).sql

# Cleanup old events (optional)
docker exec insight-postgres psql -U insight_user -d strategic_insight -c "DELETE FROM core_events WHERE timestamp < NOW() - INTERVAL '180 days';"
```

### Resource Monitoring

```bash
# Disk usage
df -h

# Memory usage
free -h

# Docker resource usage
docker stats
```

---

## Troubleshooting

### API Not Responding

```bash
# Check if container is running
docker ps | grep insight-api

# View API logs
docker logs insight-api

# Restart API
docker-compose restart api
```

### Database Connection Issues

```bash
# Check PostgreSQL is running
docker ps | grep postgres

# Test connection
docker exec insight-postgres psql -U insight_user -d strategic_insight -c "SELECT 1;"

# Check connection string in .env
cat .env | grep DATABASE_URL
```

### n8n Workflow Failures

1. Check n8n execution logs
2. Verify API endpoint URL is correct
3. Test API manually: `curl -X POST http://your-api/ingest/email -H "Content-Type: application/json" -d @test_event.json`
4. Check n8n credentials are valid

### Slack Not Receiving Messages

1. Verify bot token: `cat .env | grep SLACK_BOT_TOKEN`
2. Check bot permissions in Slack app settings
3. Test user ID: https://api.slack.com/methods/users.list/test
4. View processor logs: `docker logs insight-processor`

---

## Next Steps

After successful setup:

1. **Monitor First Week**: Watch logs during first weekly run
2. **Tune Rules**: Adjust thresholds in `src/config.py` based on findings
3. **Review Reports**: Evaluate brief quality and adjust prompts if needed
4. **Scale**: Consider adding more data sources
5. **Backup**: Setup automated database backups
6. **Alerts**: Configure monitoring alerts for failures

---

## Support

For issues or questions:
1. Check logs: `docker-compose logs -f`
2. Review this guide
3. Consult main README.md
4. Check SOW documentation

---

**Setup Complete!** Your Weekly Strategic Insight Engine is now running.
