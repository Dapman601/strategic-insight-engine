"""Create GitHub repository for Strategic Insight Engine."""
import requests
import json

print("=" * 80)
print("CREATE GITHUB REPOSITORY")
print("=" * 80)
print()
print("This script will create a new GitHub repository.")
print()
print("You need a GitHub Personal Access Token with 'repo' scope.")
print("Create one at: https://github.com/settings/tokens/new")
print()
print("Required scopes: repo (Full control of private repositories)")
print()

# Get token from user
token = input("Enter your GitHub Personal Access Token: ").strip()

if not token:
    print("[ERROR] No token provided. Exiting.")
    exit(1)

# Repository details
repo_name = "strategic-insight-engine"
description = "ML-powered communication analysis system that ingests emails and meetings to detect decision pressure, drift, and strategic patterns. Automated weekly briefs via Slack."
private = False  # Set to True if you want a private repo

print()
print("Creating repository with these details:")
print(f"  Name: {repo_name}")
print(f"  Description: {description}")
print(f"  Visibility: {'Private' if private else 'Public'}")
print()

# Create repository
url = "https://api.github.com/user/repos"
headers = {
    "Authorization": f"token {token}",
    "Accept": "application/vnd.github.v3+json"
}

data = {
    "name": repo_name,
    "description": description,
    "private": private,
    "has_issues": True,
    "has_projects": True,
    "has_wiki": True,
    "auto_init": False  # We already have code to push
}

try:
    response = requests.post(url, headers=headers, json=data, timeout=30)

    if response.status_code == 201:
        repo_data = response.json()
        clone_url = repo_data['clone_url']
        html_url = repo_data['html_url']
        ssh_url = repo_data['ssh_url']

        print("=" * 80)
        print("SUCCESS! Repository created")
        print("=" * 80)
        print()
        print(f"Repository URL: {html_url}")
        print(f"Clone URL (HTTPS): {clone_url}")
        print(f"Clone URL (SSH): {ssh_url}")
        print()
        print("=" * 80)
        print("NEXT STEPS:")
        print("=" * 80)
        print()
        print("Run these commands to push your code:")
        print()
        print(f"git remote add origin {clone_url}")
        print("git branch -M main")
        print("git push -u origin main")
        print()
        print("Or if you prefer SSH:")
        print()
        print(f"git remote add origin {ssh_url}")
        print("git branch -M main")
        print("git push -u origin main")
        print()

    elif response.status_code == 422:
        error_data = response.json()
        if "name already exists" in error_data.get('errors', [{}])[0].get('message', ''):
            print("[ERROR] Repository 'strategic-insight-engine' already exists in your account.")
            print()
            print("Options:")
            print("1. Delete the existing repo and run this script again")
            print("2. Use a different name (edit this script)")
            print("3. Push to the existing repo:")
            print()
            print("   git remote add origin https://github.com/YOUR_USERNAME/strategic-insight-engine.git")
            print("   git branch -M main")
            print("   git push -u origin main")
        else:
            print(f"[ERROR] Repository creation failed: {error_data}")
    else:
        print(f"[ERROR] Failed to create repository: {response.status_code}")
        print(f"Response: {response.text}")

except Exception as e:
    print(f"[ERROR] {str(e)}")
    import traceback
    traceback.print_exc()
