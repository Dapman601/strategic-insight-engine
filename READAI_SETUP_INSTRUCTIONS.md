# Read.ai Webhook Setup Instructions

**Status:** Webhook endpoint ready ✅
**Webhook URL:** `https://n8n.srv996391.hstgr.cloud/webhook/readai-webhook`

---

## 🎯 Quick Setup (5 Minutes)

### **Step 1: Log into Read.ai**
Go to: https://www.read.ai or https://app.read.ai

### **Step 2: Find Webhook Settings**

**Typical locations:**
- Settings → Integrations → Webhooks
- Workspace Settings → API & Webhooks
- Settings → API → Webhooks

### **Step 3: Add New Webhook**

Click **"Add Webhook"** or **"Create Webhook"**

### **Step 4: Enter Webhook Details**

**Webhook URL:** (Copy exactly)
```
https://n8n.srv996391.hstgr.cloud/webhook/readai-webhook
```

**Name:** `Strategic Insight Engine` (optional)

**Method:** `POST`

**Content Type:** `application/json`

### **Step 5: Select Events to Trigger**

Check these boxes:
- ✅ Meeting Completed
- ✅ Transcript Available
- ✅ Summary Generated
- ✅ Recording Ready (optional)

### **Step 6: Save**

Click **"Save"** or **"Create Webhook"**

---

## ✅ After Setup

### **Test with a Real Meeting**

1. **Have a meeting with Read.ai recording enabled**
   - Schedule a short test meeting (even 2-3 minutes)
   - Enable Read.ai bot to join
   - Say a few test phrases like:
     - "We decided to test the integration"
     - "This is high priority"
     - "Follow up required next week"

2. **Wait for Read.ai to process**
   - Processing typically takes 5-10 minutes after meeting ends
   - Read.ai will automatically send webhook when ready

3. **Verify ingestion**

Run this command to check if the meeting was captured:

```bash
ssh root@72.62.132.205 "docker exec insight-postgres psql -U insight_user -d strategic_insight -c \"SELECT id, subject, source, actor, timestamp FROM core_events WHERE source = 'meeting' AND id LIKE 'read_ai:%' AND id NOT LIKE 'read_ai:synthetic%' ORDER BY timestamp DESC LIMIT 5;\""
```

**Expected output:**
```
id              | subject                    | source  | actor              | timestamp
----------------|----------------------------|---------|--------------------|-----------
read_ai:abc123  | Your Meeting Title         | meeting | participant1, ...  | 2025-...
```

---

## 🔍 Troubleshooting

### **Meeting Not Showing Up?**

**1. Check n8n workflow is active:**
- Visit: https://n8n.srv996391.hstgr.cloud
- Login: frontendlabs.uk@gmail.com / 4rontEnd#labs
- Open: "Read.ai to Insight Engine"
- Verify: Toggle shows "Active"

**2. Check n8n execution logs:**
- In n8n UI, click "Executions" tab
- Look for recent webhook triggers
- Check for any errors

**3. Check Read.ai sent the webhook:**
- In Read.ai settings, webhooks usually show delivery history
- Look for recent deliveries with status 200

**4. Check API is accessible:**
```bash
curl http://72.62.132.205:8000/health
```
Should return: `{"status":"healthy"}`

**5. Check webhook URL is correct:**
Make sure you entered exactly:
```
https://n8n.srv996391.hstgr.cloud/webhook/readai-webhook
```

---

## 📊 What Gets Captured

The system will automatically extract from Read.ai meetings:

1. **Meeting metadata:**
   - Title
   - Duration
   - Participants
   - Timestamp

2. **Content analysis:**
   - Full transcript
   - AI-generated summary
   - Key decisions identified
   - Action items with owners

3. **Strategic signals:**
   - Decision keywords ("decided", "agreed", "will do")
   - Deferral patterns ("table this", "revisit", "defer")
   - Urgency indicators ("urgent", "critical", "asap")
   - Follow-up requirements

4. **Clustering:**
   - Meetings about similar topics get grouped
   - Recurring meeting patterns detected
   - Decision pressure identified

---

## 🎊 Success Indicators

You'll know it's working when:

1. ✅ Webhook configured in Read.ai shows "Active"
2. ✅ Meeting appears in database after Read.ai processes it
3. ✅ Next Monday's weekly brief includes meeting insights
4. ✅ Slack brief shows meeting-based decision pressure

---

## 📞 Need Help?

**Common Issues:**

| Problem | Solution |
|---------|----------|
| Can't find webhook settings | Contact Read.ai support - webhook feature may require specific plan |
| Webhook shows error | Verify URL is exactly: `https://n8n.srv996391.hstgr.cloud/webhook/readai-webhook` |
| Meeting not captured | Check n8n execution logs for errors |
| Wrong data extracted | Read.ai payload format may have changed - check n8n workflow |

---

## 🔗 Integration Flow

```
┌─────────────────┐
│   Read.ai       │
│   Meeting End   │
└────────┬────────┘
         │
         │ (5-10 min processing)
         │
         v
┌─────────────────┐
│  Read.ai sends  │
│  webhook POST   │
└────────┬────────┘
         │
         v
┌─────────────────────────────────────┐
│  n8n Workflow:                      │
│  https://n8n.srv996391.hstgr.cloud  │
│  /webhook/readai-webhook            │
│                                     │
│  - Receives webhook                 │
│  - Normalizes to canonical schema   │
│  - Extracts decisions               │
│  - Calculates urgency               │
└────────┬────────────────────────────┘
         │
         v
┌─────────────────────────────────────┐
│  Strategic Insight API              │
│  POST /ingest/meeting               │
│  72.62.132.205:8000                 │
└────────┬────────────────────────────┘
         │
         v
┌─────────────────────────────────────┐
│  PostgreSQL Database                │
│  - Stores meeting event             │
│  - Generates embedding              │
│  - Ready for weekly analysis        │
└─────────────────────────────────────┘
```

---

## ⏰ When You'll See Results

- **Immediately:** Meeting stored in database
- **Monday 9 AM UTC:** Included in weekly brief
- **Ongoing:** Patterns and trends emerge over time

---

**Last Updated:** December 30, 2025
**Webhook URL:** `https://n8n.srv996391.hstgr.cloud/webhook/readai-webhook`
**Status:** ✅ Ready for configuration
