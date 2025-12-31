# 🚀 HOSTINGER VPS DEPLOYMENT GUIDE
## Strategic Insight Engine - Production Deployment

---

## 📋 PRE-DEPLOYMENT CHECKLIST

### ✅ What You Need

**VPS Information:**
- **Server:** srv996391.hstgr.cloud
- **SSH Access:** Required (username/password or SSH key)
- **OS:** Linux (Ubuntu/Debian recommended)
- **Ports Needed:** 8000 (API), 5432 (PostgreSQL - internal)

**Credentials Ready:**
- [x] n8n: frontendlabs.uk@gmail.com / 4rontEnd#labs
- [x] Slack: Bot token and User ID configured
- [ ] Hostinger VPS SSH credentials

**Files Ready for Upload:**
- [x] docker-compose.yml
- [x] docker/Dockerfile
- [x] .env (with production credentials)
- [x] src/ directory
- [x] api/ directory
- [x] scripts/ directory
- [x] schema.sql
- [x] requirements.txt

---

## 🎯 DEPLOYMENT STRATEGY

We'll deploy the Strategic Insight Engine to the same Hostinger VPS where n8n is running:

```
srv996391.hstgr.cloud
├── n8n (already running)
│   └── Port: 443 (HTTPS)
└── Strategic Insight API (to deploy)
    └── Port: 8000 (HTTP)
```

**Benefits:**
1. Same server = Internal network communication possible
2. No external dependencies
3. Stable, permanent URLs
4. Better security

---

## 📝 STEP-BY-STEP DEPLOYMENT

### **STEP 1: Prepare Local Files (5 minutes)**

#### 1.1 Create Deployment Package

```bash
cd C:\Users\DELL\Documents\n8n_strategic_insight_engine

# Create deployment directory
mkdir deployment_package
cd deployment_package

# Copy essential files
cp ../docker-compose.yml .
cp ../requirements.txt .
cp ../.env .
cp -r ../docker .
cp -r ../src .
cp -r ../api .
cp -r ../scripts .
cp ../schema.sql .
cp -r ../n8n_workflows .

# Create archive for upload
tar -czf strategic-insight.tar.gz *
```

#### 1.2 Verify .env File

Make sure `.env` has these critical settings:

```bash
# Check current .env
cat .env | grep -E "SLACK|DATABASE|N8N"
```

**Required settings:**
```env
# Database (will use Docker internal network)
DATABASE_URL=postgresql://insight_user:ChangeThisPassword123@postgres:5432/strategic_insight
DB_PASSWORD=ChangeThisPassword123

# Slack (already configured)
SLACK_BOT_TOKEN=[REDACTED - See .env file]
SLACK_USER_ID=U0A5P9JJYGN

# n8n (already configured)
N8N_URL=https://n8n.srv996391.hstgr.cloud
N8N_EMAIL=frontendlabs.uk@gmail.com
N8N_PASSWORD=4rontEnd#labs
```

---

### **STEP 2: Connect to VPS (2 minutes)**

#### Option A: SSH with Password

```bash
ssh root@srv996391.hstgr.cloud
# Enter password when prompted
```

#### Option B: SSH with Key (if configured)

```bash
ssh -i ~/.ssh/hostinger_key root@srv996391.hstgr.cloud
```

#### 2.1 Verify Server Access

Once connected, check the environment:

```bash
# Check OS version
cat /etc/os-release

# Check if Docker is installed
docker --version
docker-compose --version

# Check available disk space
df -h

# Check running containers
docker ps

# Check if n8n is running
docker ps | grep n8n
```

---

### **STEP 3: Install Prerequisites (10 minutes)**

If Docker is not installed:

```bash
# Update system
apt update && apt upgrade -y

# Install Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sh get-docker.sh
rm get-docker.sh

# Start Docker
systemctl enable docker
systemctl start docker

# Install Docker Compose
curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
chmod +x /usr/local/bin/docker-compose

# Verify installation
docker --version
docker-compose --version
```

---

### **STEP 4: Upload Application Files (5 minutes)**

#### Option A: Using SCP (From Windows)

```powershell
# From Windows PowerShell or Command Prompt
scp C:\Users\DELL\Documents\n8n_strategic_insight_engine\deployment_package\strategic-insight.tar.gz root@srv996391.hstgr.cloud:/opt/
```

#### Option B: Using WinSCP / FileZilla

1. Download WinSCP: https://winscp.net/
2. Connect to srv996391.hstgr.cloud
3. Navigate to `/opt/`
4. Upload `strategic-insight.tar.gz`

#### Option C: Manual File Transfer

If SCP doesn't work, we can create files directly on the server using `cat` or `nano`.

---

### **STEP 5: Deploy on VPS (15 minutes)**

Back on the VPS (via SSH):

```bash
# Navigate to deployment directory
cd /opt
mkdir -p strategic-insight
cd strategic-insight

# If you uploaded the tar.gz:
tar -xzf ../strategic-insight.tar.gz

# Or if transferring manually, we'll do it step by step

# Create logs directory
mkdir -p logs

# Set proper permissions
chmod +x deployment/deploy_hostinger.sh
```

