import os
import asyncio
from typing import Optional
from email.message import EmailMessage
import aiosmtplib
from telegram import Bot
from . import metrics as metrics_module

async def send_email(subject: str, body: str, to: str, sender: Optional[str] = None, html: Optional[str] = None) -> bool:
    SMTP_HOST = os.getenv('SMTP_HOST')
    SMTP_PORT = int(os.getenv('SMTP_PORT') or 587)
    SMTP_USER = os.getenv('SMTP_USER')
    SMTP_PASS = os.getenv('SMTP_PASS')
    sender = sender or SMTP_USER or 'no-reply@example.com'
    msg = EmailMessage()
    msg['From'] = sender
    msg['To'] = to
    msg['Subject'] = subject
    # set plain text
    msg.set_content(body)

    if not SMTP_HOST:
        # fallback: print and return False to indicate not sent
        print('SMTP_HOST not set; skipping send_email')
        return False

    try:
        # If caller provided html, attach it as an alternative
        if html:
            msg.add_alternative(html, subtype='html')

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
        return True
    except Exception as e:
        print(f'send_email failed: {e}')
        metrics_module.delivery_failures_total.inc()
        return False


async def send_telegram(text: str, chat_id: Optional[str] = None) -> bool:
    TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN')
    TELEGRAM_CHAT_ID = os.getenv('TELEGRAM_CHAT_ID')
    chat_id = chat_id or TELEGRAM_CHAT_ID
    if not TELEGRAM_TOKEN or not chat_id:
        print('Telegram token or chat id not configured; skipping send_telegram')
        return False
    try:
        bot = Bot(token=TELEGRAM_TOKEN)
        await bot.send_message(chat_id=chat_id, text=text)
        metrics_module.delivery_telegram_success_total.inc()
        return True
    except Exception as e:
        print(f'send_telegram failed: {e}')
        metrics_module.delivery_failures_total.inc()
        return False


# convenience sync wrappers
def send_email_sync(subject: str, body: str, to: str, sender: Optional[str] = None) -> bool:
    return asyncio.run(send_email(subject, body, to, sender))

def send_telegram_sync(text: str, chat_id: Optional[str] = None) -> bool:
    return asyncio.run(send_telegram(text, chat_id))

