"""Check Slack bot token scopes."""

from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError

SLACK_BOT_TOKEN = "[REDACTED]"

def check_slack_scopes():
    """Check what scopes are configured for the Slack bot."""
    client = WebClient(token=SLACK_BOT_TOKEN)

    try:
        # Test authentication and get bot info
        response = client.auth_test()

        print("=" * 80)
        print("SLACK BOT CONFIGURATION")
        print("=" * 80)
        print(f"Bot User ID: {response.get('user_id')}")
        print(f"Bot Name: {response.get('user')}")
        print(f"Team: {response.get('team')}")
        print(f"Team ID: {response.get('team_id')}")
        print(f"URL: {response.get('url')}")
        print()

        # Get team info for more details
        try:
            team_info = client.team_info()
            print(f"Workspace Name: {team_info['team']['name']}")
            print()
        except:
            pass

        # The auth.test response doesn't directly show scopes
        # But we can infer from the token type and test capabilities
        print("=" * 80)
        print("CONFIGURED SCOPES (Inferred from capabilities)")
        print("=" * 80)

        scopes_needed = []

        # Test conversations.open (for DMs)
        try:
            test_response = client.conversations_open(users=response['user_id'])
            print("✅ conversations.open - WORKING")
            scopes_needed.append("im:write or chat:write")
        except SlackApiError as e:
            print(f"❌ conversations.open - FAILED: {e.response['error']}")

        # Test chat.postMessage capability
        print("✅ chat.postMessage - ASSUMED WORKING (used in production)")
        scopes_needed.append("chat:write")

        print()
        print("=" * 80)
        print("REQUIRED SCOPES FOR THIS BOT")
        print("=" * 80)
        print("Based on the code in src/insight/modules/slack.py:")
        print()
        print("MINIMUM REQUIRED:")
        print("  • chat:write         - Send messages to channels/DMs")
        print("  • im:write           - Open and write to DM channels")
        print()
        print("RECOMMENDED:")
        print("  • chat:write")
        print("  • im:write")
        print("  • users:read         - Get user information (optional)")
        print()
        print("=" * 80)
        print("WHAT THE BOT DOES")
        print("=" * 80)
        print("1. Opens a DM channel with user (conversations.open)")
        print("2. Sends formatted weekly brief (chat.postMessage)")
        print("3. Supports markdown formatting")
        print()
        print("=" * 80)

    except SlackApiError as e:
        print(f"❌ ERROR: {e.response['error']}")
        print(f"Details: {e.response.get('error_description', 'No description')}")
    except Exception as e:
        print(f"❌ ERROR: {str(e)}")

if __name__ == "__main__":
    check_slack_scopes()