#### 5.1 Verify Files

```bash
# Check all files are present
ls -la
# Should see: docker-compose.yml, .env, src/, api/, scripts/, etc.

# Verify .env configuration
cat .env | head -20
```

#### 5.2 Build and Start Containers

```bash
# Build Docker images (this will take 5-10 minutes)
docker-compose build --no-cache

# Start containers
docker-compose up -d

# Check status
docker-compose ps
```

**Expected output:**
```
NAME                STATUS              PORTS
insight-postgres    Up (healthy)        5432/tcp
insight-api         Up (healthy)        0.0.0.0:8000->8000/tcp
insight-processor   Up                  -
```

---

### **STEP 6: Verify Deployment (5 minutes)**

#### 6.1 Check Container Health

```bash
# View logs
docker-compose logs --tail=50

# Check API health
curl http://localhost:8000/health
# Expected: {"status":"healthy","timestamp":"..."}

# Check stats
curl http://localhost:8000/stats
# Expected: {"total_events":0,"email_events":0,"meeting_events":0}
```

#### 6.2 Test from External Network

From your local machine (Windows):

```powershell
# Test external access
curl http://srv996391.hstgr.cloud:8000/health

# Or in browser:
# http://srv996391.hstgr.cloud:8000/health
```

---

### **STEP 7: Configure Firewall (5 minutes)**

Ensure port 8000 is accessible:

```bash
# Check if UFW is active
ufw status

# If UFW is active, allow port 8000
ufw allow 8000/tcp
ufw reload

# Or if using iptables
iptables -A INPUT -p tcp --dport 8000 -j ACCEPT
```

**For Hostinger Control Panel:**
1. Log into Hostinger control panel
2. Navigate to VPS → Firewall
3. Add rule: Allow TCP port 8000

---

### **STEP 8: Configure Nginx Reverse Proxy (Optional - 10 minutes)**

For production, it's better to use HTTPS. Set up Nginx as reverse proxy:

#### 8.1 Install Nginx

```bash
apt install -y nginx certbot python3-certbot-nginx
```

#### 8.2 Create Nginx Configuration

```bash
cat > /etc/nginx/sites-available/insight-api << 'EOF'
server {
    listen 80;
    server_name srv996391.hstgr.cloud;

    location /api/ {
        proxy_pass http://localhost:8000/;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_cache_bypass $http_upgrade;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
EOF

# Enable site
ln -s /etc/nginx/sites-available/insight-api /etc/nginx/sites-enabled/

# Test configuration
nginx -t

# Restart Nginx
systemctl restart nginx
```

#### 8.3 Add SSL Certificate (Recommended)

```bash
# Get free SSL from Let's Encrypt
certbot --nginx -d srv996391.hstgr.cloud

# Follow prompts to configure HTTPS
```

**After SSL:**
- API accessible at: `https://srv996391.hstgr.cloud/api/`
- Health check: `https://srv996391.hstgr.cloud/api/health`

---

### **STEP 9: Update n8n Workflows (10 minutes)**

#### 9.1 Determine API URL

**Option A: Direct Port Access (No Nginx)**
```
http://srv996391.hstgr.cloud:8000
```

**Option B: Nginx Reverse Proxy (With SSL)**
```
https://srv996391.hstgr.cloud/api
```

**Option C: Internal Docker Network (Same VPS)**
```
http://insight-api:8000
```

#### 9.2 Update Workflows via n8n UI

1. Go to: https://n8n.srv996391.hstgr.cloud
2. Login: frontendlabs.uk@gmail.com / 4rontEnd#labs
3. Open: "Gmail to Insight Engine"
4. Click: "POST to Insight API" node
5. Update URL to:
   ```
   http://insight-api:8000/ingest/email
   ```
   OR
   ```
   https://srv996391.hstgr.cloud/api/ingest/email
   ```
6. Save workflow
7. Repeat for "Read.ai to Insight Engine":
   ```
   http://insight-api:8000/ingest/meeting
   ```
8. Also update Gmail credential to "Miva" (ID: dDUEFsj2S2JKsQDb)

---

### **STEP 10: Test End-to-End (10 minutes)**

#### 10.1 Test Direct API Ingestion

From VPS:

```bash
# Test email ingestion
curl -X POST http://localhost:8000/ingest/email \
  -H "Content-Type: application/json" \
  -d '{
    "id": "test-vps-001",
    "source": "email",
    "timestamp": "2025-12-28T20:00:00Z",
    "actor": "test@example.com",
    "direction": "inbound",
    "subject": "VPS Deployment Test",
    "text": "Testing from VPS deployment",
    "thread_id": null,
    "decision": "none",
    "action_owner": null,
    "follow_up_required": false,
    "urgency_score": 5,
    "sentiment": "unknown",
    "raw_ref": "vps-test-001"
  }'

# Check stats
curl http://localhost:8000/stats
# Should show 1 event
```

#### 10.2 Test n8n Workflow

1. In n8n UI, open "Gmail to Insight Engine"
2. Click "Execute Workflow" button
3. Check execution log for success/errors
4. Verify event appears in database:

