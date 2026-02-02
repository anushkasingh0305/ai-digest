import os
import asyncio
from typing import Optional
from email.message import EmailMessage
import aiosmtplib
from telegram import Bot
from . import metrics as metrics_module
from ..logging_config import get_logger

logger = get_logger(__name__)


async def send_email(
    subject: str,
    body: str,
    to: str,
    sender: Optional[str] = None,
    html: Optional[str] = None,
) -> bool:
    """
    Send email via SMTP.

    Args:
        subject: Email subject.
        body: Plain text body.
        to: Recipient email address.
        sender: Sender email address (defaults to SMTP_USER or no-reply@example.com).
        html: Optional HTML body as alternative.

    Returns:
        True if sent successfully, False otherwise.
    """
    SMTP_HOST = os.getenv("SMTP_HOST")
    SMTP_PORT = int(os.getenv("SMTP_PORT") or 587)
    SMTP_USER = os.getenv("SMTP_USER")
    SMTP_PASS = os.getenv("SMTP_PASS")
    sender = sender or SMTP_USER or "no-reply@example.com"

    msg = EmailMessage()
    msg["From"] = sender
    msg["To"] = to
    msg["Subject"] = subject
    msg.set_content(body)

    if not SMTP_HOST:
        logger.warning(
            "SMTP_HOST not configured, skipping email send",
            extra={"recipient": to, "component": "delivery.email"},
        )
        return False

    try:
        logger.debug(
            f"Preparing email to {to}",
            extra={
                "recipient": to,
                "subject": subject,
                "body_length": len(body),
                "component": "delivery.email",
            },
        )

        if html:
            msg.add_alternative(html, subtype="html")
            logger.debug(
                "HTML alternative added",
                extra={
                    "recipient": to,
                    "html_length": len(html),
                    "component": "delivery.email",
                },
            )

        logger.info(
            f"Sending email via {SMTP_HOST}:{SMTP_PORT}",
            extra={
                "recipient": to,
                "smtp_host": SMTP_HOST,
                "smtp_port": SMTP_PORT,
                "component": "delivery.email",
            },
        )

        await aiosmtplib.send(
            msg,
            hostname=SMTP_HOST,
            port=SMTP_PORT,
            username=SMTP_USER,
            password=SMTP_PASS,
            start_tls=True,
            timeout=10,
        )

        metrics_module.delivery_email_success_total.inc()
        logger.info(
            f"Email sent successfully to {to}",
            extra={"recipient": to, "component": "delivery.email"},
        )
        return True

    except Exception as e:
        logger.error(
            f"Email send failed: {str(e)}",
            extra={
                "recipient": to,
                "error": str(e),
                "component": "delivery.email",
            },
            exc_info=True,
        )
        metrics_module.delivery_failures_total.inc()
        return False


async def send_telegram(text: str, chat_id: Optional[str] = None) -> bool:
    """
    Send message via Telegram.

    Args:
        text: Message text to send.
        chat_id: Telegram chat ID (defaults to TELEGRAM_CHAT_ID env var).

    Returns:
        True if sent successfully, False otherwise.
    """
    TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
    TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")
    chat_id = chat_id or TELEGRAM_CHAT_ID

    if not TELEGRAM_TOKEN or not chat_id:
        logger.warning(
            "Telegram token or chat_id not configured, skipping send",
            extra={
                "has_token": bool(TELEGRAM_TOKEN),
                "has_chat_id": bool(chat_id),
                "component": "delivery.telegram",
            },
        )
        return False

    try:
        logger.debug(
            f"Preparing Telegram message to {chat_id}",
            extra={
                "chat_id": chat_id,
                "message_length": len(text),
                "component": "delivery.telegram",
            },
        )

        bot = Bot(token=TELEGRAM_TOKEN)
        logger.info(
            f"Sending Telegram message to {chat_id}",
            extra={"chat_id": chat_id, "component": "delivery.telegram"},
        )

        await bot.send_message(chat_id=chat_id, text=text)

        metrics_module.delivery_telegram_success_total.inc()
        logger.info(
            f"Telegram message sent successfully to {chat_id}",
            extra={"chat_id": chat_id, "component": "delivery.telegram"},
        )
        return True

    except Exception as e:
        logger.error(
            f"Telegram send failed: {str(e)}",
            extra={
                "chat_id": chat_id,
                "error": str(e),
                "component": "delivery.telegram",
            },
            exc_info=True,
        )
        metrics_module.delivery_failures_total.inc()
        return False


# Convenience sync wrappers
def send_email_sync(
    subject: str, body: str, to: str, sender: Optional[str] = None
) -> bool:
    return asyncio.run(send_email(subject, body, to, sender))


def send_telegram_sync(text: str, chat_id: Optional[str] = None) -> bool:
    return asyncio.run(send_telegram(text, chat_id))
