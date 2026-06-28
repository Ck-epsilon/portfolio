# Author: Ck.epsilon & Chaos (AI Programming Assistant)
"""
Alerting module: email (SMTP) and Slack webhook notifications.
Reports task completion, failures, and system events.
"""

import smtplib
import logging
from email.mime.text import MIMEText
from typing import Optional
import os

logger = logging.getLogger(__name__)


class Alerter:
    """Multi-channel alerter: email + Slack webhook.

    Email config via env vars:
        SMTP_HOST, SMTP_PORT, SMTP_USER, SMTP_PASSWORD, ALERT_EMAIL_TO

    Slack config via env var:
        SLACK_WEBHOOK_URL
    """

    def __init__(self):
        self.smtp_host = os.getenv("SMTP_HOST", "smtp.qq.com")
        self.smtp_port = int(os.getenv("SMTP_PORT", "587"))
        self.smtp_user = os.getenv("SMTP_USER", "")
        self.smtp_password = os.getenv("SMTP_PASSWORD", "")
        self.alert_email_to = os.getenv("ALERT_EMAIL_TO", "")
        self.slack_webhook = os.getenv("SLACK_WEBHOOK_URL", "")

    def send_email(self, subject: str, body: str, to: Optional[str] = None) -> bool:
        """Send email alert via SMTP. Returns True on success."""
        if not self.smtp_user or not self.smtp_password:
            logger.warning("SMTP not configured, skipping email alert")
            return False
        recipient = to or self.alert_email_to
        if not recipient:
            logger.warning("No recipient configured")
            return False

        msg = MIMEText(body, "plain", "utf-8")
        msg["Subject"] = subject
        msg["From"] = self.smtp_user
        msg["To"] = recipient

        try:
            with smtplib.SMTP(self.smtp_host, self.smtp_port, timeout=10) as s:
                s.starttls()
                s.login(self.smtp_user, self.smtp_password)
                s.send_message(msg)
            logger.info("Alert email sent: %s → %s", subject, recipient)
            return True
        except Exception as e:
            logger.error("Failed to send email alert: %s", e)
            return False

    async def send_slack(self, text: str) -> bool:
        """Send Slack webhook message. Returns True on success."""
        if not self.slack_webhook:
            logger.info("Slack webhook not configured")
            return False
        import httpx
        try:
            async with httpx.AsyncClient(timeout=10) as client:
                resp = await client.post(self.slack_webhook, json={"text": text})
                if resp.status_code == 200:
                    return True
                logger.error("Slack webhook failed: %d %s", resp.status_code, resp.text)
                return False
        except Exception as e:
            logger.error("Slack webhook error: %s", e)
            return False

    def notify_task_complete(self, task_id: str, agent_name: str, result_preview: str = ""):
        """Send notifications on task completion."""
        subject = f"[AI Workbench] Task {task_id} completed"
        body = f"Agent: {agent_name}\nTask: {task_id}\nResult: {result_preview[:500]}"
        self.send_email(subject, body)

    def notify_task_failed(self, task_id: str, agent_name: str, error: str):
        """Send notifications on task failure."""
        subject = f"[AI Workbench] Task {task_id} FAILED"
        body = f"Agent: {agent_name}\nTask: {task_id}\nError: {error}"
        self.send_email(subject, body)


# Global alerter instance
alerter = Alerter()
