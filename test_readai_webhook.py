import requests
import json
from datetime import datetime

# Read.ai webhook URL
WEBHOOK_URL = "https://n8n.srv996391.hstgr.cloud/webhook/readai-webhook"

# Sample Read.ai webhook payload (based on their documentation)
payload = {
    "event": "meeting.completed",
    "meeting": {
        "id": "test-meeting-001",
        "title": "Test Strategic Planning Meeting",
        "start_time": datetime.now().isoformat(),
        "end_time": datetime.now().isoformat(),
        "duration": 3600,
        "participants": [
            {"name": "John Doe", "email": "john@example.com"},
            {"name": "Jane Smith", "email": "jane@example.com"}
        ]
    },
    "transcript": {
        "text": "In this meeting, we discussed the Q1 roadmap and decided to prioritize the new feature development. Action items: John to prepare the spec by Friday, Jane to review the budget. High priority items were identified for immediate attention.",
        "summary": "Strategic planning session covering Q1 priorities and resource allocation"
    },
    "decisions": [
        "Prioritize new feature development in Q1",
        "Allocate additional budget for engineering team"
    ],
    "action_items": [
        {
            "text": "John to prepare feature spec",
            "assignee": "john@example.com",
            "due_date": "2025-12-31"
        }
    ]
}

print("=" * 60)
print("TESTING READ.AI WEBHOOK")
print("=" * 60)
print(f"Webhook URL: {WEBHOOK_URL}")
print(f"Sending test payload...")
print()

try:
    response = requests.post(
        WEBHOOK_URL,
        json=payload,
        headers={"Content-Type": "application/json"},
        timeout=30
    )

    print(f"Response Status: {response.status_code}")
    print(f"Response Headers: {dict(response.headers)}")
    print(f"Response Body: {response.text}")
    print()

    if response.status_code == 200:
        print("✅ SUCCESS! Webhook accepted the payload")
        print()
        print("Now checking if meeting was ingested into database...")
        print("Run this command on VPS:")
        print('  ssh root@72.62.132.205 "docker exec insight-postgres psql -U insight_user -d strategic_insight -c \'SELECT id, subject, source, timestamp FROM core_events WHERE source = \\\'meeting\\\' ORDER BY timestamp DESC LIMIT 3;\'"')
    else:
        print(f"❌ FAILED! Status code: {response.status_code}")
        print(f"Response: {response.text}")

except Exception as e:
    print(f"❌ ERROR: {str(e)}")

print("=" * 60)