```bash
docker exec -it insight-postgres psql -U insight_user -d strategic_insight -c "SELECT COUNT(*) FROM core_events;"
```

#### 10.3 Test Weekly Processing

```bash
# Generate demo data
docker exec insight-processor python scripts/ingest_demo.py

# Run weekly processing
docker exec insight-processor python scripts/weekly_run.py

# Check if brief was sent to Slack
# You should receive a message in Slack!
```

---

### **STEP 11: Configure Read.ai Webhook (5 minutes)**

Now that the API is publicly accessible:

1. Log into Read.ai
2. Go to Settings → Integrations → Webhooks
3. Add webhook URL:
   - If using Nginx: `https://srv996391.hstgr.cloud/api/webhook/readai-webhook`
   - If direct: `http://srv996391.hstgr.cloud:8000/webhook/readai-webhook`
4. Select triggers: Meeting completed, Transcript ready
5. Save

---

### **STEP 12: Monitor and Maintain**

#### Set Up Log Rotation

```bash
# Create log rotation config
cat > /etc/logrotate.d/strategic-insight << 'EOF'
/opt/strategic-insight/logs/*.log {
    daily
    rotate 7
    compress
    delaycompress
    missingok
    notifempty
}
EOF
```

#### Monitoring Commands

```bash
# View live logs
cd /opt/strategic-insight
docker-compose logs -f

# Check container status
docker-compose ps

# Restart containers
docker-compose restart

# View database size
docker exec insight-postgres psql -U insight_user -d strategic_insight -c "SELECT pg_size_pretty(pg_database_size('strategic_insight'));"

# Check weekly processing logs
docker exec insight-processor cat /app/logs/weekly.log
```

---

## 🎯 QUICK REFERENCE

### **Useful URLs**

| Service | URL |
|---------|-----|
| **API Health** | http://srv996391.hstgr.cloud:8000/health |
| **API Stats** | http://srv996391.hstgr.cloud:8000/stats |
| **n8n** | https://n8n.srv996391.hstgr.cloud |
| **API Docs** | http://srv996391.hstgr.cloud:8000/docs |

### **Useful Commands**

```bash
# SSH to VPS
ssh root@srv996391.hstgr.cloud

# Navigate to app
cd /opt/strategic-insight

# View status
docker-compose ps

# View logs
docker-compose logs -f api
docker-compose logs -f processor

# Restart services
docker-compose restart

# Stop services
docker-compose down

# Start services
docker-compose up -d

# Check database
docker exec -it insight-postgres psql -U insight_user -d strategic_insight

# Manual weekly run
docker exec insight-processor python scripts/weekly_run.py

# Check cron
docker exec insight-processor crontab -l
```

---

## 🚨 TROUBLESHOOTING

### **Port 8000 Not Accessible**

```bash
# Check if API is running
docker ps | grep insight-api

# Check port binding
netstat -tuln | grep 8000

# Check firewall
ufw status
iptables -L -n | grep 8000

# Check Hostinger firewall in control panel
```

### **Container Won't Start**

```bash
# Check logs
docker-compose logs api

# Rebuild
docker-compose down
docker-compose build --no-cache
docker-compose up -d
```

### **Database Connection Issues**

```bash
# Check PostgreSQL
docker-compose logs postgres

# Test connection
docker exec insight-api python -c "from src.database import engine; print('OK' if engine else 'FAIL')"
```

### **n8n Can't Reach API**

1. Check API is accessible externally:
   ```bash
   curl http://srv996391.hstgr.cloud:8000/health
   ```
2. If using internal network, ensure both containers on same network:
   ```bash
   docker network ls
   docker network inspect n8n_strategic_insight_engine_insight-network
   ```

---

## ✅ DEPLOYMENT CHECKLIST

- [ ] SSH access to VPS confirmed
- [ ] Docker installed on VPS
- [ ] Files uploaded to VPS
- [ ] `.env` file configured
- [ ] Docker containers built and running
- [ ] API health check passing
- [ ] Port 8000 accessible externally
- [ ] (Optional) Nginx reverse proxy configured
- [ ] (Optional) SSL certificate installed
- [ ] n8n workflow URLs updated
- [ ] Gmail credential fixed in n8n
- [ ] Read.ai webhook configured
- [ ] End-to-end test successful
- [ ] Slack message received

---

## 🎊 SUCCESS CRITERIA

Your deployment is successful when:

1. ✅ `curl http://srv996391.hstgr.cloud:8000/health` returns `{"status":"healthy"}`
2. ✅ n8n workflows execute without errors
3. ✅ Events appear in database
4. ✅ Weekly processing runs and sends Slack message
5. ✅ System runs automatically via cron

---

## 📞 NEXT STEPS AFTER DEPLOYMENT

1. **Send Test Email** to frontendlabs.uk@gmail.com
2. **Wait 1 hour** for n8n Gmail trigger to poll
3. **Check Database** for ingested event
4. **Have Meeting** with Read.ai recording
5. **Verify Webhook** receives meeting data
6. **Wait for Monday 9 AM UTC** for automatic weekly brief

---

*Deployment Guide Version 1.0*
*Last Updated: December 28, 2025*
