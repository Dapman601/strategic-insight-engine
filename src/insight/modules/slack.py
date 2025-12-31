"""Slack integration for delivering weekly briefs."""

import logging
from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError

from src.config import get_settings

settings = get_settings()
logger = logging.getLogger(__name__)


def send_slack_dm(message: str, user_id: str | None = None) -> bool:
    """
    Send a direct message via Slack.

    Args:
        message: Message content (supports Markdown)
        user_id: Slack user ID (defaults to config)

    Returns:
        True if successful, False otherwise
    """
    if not settings.slack_bot_token:
        logger.error("Slack bot token not configured")
        return False

    target_user = user_id or settings.slack_user_id
    if not target_user:
        logger.error("Slack user ID not configured")
        return False

    try:
        client = WebClient(token=settings.slack_bot_token)

        # Open a DM channel with the user
        response = client.conversations_open(users=target_user)
        channel_id = response["channel"]["id"]

        # Send the message
        client.chat_postMessage(
            channel=channel_id,
            text=message,
            mrkdwn=True
        )

        logger.info(f"Slack message sent successfully to {target_user}")
        return True

    except SlackApiError as e:
        logger.error(f"Slack API error: {e.response['error']}")
        return False
    except Exception as e:
        logger.error(f"Failed to send Slack message: {e}")
        return False


def send_weekly_brief(
    markdown_brief: str,
    watchlist: list[str],
    week_start: str,
    week_end: str
) -> bool:
    """
    Send formatted weekly brief via Slack.

    Args:
        markdown_brief: Markdown formatted brief
        watchlist: List of watchlist items
        week_start: Week start date string
        week_end: Week end date string

    Returns:
        True if successful, False otherwise
    """
    # Format watchlist
    watchlist_text = "\n".join([f"• {item}" for item in watchlist])

    # Compose full message
    full_message = f"""📊 *Weekly Strategic Brief*
_{week_start} to {week_end}_

{markdown_brief}

🔍 *Watchlist*
{watchlist_text if watchlist else "No items on watchlist"}

---
_Generated automatically by the Weekly Strategic Insight Engine_
"""

    return send_slack_dm(full_message)
