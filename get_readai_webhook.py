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
            print(f"[OK] Read.ai Workflow Status:")
            print(f"  Name: {workflow['data']['name']}")
            print(f"  Active: {workflow['data']['active']}")
            print(f"  Updated: {workflow['data']['updatedAt']}")
            print()

            # Find webhook node
            for node in workflow['data']['nodes']:
                if 'webhook' in node['type'].lower() or 'webhook' in node.get('name', '').lower():
                    print(f"[Webhook Node]")
                    print(f"  Name: {node['name']}")
                    print(f"  Type: {node['type']}")

                    if 'parameters' in node and 'path' in node['parameters']:
                        webhook_path = node['parameters']['path']
                        webhook_url = f"{N8N_URL}/webhook/{webhook_path}"
                        print(f"  Path: {webhook_path}")
                        print(f"  Full URL: {webhook_url}")
                        print()
                        print(f"=" * 60)
                        print(f"CONFIGURE READ.AI WITH THIS WEBHOOK URL:")
                        print(f"{webhook_url}")
                        print(f"=" * 60)
                    print()

                # Check HTTP Request node
                if node['type'] == 'n8n-nodes-base.httpRequest':
                    print(f"[HTTP Request to API]")
                    print(f"  URL: {node['parameters'].get('url', 'N/A')}")
                    print()
        else:
            print(f"[ERROR] Failed to get workflow: {wf_response.status_code}")
    else:
        print(f"[ERROR] Login failed: {response.status_code}")
except Exception as e:
    print(f"[ERROR] {str(e)}")
