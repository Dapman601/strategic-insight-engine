"""Verify Read.ai webhook is configured and working."""

import requests
import json
from datetime import datetime

# Read.ai webhook URL (via n8n)
WEBHOOK_URL = "https://n8n.srv996391.hstgr.cloud/webhook/readai-webhook"

# Sample test payload (simulates what Read.ai would send)
test_payload = {
    "meeting_id": "test-verify-123",
    "id": "test-verify-123",
    "title": "Read.ai Integration Verification Test",
    "meeting_title": "Read.ai Integration Verification Test",
    "start_time": datetime.now().isoformat(),
    "created_at": datetime.now().isoformat(),
    "organizer": "frontendlabs.uk@gmail.com",
    "participants": [
        {"name": "Test User", "email": "test@example.com"}
    ],
    "summary": "This is a test to verify Read.ai webhook integration with the Strategic Insight Engine. If you see this in your database, the webhook is working correctly!",
    "transcript": "Test meeting transcript for verification purposes.",
    "priority": "high",
    "meeting_type": "test"
}

print("=" * 70)
print("READ.AI WEBHOOK VERIFICATION TEST")
print("=" * 70)
print(f"Webhook URL: {WEBHOOK_URL}")
print()
print("Sending test payload...")
print()

try:
    response = requests.post(
        WEBHOOK_URL,
        json=test_payload,
        headers={"Content-Type": "application/json"},
        timeout=30
    )

    print(f"Response Status: {response.status_code}")

    if response.status_code == 200:
        print("✅ SUCCESS! Webhook accepted the payload")
        print()
        print("Response:")
        try:
            print(json.dumps(response.json(), indent=2))
        except:
            print(response.text)

        print()
        print("=" * 70)
        print("NEXT: Check if the meeting was ingested")
        print("=" * 70)
        print()
        print("Run this command on VPS to verify:")
        print()
        print('ssh root@72.62.132.205 "docker exec insight-postgres psql -U insight_user -d strategic_insight -c')
        print('  \\"SELECT id, subject, source, decision, urgency_score, timestamp FROM core_events')
        print('  WHERE id = \'read_ai:test-verify-123\';\\"')
        print('"')
        print()
        print("If you see the test meeting, Read.ai webhook is configured correctly!")

    else:
        print(f"❌ FAILED! Status code: {response.status_code}")
        print(f"Response: {response.text}")

except Exception as e:
    print(f"❌ ERROR: {str(e)}")
    print()
    print("Possible issues:")
    print("1. n8n workflow is not active")
    print("2. Webhook URL is incorrect")
    print("3. Network connectivity issue")

print()
print("=" * 70)
