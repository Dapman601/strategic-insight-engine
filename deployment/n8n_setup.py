"""
n8n Workflow Deployment Script
Automatically imports workflows to n8n instance using API
"""

import requests
import json
import sys
from pathlib import Path

# n8n Configuration (from credentials)
N8N_URL = "https://n8n.srv996391.hstgr.cloud"
N8N_EMAIL = "frontendlabs.uk@gmail.com"
N8N_PASSWORD = "4rontEnd#labs"


def login_n8n():
    """Login to n8n and get authentication cookie."""
    print("Logging in to n8n...")

    login_url = f"{N8N_URL}/rest/login"
    payload = {
        "emailOrLdapLoginId": N8N_EMAIL,
        "password": N8N_PASSWORD
    }

    response = requests.post(login_url, json=payload)

    if response.status_code == 200:
        print("[OK] Login successful")
        return response.cookies
    else:
        print(f"[ERROR] Login failed: {response.status_code} - {response.text}")
        return None


def import_workflow(workflow_path: Path, cookies):
    """Import workflow to n8n."""
    print(f"\nImporting workflow: {workflow_path.name}")

    with open(workflow_path, 'r') as f:
        workflow_data = json.load(f)

    import_url = f"{N8N_URL}/rest/workflows"

    response = requests.post(
        import_url,
        json=workflow_data,
        cookies=cookies
    )

    if response.status_code in [200, 201]:
        result = response.json()
        print(f"[OK] Workflow imported successfully")
        print(f"  ID: {result.get('id')}")
        print(f"  Name: {result.get('name')}")
        return True
    else:
        print(f"[ERROR] Import failed: {response.status_code} - {response.text}")
        return False


def activate_workflow(workflow_id: str, cookies):
    """Activate an imported workflow."""
    print(f"Activating workflow {workflow_id}...")

    activate_url = f"{N8N_URL}/rest/workflows/{workflow_id}/activate"

    response = requests.patch(
        activate_url,
        cookies=cookies
    )

    if response.status_code == 200:
        print(f"[OK] Workflow activated")
        return True
    else:
        print(f"[ERROR] Activation failed: {response.status_code}")
        return False


def main():
    """Main deployment function."""
    print("=" * 80)
    print("n8n Workflow Deployment")
    print("=" * 80)

    # Find workflow files
    workflow_dir = Path(__file__).parent.parent / "n8n_workflows"

    if not workflow_dir.exists():
        print(f"[ERROR] Workflow directory not found: {workflow_dir}")
        sys.exit(1)

    workflow_files = list(workflow_dir.glob("*.json"))

    if not workflow_files:
        print(f"[ERROR] No workflow files found in {workflow_dir}")
        sys.exit(1)

    print(f"Found {len(workflow_files)} workflow(s)")

    # Login
    cookies = login_n8n()
    if not cookies:
        print("[ERROR] Cannot proceed without authentication")
        sys.exit(1)

    # Import each workflow
    imported_count = 0
    for workflow_path in workflow_files:
        if import_workflow(workflow_path, cookies):
            imported_count += 1

    print("\n" + "=" * 80)
    print(f"Deployment Complete: {imported_count}/{len(workflow_files)} workflows imported")
    print("=" * 80)

    if imported_count > 0:
        print("\nNext steps:")
        print("1. Log in to n8n web interface")
        print("2. Configure Gmail OAuth2 credentials")
        print("3. Update API endpoint URLs if needed")
        print("4. Test workflows manually")
        print("5. Activate workflows")
        print(f"\nn8n URL: {N8N_URL}")


if __name__ == "__main__":
    main()
