import asyncio
import pytest
from unittest.mock import patch, AsyncMock

from src.services import delivery

def test_send_email_skips_when_no_smtp_host(monkeypatch):
    import asyncio
    monkeypatch.delenv('SMTP_HOST', raising=False)
    res = asyncio.run(delivery.send_email('sub','body','to@example.com'))
    assert res is False

@patch('aiosmtplib.send', new_callable=AsyncMock)
def test_send_email_calls_aiosmtplib(mock_send, monkeypatch):
    import asyncio
    monkeypatch.setenv('SMTP_HOST','smtp.example')
    monkeypatch.setenv('SMTP_PORT','587')
    monkeypatch.setenv('SMTP_USER','user')
    monkeypatch.setenv('SMTP_PASS','pass')
    mock_send.return_value = {}
    res = asyncio.run(delivery.send_email('s','b','to@example.com'))
    assert res is True
    assert mock_send.called


@patch('aiosmtplib.send', new_callable=AsyncMock)
def test_send_email_attaches_html_alternative(mock_send, monkeypatch):
    import asyncio
    from email.message import EmailMessage
    monkeypatch.setenv('SMTP_HOST','smtp.example')
    monkeypatch.setenv('SMTP_PORT','587')
    monkeypatch.setenv('SMTP_USER','user')
    monkeypatch.setenv('SMTP_PASS','pass')
    mock_send.return_value = {}
    html = '<html><body><p><b>Hi</b></p></body></html>'
    res = asyncio.run(delivery.send_email('s','b','to@example.com', html=html))
    assert res is True
    assert mock_send.called
    sent_msg = mock_send.call_args[0][0]
    # ensure HTML alternative present
    html_part = sent_msg.get_body(preferencelist=('html',))
    assert html_part is not None
    assert 'Hi' in html_part.get_content()

@patch('src.services.delivery.Bot')
def test_send_telegram_skips_when_not_configured(mock_bot, monkeypatch):
    import asyncio
    monkeypatch.delenv('TELEGRAM_TOKEN', raising=False)
    monkeypatch.delenv('TELEGRAM_CHAT_ID', raising=False)
    res = asyncio.run(delivery.send_telegram('hi'))
    assert res is False

@patch('src.services.delivery.Bot')
def test_send_telegram_calls_bot(mock_bot, monkeypatch):
    import asyncio
    mock_instance = AsyncMock()
    mock_bot.return_value = mock_instance
    monkeypatch.setenv('TELEGRAM_TOKEN','tok')
    monkeypatch.setenv('TELEGRAM_CHAT_ID','12345')
    res = asyncio.run(delivery.send_telegram('hello'))
    assert res is True
    mock_bot.assert_called()
