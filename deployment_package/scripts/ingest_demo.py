"""Demo script to ingest synthetic test data."""

import sys
import requests
from datetime import datetime, timedelta
import random
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent))


# Synthetic data templates
SUBJECTS = [
    "Q1 Budget Review",
    "Product Roadmap Discussion",
    "Customer Feedback Analysis",
    "Team Performance Metrics",
    "Strategic Planning Session",
    "Marketing Campaign Results",
    "Engineering Sprint Review",
    "Sales Pipeline Update",
    "Technical Debt Priority",
    "Vendor Contract Renewal"
]

ACTORS = [
    "john.doe@company.com",
    "jane.smith@company.com",
    "bob.johnson@company.com",
    "alice.williams@company.com",
    "charlie.brown@company.com"
]

DECISIONS = ["made", "deferred", "none"]
DIRECTIONS = ["inbound", "outbound", "internal"]


def generate_synthetic_email(index: int, days_ago: int) -> dict:
    """Generate synthetic email event."""
    timestamp = datetime.now().astimezone() - timedelta(days=days_ago, hours=random.randint(0, 23))

    subject = random.choice(SUBJECTS)
    actor = random.choice(ACTORS)
    decision = random.choice(DECISIONS)
    urgency = random.randint(0, 10)

    text = f"This is a synthetic email about {subject.lower()}. "

    if decision == "made":
        text += "We have decided to proceed with the proposed approach. "
    elif decision == "deferred":
        text += "We will defer this decision until next week. "

    if urgency >= 8:
        text += "This is URGENT and requires immediate attention. "
    elif urgency >= 5:
        text += "This is important and should be prioritized. "

    if random.random() > 0.5:
        text += "Follow-up required by end of week. "

    return {
        "id": f"gmail:synthetic_{index}",
        "source": "email",
        "timestamp": timestamp.isoformat(),
        "actor": actor,
        "direction": random.choice(DIRECTIONS),
        "subject": subject,
        "text": text,
        "thread_id": f"thread_{index // 3}" if random.random() > 0.6 else None,
        "decision": decision,
        "action_owner": random.choice(ACTORS) if decision == "made" else None,
        "follow_up_required": random.random() > 0.5,
        "urgency_score": urgency,
        "sentiment": "unknown",
        "raw_ref": f"msg_{index}"
    }


def generate_synthetic_meeting(index: int, days_ago: int) -> dict:
    """Generate synthetic meeting event."""
    timestamp = datetime.now().astimezone() - timedelta(days=days_ago, hours=random.randint(9, 17))

    subject = random.choice(SUBJECTS) + " Meeting"
    participants = random.sample(ACTORS, k=random.randint(2, 4))
    decision = random.choice(DECISIONS)
    urgency = random.randint(3, 9)

    text = f"Meeting summary: We discussed {subject.lower()}. "
    text += f"Attendees: {', '.join(participants)}. "

    if decision == "made":
        text += "Key decisions were made during this session. "
    elif decision == "deferred":
        text += "Several decisions were deferred pending more data. "

    if urgency >= 7:
        text += "High priority action items were identified. "

    return {
        "id": f"read_ai:synthetic_{index}",
        "source": "meeting",
        "timestamp": timestamp.isoformat(),
        "actor": ", ".join(participants),
        "direction": "internal",
        "subject": subject,
        "text": text,
        "thread_id": f"recurring_{index // 4}" if random.random() > 0.7 else None,
        "decision": decision,
        "action_owner": random.choice(participants) if decision == "made" else None,
        "follow_up_required": random.random() > 0.4,
        "urgency_score": urgency,
        "sentiment": "unknown",
        "raw_ref": f"meeting_{index}"
    }


def ingest_event(event: dict, api_url: str = "http://localhost:8000"):
    """Ingest event via API."""
    endpoint = f"{api_url}/ingest/{event['source']}"

    try:
        response = requests.post(endpoint, json=event, timeout=10)
        if response.status_code == 200:
            result = response.json()
            print(f"[OK] Ingested {event['source']} event: {event['id']}")
            return True
        else:
            print(f"[X] Failed to ingest {event['id']}: {response.status_code} - {response.text}")
            return False
    except Exception as e:
        print(f"[X] Error ingesting {event['id']}: {e}")
        return False


def main():
    """Generate and ingest synthetic test data."""
    print("=" * 80)
    print("SYNTHETIC DATA INGESTION")
    print("=" * 80)

    api_url = "http://localhost:8000"

    # Test API connectivity
    try:
        response = requests.get(f"{api_url}/health", timeout=5)
        if response.status_code != 200:
            print(f"[X] API not responding at {api_url}")
            print("Please start the API server first: python api/main.py")
            return
        print(f"[OK] API is healthy at {api_url}\n")
    except Exception as e:
        print(f"[X] Cannot connect to API at {api_url}: {e}")
        print("Please start the API server first: python api/main.py")
        return

    # Generate events for the past 35 days (covers week + baseline)
    num_emails = 50
    num_meetings = 30

    print(f"Generating {num_emails} synthetic emails...")
    for i in range(num_emails):
        days_ago = random.randint(0, 35)
        event = generate_synthetic_email(i, days_ago)
        ingest_event(event, api_url)

    print(f"\nGenerating {num_meetings} synthetic meetings...")
    for i in range(num_meetings):
        days_ago = random.randint(0, 35)
        event = generate_synthetic_meeting(i, days_ago)
        ingest_event(event, api_url)

    # Get stats
    print("\n" + "=" * 80)
    print("INGESTION COMPLETE")
    print("=" * 80)

    try:
        response = requests.get(f"{api_url}/stats", timeout=5)
        if response.status_code == 200:
            stats = response.json()
            print(f"Total Events: {stats['total_events']}")
            print(f"  - Emails: {stats['email_events']}")
            print(f"  - Meetings: {stats['meeting_events']}")
        print("\nYou can now run the weekly processing:")
        print("  python scripts/weekly_run.py")
    except Exception as e:
        print(f"Could not fetch stats: {e}")

    print("=" * 80)


if __name__ == "__main__":
    main()
