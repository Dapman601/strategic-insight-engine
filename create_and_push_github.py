"""Create GitHub repository and push code."""
import requests
import subprocess
import sys

print("=" * 80)
print("CREATE GITHUB REPOSITORY & PUSH CODE")
print("=" * 80)
print()
print("Git is configured as:")
print("  Name: ADEDAPO AJAYI")
print("  Email: Dapman601@hotmail.co.uk")
print()
print("I need your GitHub Personal Access Token to create the repository.")
print()
print("Get your token here: https://github.com/settings/tokens")
print("Required scope: repo")
print()

# Get token
token = input("Enter your GitHub Personal Access Token (or press Enter to skip): ").strip()

if not token:
    print()
    print("No token provided. You can create the repository manually at:")
    print("https://github.com/new")
    print()
    print("Repository name: strategic-insight-engine")
    print('Description: ML-powered communication analysis system')
    print()
    print("After creating the repo, run these commands:")
    print()
    print("git remote add origin https://github.com/YOUR_USERNAME/strategic-insight-engine.git")
    print("git branch -M main")
    print("git push -u origin main")
    sys.exit(0)

# Get GitHub username
print()
print("Fetching your GitHub username...")

try:
    user_response = requests.get(
        "https://api.github.com/user",
        headers={"Authorization": f"token {token}"},
        timeout=10
    )

    if user_response.status_code != 200:
        print(f"[ERROR] Failed to authenticate: {user_response.status_code}")
        print("Please check your token and try again.")
        sys.exit(1)

    username = user_response.json()['login']
    print(f"Authenticated as: {username}")

except Exception as e:
    print(f"[ERROR] {str(e)}")
    sys.exit(1)

# Create repository
repo_name = "strategic-insight-engine"
description = "ML-powered communication analysis system that ingests emails and meetings to detect decision pressure, drift, and strategic patterns. Automated weekly briefs via Slack."

print()
print(f"Creating repository: {repo_name}")

try:
    create_response = requests.post(
        "https://api.github.com/user/repos",
        headers={
            "Authorization": f"token {token}",
            "Accept": "application/vnd.github.v3+json"
        },
        json={
            "name": repo_name,
            "description": description,
            "private": False,
            "has_issues": True,
            "has_projects": True,
            "has_wiki": True,
            "auto_init": False
        },
        timeout=30
    )

    if create_response.status_code == 201:
        repo_data = create_response.json()
        html_url = repo_data['html_url']
        clone_url = repo_data['clone_url']

        print(f"Repository created: {html_url}")

        # Add remote and push
        print()
        print("Adding remote and pushing code...")

        # Add remote
        subprocess.run(["git", "remote", "add", "origin", clone_url], check=True)

        # Rename branch to main
        subprocess.run(["git", "branch", "-M", "main"], check=True)

        # Push to GitHub
        print("Pushing to GitHub...")
        result = subprocess.run(["git", "push", "-u", "origin", "main"], capture_output=True, text=True)

        if result.returncode == 0:
            print()
            print("=" * 80)
            print("SUCCESS! Code pushed to GitHub")
            print("=" * 80)
            print()
            print(f"Repository URL: {html_url}")
            print()
            print("Your Strategic Insight Engine is now on GitHub!")

        else:
            print(f"[ERROR] Push failed: {result.stderr}")
            print()
            print("Try pushing manually:")
            print(f"git push -u origin main")

    elif create_response.status_code == 422:
        error_msg = create_response.json().get('errors', [{}])[0].get('message', '')
        if 'already exists' in error_msg:
            print(f"Repository already exists at: https://github.com/{username}/{repo_name}")
            print()
            print("Pushing to existing repository...")

            clone_url = f"https://github.com/{username}/{repo_name}.git"

            subprocess.run(["git", "remote", "add", "origin", clone_url], check=False)
            subprocess.run(["git", "branch", "-M", "main"], check=True)

            result = subprocess.run(["git", "push", "-u", "origin", "main"], capture_output=True, text=True)

            if result.returncode == 0:
                print()
                print("SUCCESS! Code pushed to existing repository")
                print(f"Repository URL: https://github.com/{username}/{repo_name}")
            else:
                print(f"[ERROR] Push failed: {result.stderr}")
        else:
            print(f"[ERROR] {create_response.json()}")
    else:
        print(f"[ERROR] Failed to create repository: {create_response.status_code}")
        print(create_response.text)

except Exception as e:
    print(f"[ERROR] {str(e)}")
    import traceback
    traceback.print_exc()
