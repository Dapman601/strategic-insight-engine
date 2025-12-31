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

        # Get Gmail workflow
        wf_url = f'{N8N_URL}/rest/workflows/YUjszHZs59XBKaNN'
        wf_response = requests.get(wf_url, cookies=cookies, timeout=10)

        if wf_response.status_code == 200:
            workflow = wf_response.json()
            print(f"[OK] Gmail Workflow Status:")
            print(f"  Name: {workflow['data']['name']}")
            print(f"  Active: {workflow['data']['active']}")
            print(f"  Updated: {workflow['data']['updatedAt']}")
            print()

            # Check Gmail trigger node
            for node in workflow['data']['nodes']:
                if 'Gmail' in node['type']:
                    print(f"[Gmail Trigger Node]")
                    print(f"  Type: {node['type']}")
                    print(f"  Name: {node['name']}")
                    if 'parameters' in node:
                        params = node['parameters']
                        print(f"  Parameters: {json.dumps(params, indent=4)}")
                    print()

                # Check HTTP Request node
                if node['type'] == 'n8n-nodes-base.httpRequest':
                    print(f"[HTTP Request Node]")
                    print(f"  URL: {node['parameters'].get('url', 'N/A')}")
                    print()
        else:
            print(f"[ERROR] Failed to get workflow: {wf_response.status_code}")
    else:
        print(f"[ERROR] Login failed: {response.status_code}")
except Exception as e:
    print(f"[ERROR] {str(e)}")
