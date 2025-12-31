import requests
import json

N8N_URL = 'https://n8n.srv996391.hstgr.cloud'
N8N_EMAIL = 'frontendlabs.uk@gmail.com'
N8N_PASSWORD = '4rontEnd#labs'

# Login
login_url = f'{N8N_URL}/rest/login'
payload = {'emailOrLdapLoginId': N8N_EMAIL, 'password': N8N_PASSWORD}

try:
    response = requests.post(login_url, json=payload, timeout=10)
    if response.status_code == 200:
        cookies = response.cookies

        # Get recent executions for Read.ai workflow
        exec_url = f'{N8N_URL}/rest/executions?filter={{"workflowId":"Zu6VBTt6PRqX7qNH"}}&limit=5'
        exec_response = requests.get(exec_url, cookies=cookies, timeout=10)

        if exec_response.status_code == 200:
            executions = exec_response.json()

            print("=" * 80)
            print("RECENT READ.AI WORKFLOW EXECUTIONS")
            print("=" * 80)

            if executions['data']:
                for i, execution in enumerate(executions['data'], 1):
                    print(f"\n[Execution {i}]")
                    print(f"  ID: {execution.get('id')}")
                    print(f"  Status: {execution.get('status')}")
                    print(f"  Started: {execution.get('startedAt')}")
                    print(f"  Stopped: {execution.get('stoppedAt')}")
                    print(f"  Mode: {execution.get('mode')}")

                    if execution.get('status') == 'error':
                        print(f"  ERROR: {execution.get('data', {}).get('resultData', {}).get('error', {}).get('message')}")
            else:
                print("\nNo executions found for this workflow")
                print("This might mean:")
                print("  1. The webhook wasn't triggered")
                print("  2. The workflow isn't active")
                print("  3. There's a configuration issue")

        else:
            print(f"[ERROR] Failed to get executions: {exec_response.status_code}")
    else:
        print(f"[ERROR] Login failed: {response.status_code}")
except Exception as e:
    print(f"[ERROR] {str(e)}")
