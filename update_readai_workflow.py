"""Update Read.ai workflow to handle test payloads gracefully."""
import requests
import json
import warnings
warnings.filterwarnings('ignore')

N8N_URL = 'https://n8n.srv996391.hstgr.cloud'
N8N_EMAIL = 'frontendlabs.uk@gmail.com'
N8N_PASSWORD = '4rontEnd#labs'
WORKFLOW_ID = 'Zu6VBTt6PRqX7qNH'

# Updated function code with robust error handling
UPDATED_CODE = r"""// Normalize Read.ai meeting to canonical event schema
const item = $input.item.json;

// Generate unique ID
const eventId = `read_ai:${item.meeting_id || item.id || 'test_' + Date.now()}`;

// Extract participants
const participants = (item.participants || []).map(p => p.email || p.name).join(', ');

// Determine direction based on organizer
let direction = 'internal';
const userEmail = 'frontendlabs.uk@gmail.com';
if (item.organizer && item.organizer.includes(userEmail)) {
  direction = 'outbound';
} else if (item.participants && item.participants.some(p => !p.email || !p.email.includes('@yourcompany.com'))) {
  direction = 'inbound';
}

// Parse decision status from transcript
let decision = 'none';
let actionOwner = null;
const transcript = item.transcript || item.summary || '';
const lowerTranscript = transcript.toLowerCase();

if (lowerTranscript.includes('decided') || lowerTranscript.includes('we will') || lowerTranscript.includes('agreed to')) {
  decision = 'made';
}
if (lowerTranscript.includes('defer') || lowerTranscript.includes('table this') || lowerTranscript.includes('revisit later')) {
  decision = 'deferred';
}

// Extract action items and owners
const actionItems = item.action_items || [];
if (actionItems.length > 0 && actionItems[0].owner) {
  actionOwner = actionItems[0].owner;
}

// Determine follow-up requirement
const followUpRequired = actionItems.length > 0 ||
                         lowerTranscript.includes('follow up') ||
                         lowerTranscript.includes('next meeting');

// Calculate urgency score (0-10)
let urgencyScore = 5; // default for meetings
if (item.priority === 'high' || lowerTranscript.includes('urgent') || lowerTranscript.includes('critical')) {
  urgencyScore = 9;
} else if (item.priority === 'medium' || actionItems.length > 3) {
  urgencyScore = 7;
} else if (item.priority === 'low' || item.meeting_type === 'status update') {
  urgencyScore = 4;
}

// Build text from summary and truncated transcript
const summaryText = item.summary || '';
const transcriptExcerpt = transcript.substring(0, 1000);
const fullText = `${summaryText}\n\nKey points: ${transcriptExcerpt}`;

// Robust timestamp handling - handle test payloads and invalid dates
let timestamp;
const timeValue = item.start_time || item.created_at || item.timestamp;
if (timeValue) {
  const date = new Date(timeValue);
  // Check if date is valid
  if (!isNaN(date.getTime())) {
    timestamp = date.toISOString();
  } else {
    // Invalid date, use current time
    timestamp = new Date().toISOString();
  }
} else {
  // No timestamp provided (test payload), use current time
  timestamp = new Date().toISOString();
}

// Build canonical event
const canonicalEvent = {
  id: eventId,
  source: 'meeting',
  timestamp: timestamp,
  actor: participants || item.organizer || 'test-user',
  direction: direction,
  subject: item.title || item.meeting_title || '(Test webhook payload)',
  text: fullText.substring(0, 2000) || 'Test webhook received',
  thread_id: item.recurring_meeting_id || null,
  decision: decision,
  action_owner: actionOwner,
  follow_up_required: followUpRequired,
  urgency_score: urgencyScore,
  sentiment: 'unknown',
  raw_ref: item.meeting_url || item.id || 'test'
};

return { json: canonicalEvent };"""

print("=" * 80)
print("UPDATING READ.AI WORKFLOW TO HANDLE TEST PAYLOADS")
print("=" * 80)
print()

try:
    # Login
    print("[1/4] Logging into n8n...")
    response = requests.post(
        f'{N8N_URL}/rest/login',
        json={'emailOrLdapLoginId': N8N_EMAIL, 'password': N8N_PASSWORD},
        timeout=10,
        verify=False
    )

    if response.status_code != 200:
        print(f"[ERROR] Login failed: {response.status_code}")
        exit(1)

    cookies = response.cookies
    print("      Logged in successfully")

    # Get current workflow
    print("[2/4] Fetching current workflow...")
    wf_response = requests.get(
        f'{N8N_URL}/rest/workflows/{WORKFLOW_ID}',
        cookies=cookies,
        timeout=10,
        verify=False
    )

    if wf_response.status_code != 200:
        print(f"[ERROR] Failed to get workflow: {wf_response.status_code}")
        exit(1)

    workflow = wf_response.json()
    print("      Workflow fetched")

    # Update the normalization node
    print("[3/4] Updating 'Normalize Read.ai Event' node...")
    nodes = workflow['data']['nodes']
    updated = False

    for i, node in enumerate(nodes):
        if node['name'] == 'Normalize Read.ai Event':
            nodes[i]['parameters']['functionCode'] = UPDATED_CODE
            updated = True
            print("      Node code updated")
            break

    if not updated:
        print("[ERROR] Could not find 'Normalize Read.ai Event' node")
        exit(1)

    # Save workflow
    print("[4/4] Saving updated workflow...")
    update_response = requests.patch(
        f'{N8N_URL}/rest/workflows/{WORKFLOW_ID}',
        json={'nodes': nodes},
        cookies=cookies,
        timeout=10,
        verify=False
    )

    if update_response.status_code == 200:
        print("      Workflow saved")
        print()
        print("=" * 80)
        print("SUCCESS! WORKFLOW UPDATED")
        print("=" * 80)
        print()
        print("Changes made:")
        print("  1. Added robust timestamp validation")
        print("  2. Falls back to current time for test payloads")
        print("  3. Validates date before calling toISOString()")
        print("  4. Handles missing meeting_id, title, actor, and other fields")
        print("  5. Provides default values for all required fields")
        print()
        print("The workflow will now successfully process:")
        print("  - Real Read.ai meetings with complete data")
        print("  - Test webhook payloads with minimal/missing data")
        print("  - Edge cases with invalid timestamps")
        print()
        print("Next: Send another test from Read.ai to verify it works!")
    else:
        print(f"[ERROR] Failed to update workflow: {update_response.status_code}")
        print(update_response.text)
        exit(1)

except Exception as e:
    print(f"[ERROR] {str(e)}")
    import traceback
    traceback.print_exc()
    exit(1)
