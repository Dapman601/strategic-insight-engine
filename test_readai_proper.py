import requests
import json
from datetime import datetime

# Read.ai webhook URL
WEBHOOK_URL = "https://n8n.srv996391.hstgr.cloud/webhook/readai-webhook"

# Proper Read.ai webhook payload format (matching n8n function expectations)
payload = {
    "meeting_id": "test-mtg-12345",
    "id": "test-mtg-12345",
    "title": "Q1 Strategic Planning - Read.ai Test",
    "meeting_title": "Q1 Strategic Planning - Read.ai Test",
    "start_time": "2025-12-30T10:00:00Z",
    "created_at": "2025-12-30T10:00:00Z",
    "organizer": "frontendlabs.uk@gmail.com",
    "participants": [
        {"name": "Frontend Labs", "email": "frontendlabs.uk@gmail.com"},
        {"name": "John Doe", "email": "john@example.com"},
        {"name": "Jane Smith", "email": "jane@example.com"}
    ],
    "summary": "We reviewed the Q1 roadmap and decided to prioritize feature development. Key decision made to allocate additional budget for the engineering team.",
    "transcript": "In this meeting, we discussed the Q1 roadmap. After thorough analysis, we decided to proceed with the new feature development as our top priority. John raised concerns about the timeline, but we agreed to move forward. Action items were assigned: Jane will prepare the budget proposal by Friday. This is a high priority initiative that requires immediate attention. Follow up meeting scheduled for next week to review progress.",
    "action_items": [
        {
            "text": "Prepare budget proposal",
            "owner": "jane@example.com",
            "due_date": "2025-12-31"
        },
        {
            "text": "Review technical specifications",
            "owner": "john@example.com",
            "due_date": "2025-12-31"
        }
    ],
    "priority": "high",
    "meeting_type": "planning",
    "meeting_url": "https://read.ai/meetings/test-mtg-12345",
    "recurring_meeting_id": None
}

print("=" * 60)
print("TESTING READ.AI WEBHOOK - PROPER FORMAT")
print("=" * 60)
print(f"Webhook URL: {WEBHOOK_URL}")
print(f"Payload:")
print(json.dumps(payload, indent=2))
print()
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

    try:
        response_json = response.json()
        print(f"Response Body: {json.dumps(response_json, indent=2)}")

        if response.status_code == 200:
            print()
            print("[SUCCESS] Webhook accepted and processed the payload!")

            if response_json.get('status') == 'success':
                print(f"Event ID: {response_json.get('event_id')}")
                print()
                print("Now check the database to verify ingestion...")
            elif response_json.get('status') == 'error':
                print(f"[ERROR] n8n processing failed: {response_json.get('message')}")
    except:
        print(f"Response Body (raw): {response.text}")

    print()
    print("To verify ingestion, run:")
    print('  ssh root@72.62.132.205 "docker exec insight-postgres psql -U insight_user -d strategic_insight -c \\')
    print('    \'SELECT id, subject, actor, urgency_score, timestamp FROM core_events WHERE id LIKE \\\'read_ai:test%\\\' ORDER BY timestamp DESC;\\\'"')

except Exception as e:
    print(f"[ERROR] {str(e)}")

print("=" * 60)
