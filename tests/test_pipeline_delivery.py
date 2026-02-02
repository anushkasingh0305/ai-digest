import asyncio
from unittest.mock import AsyncMock, patch

from src.workflows.pipeline import Pipeline


def test_pipeline_delivery_triggers_sends(monkeypatch):
    # Mock delivery functions to avoid network
    mock_email = AsyncMock(return_value=True)
    mock_telegram = AsyncMock(return_value=True)
    monkeypatch.setenv('DELIVERY_EMAIL', 'to@example.com')
    monkeypatch.setenv('TELEGRAM_CHAT_ID', '123456789')

    with patch('src.services.delivery.send_email', mock_email), patch(
        'src.services.delivery.send_telegram', mock_telegram
    ):
        asyncio.run(Pipeline().run(deliver=True))

    assert mock_email.called
    assert mock_telegram.called
