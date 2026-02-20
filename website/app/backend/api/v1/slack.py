"""
Slack endpoints.
"""
from fastapi import APIRouter
from pydantic import BaseModel
from typing import Dict, Any

from slack.notifier import slack_notifier, NotificationType
from core.logging import get_logger

logger = get_logger("api.slack")
router = APIRouter()


class SlackNotificationRequest(BaseModel):
    """Request model for Slack notifications."""
    notification_type: str
    data: Dict[str, Any]
    channel: str = None


@router.post("/notify")
async def send_notification(request: SlackNotificationRequest):
    """Send Slack notification."""
    try:
        notification_type = NotificationType(request.notification_type)
        success = await slack_notifier.send_notification(
            notification_type=notification_type,
            data=request.data,
            channel=request.channel
        )
        return {"status": "success" if success else "failed"}
    except Exception as e:
        logger.error(f"Failed to send Slack notification: {e}", exc_info=True)
        return {"status": "error", "message": str(e)}
