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

        # Get Read.ai workflow
        wf_url = f'{N8N_URL}/rest/workflows/Zu6VBTt6PRqX7qNH'
        wf_response = requests.get(wf_url, cookies=cookies, timeout=10)

        if wf_response.status_code == 200:
            workflow = wf_response.json()

            print("=" * 80)
            print("READ.AI WORKFLOW - FULL NODE DETAILS")
            print("=" * 80)

            for i, node in enumerate(workflow['data']['nodes']):
                print(f"\nNODE {i+1}: {node['name']}")
                print(f"  Type: {node['type']}")

                if 'parameters' in node:
                    print(f"  Parameters:")
                    print(json.dumps(node['parameters'], indent=4))

                print("-" * 80)

        else:
            print(f"[ERROR] Failed to get workflow: {wf_response.status_code}")
    else:
        print(f"[ERROR] Login failed: {response.status_code}")
except Exception as e:
    print(f"[ERROR] {str(e)}")
