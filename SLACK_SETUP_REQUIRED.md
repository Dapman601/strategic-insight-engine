# ⚠️ Slack Bot Scopes Required

## Current Status

✅ **Credentials Updated:**
- Bot Token: `[REDACTED - See .env file]`
- User ID: `U01K29DED53`
- Bot Name: `strategic_insight_gen`
- Team: `Frontendlabs`

❌ **Error:** `missing_scope` - Bot lacks required permissions

---

## Required Scopes

The Strategic Insight Engine bot needs these **Bot Token Scopes**:

### **Minimum Required:**
- `chat:write` - Send messages to channels and DMs
- `im:write` - Open and send direct messages
- `channels:read` - View basic channel info (optional)
- `users:read` - View user information (optional)

---

## How to Add Scopes

### **Step 1: Go to Slack App Settings**
1. Visit: https://api.slack.com/apps
2. Select your app: **strategic_insight_gen**
3. Or use the App ID to find it

### **Step 2: Add Bot Token Scopes**
1. In the left sidebar, click **"OAuth & Permissions"**
2. Scroll to **"Scopes"** section
3. Under **"Bot Token Scopes"**, click **"Add an OAuth Scope"**
4. Add these scopes:
   - `chat:write`
   - `im:write`

### **Step 3: Reinstall App to Workspace**
1. After adding scopes, Slack will show a yellow banner: **"Please reinstall your app"**
2. Click **"Reinstall App"** button
3. Click **"Allow"** to grant the new permissions
4. **IMPORTANT:** Copy the new Bot Token that's generated
5. Replace the token in `.env` if it changed

### **Step 4: Update Token (if changed)**
If you got a new token after reinstalling:

**On VPS:**
```bash
ssh root@72.62.132.205
cd /opt/strategic-insight
nano .env
# Update SLACK_BOT_TOKEN with new token
# Save and exit

docker compose restart weekly-processor api
```

**Or use this command:**
```bash
ssh root@72.62.132.205 "cd /opt/strategic-insight && sed -i 's/SLACK_BOT_TOKEN=.*/SLACK_BOT_TOKEN=NEW_TOKEN_HERE/' .env && docker compose restart weekly-processor api"
```

---

## Test After Setup

Run this test on VPS to verify it works:

```bash
ssh root@72.62.132.205 "cd /opt/strategic-insight && docker exec insight-processor python -c \"
from slack_sdk import WebClient

client = WebClient(token='YOUR_BOT_TOKEN')
response = client.conversations_open(users='U01K29DED53')
channel_id = response['channel']['id']
client.chat_postMessage(channel=channel_id, text='✅ Scopes configured correctly!')
print('[SUCCESS] Message sent!')
\""
```

---

## Current Bot Scopes

To see what scopes are currently configured:
1. Go to https://api.slack.com/apps
2. Select your app
3. Click **"OAuth & Permissions"**
4. Check the **"Bot Token Scopes"** section

---

## What the Bot Does

The bot needs these permissions to:
1. **Open DM channel** with user (requires `im:write`)
2. **Send weekly brief** as direct message (requires `chat:write`)
3. **Format messages** with markdown

---

## After Adding Scopes

Once scopes are added and app is reinstalled, test again:

```bash
ssh root@72.62.132.205
cd /opt/strategic-insight
docker exec insight-processor python scripts/weekly_run.py
```

This will send a test weekly brief to your Slack!

---

**Status:** ⏳ WAITING FOR SLACK SCOPES CONFIGURATION
**Next Step:** Add `chat:write` and `im:write` scopes to your Slack app
