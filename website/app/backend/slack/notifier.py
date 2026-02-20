"""
Slack notification service with channel grouping.
"""
import asyncio
from typing import Dict, Any, Optional, List
from datetime import datetime
import httpx
from enum import Enum

from config.settings import settings
from core.logging import get_logger
from core.exceptions import SlackError

logger = get_logger("slack")


class NotificationType(str, Enum):
    """Types of notifications."""
    CART_ABANDONMENT = "cart_abandonment"
    MODEL_DEPLOYED = "model_deployed"
    DRIFT_DETECTED = "drift_detected"
    INFLUENCER_TAG = "influencer_tag"
    DAILY_REPORT = "daily_report"
    WEEKLY_REPORT = "weekly_report"


class SlackNotifier:
    """Slack notification service."""
    
    def __init__(self):
        self.webhook_url = settings.SLACK_WEBHOOK_URL
        self.bot_token = settings.SLACK_BOT_TOKEN
        self._lock = asyncio.Lock()
    
    def _get_channel(self, notification_type: NotificationType) -> str:
        """Get channel for notification type."""
        channel_map = {
            NotificationType.CART_ABANDONMENT: settings.SLACK_CHANNEL_ALERTS,
            NotificationType.MODEL_DEPLOYED: settings.SLACK_CHANNEL_ALERTS,
            NotificationType.DRIFT_DETECTED: settings.SLACK_CHANNEL_DRIFT,
            NotificationType.INFLUENCER_TAG: settings.SLACK_CHANNEL_ALERTS,
            NotificationType.DAILY_REPORT: settings.SLACK_CHANNEL_REPORTS,
            NotificationType.WEEKLY_REPORT: settings.SLACK_CHANNEL_REPORTS,
        }
        return channel_map.get(notification_type, settings.SLACK_CHANNEL_ALERTS)
    
    def _format_message(
        self,
        notification_type: NotificationType,
        data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Format message based on notification type."""
        base_message = {
            "text": f"IndoCloth Market - {notification_type.value.replace('_', ' ').title()}",
            "blocks": [],
        }
        
        if notification_type == NotificationType.CART_ABANDONMENT:
            base_message["blocks"] = [
                {
                    "type": "header",
                    "text": {"type": "plain_text", "text": "🛒 Cart Abandonment Alert"}
                },
                {
                    "type": "section",
                    "fields": [
                        {"type": "mrkdwn", "text": f"*Product:* {data.get('product_name', 'N/A')}"},
                        {"type": "mrkdwn", "text": f"*Times Added:* {data.get('add_count', 0)}"},
                        {"type": "mrkdwn", "text": f"*Product ID:* {data.get('product_id', 'N/A')}"},
                    ]
                }
            ]
        
        elif notification_type == NotificationType.MODEL_DEPLOYED:
            base_message["blocks"] = [
                {
                    "type": "header",
                    "text": {"type": "plain_text", "text": "🚀 Model Deployed"}
                },
                {
                    "type": "section",
                    "fields": [
                        {"type": "mrkdwn", "text": f"*Model:* {data.get('model_name', 'N/A')}"},
                        {"type": "mrkdwn", "text": f"*Version:* {data.get('version', 'N/A')}"},
                        {"type": "mrkdwn", "text": f"*Performance:* {data.get('performance', 'N/A')}"},
                    ]
                }
            ]
        
        elif notification_type == NotificationType.DRIFT_DETECTED:
            base_message["blocks"] = [
                {
                    "type": "header",
                    "text": {"type": "plain_text", "text": "📉 Data Drift Detected"}
                },
                {
                    "type": "section",
                    "fields": [
                        {"type": "mrkdwn", "text": f"*Drift Score:* {data.get('drift_score', 0):.2%}"},
                        {"type": "mrkdwn", "text": f"*Threshold:* {data.get('threshold', 0):.2%}"},
                        {"type": "mrkdwn", "text": f"*Type:* {data.get('drift_type', 'N/A')}"},
                    ]
                }
            ]
        
        elif notification_type == NotificationType.INFLUENCER_TAG:
            base_message["blocks"] = [
                {
                    "type": "header",
                    "text": {"type": "plain_text", "text": "📸 Influencer Tag Detected"}
                },
                {
                    "type": "section",
                    "text": {"type": "mrkdwn", "text": f"*Caption:* {data.get('caption', 'N/A')}"},
                },
                {
                    "type": "image",
                    "image_url": data.get("image_url", ""),
                    "alt_text": "Influencer image"
                }
            ]
        
        elif notification_type == NotificationType.DAILY_REPORT:
            base_message["blocks"] = [
                {
                    "type": "header",
                    "text": {"type": "plain_text", "text": "📊 Daily AI Revenue Report"}
                },
                {
                    "type": "section",
                    "fields": [
                        {"type": "mrkdwn", "text": f"*AI Revenue Share:* {data.get('ai_revenue_share', '0%')}"},
                        {"type": "mrkdwn", "text": f"*Avg Cart Uplift:* {data.get('avg_cart_uplift', '$0')}"},
                        {"type": "mrkdwn", "text": f"*Top Recommendation:* {data.get('top_recommended_item', 'N/A')}"},
                        {"type": "mrkdwn", "text": f"*Conversion Delta:* {data.get('conversion_delta', '0%')}"},
                    ]
                }
            ]
        
        elif notification_type == NotificationType.WEEKLY_REPORT:
            base_message["blocks"] = [
                {
                    "type": "header",
                    "text": {"type": "plain_text", "text": "📘 Weekly New Learnings"}
                },
                {
                    "type": "section",
                    "text": {"type": "mrkdwn", "text": data.get("insights", "No insights available")}
                }
            ]
        
        return base_message
    
    async def send_notification(
        self,
        notification_type: NotificationType,
        data: Dict[str, Any],
        channel: Optional[str] = None
    ) -> bool:
        """Send notification to Slack."""
        if not self.webhook_url and not self.bot_token:
            logger.warning("Slack not configured, skipping notification")
            return False
        
        try:
            message = self._format_message(notification_type, data)
            target_channel = channel or self._get_channel(notification_type)
            
            # Add channel if using webhook
            if self.webhook_url:
                message["channel"] = target_channel
            
            async with httpx.AsyncClient(timeout=10.0) as client:
                if self.webhook_url:
                    response = await client.post(
                        self.webhook_url,
                        json=message,
                    )
                elif self.bot_token:
                    # Use Slack Web API
                    response = await client.post(
                        "https://slack.com/api/chat.postMessage",
                        headers={"Authorization": f"Bearer {self.bot_token}"},
                        json={
                            "channel": target_channel,
                            **message
                        },
                    )
                else:
                    raise SlackError("No Slack configuration found")
                
                response.raise_for_status()
                logger.info(f"Slack notification sent: {notification_type.value}")
                return True
                
        except Exception as e:
            logger.error(f"Failed to send Slack notification: {e}", exc_info=True)
            raise SlackError(f"Failed to send notification: {e}")


# Global notifier instance
slack_notifier = SlackNotifier()
