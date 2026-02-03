"""
Webhook service for sending digest notifications to external services.

Supports:
- Slack webhooks
- Discord webhooks
- Generic HTTP webhooks
"""

import json
import asyncio
from typing import Optional, List, Dict, Any
from datetime import datetime
from dataclasses import dataclass, field, asdict
from enum import Enum
from . import metrics as metrics_module
from ..logging_config import get_logger

logger = get_logger(__name__)


class WebhookType(str, Enum):
    """Supported webhook types."""

    SLACK = "slack"
    DISCORD = "discord"
    GENERIC = "generic"


@dataclass
class Webhook:
    """Webhook configuration."""

    id: str
    name: str
    type: WebhookType
    url: str
    enabled: bool = True
    headers: Dict[str, str] = field(default_factory=dict)
    payload_template: Optional[str] = None
    created_at: str = field(default_factory=lambda: datetime.utcnow().isoformat())
    updated_at: str = field(default_factory=lambda: datetime.utcnow().isoformat())
    last_triggered_at: Optional[str] = None
    trigger_count: int = 0

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return asdict(self)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Webhook":
        """Create from dictionary."""
        if isinstance(data.get("type"), str):
            data["type"] = WebhookType(data["type"])
        return cls(**data)


class WebhookManager:
    """Manager for webhooks with persistence."""

    def __init__(self, storage_path: str = "webhooks.json"):
        """
        Initialize webhook manager.

        Args:
            storage_path: Path to JSON file for persistence.
        """
        self.storage_path = storage_path
        self.webhooks: Dict[str, Webhook] = {}
        self._load_webhooks()

    def _load_webhooks(self) -> None:
        """Load webhooks from storage."""
        try:
            with open(self.storage_path, "r") as f:
                data = json.load(f)
                self.webhooks = {
                    webhook_id: Webhook.from_dict(webhook_data)
                    for webhook_id, webhook_data in data.items()
                }
            logger.info(
                f"Loaded {len(self.webhooks)} webhooks",
                extra={"component": "webhooks.manager", "count": len(self.webhooks)},
            )
        except FileNotFoundError:
            logger.debug(
                "Webhooks file not found, starting with empty list",
                extra={"component": "webhooks.manager"},
            )
            self.webhooks = {}

    def _save_webhooks(self) -> None:
        """Save webhooks to storage."""
        with open(self.storage_path, "w") as f:
            data = {
                webhook_id: webhook.to_dict()
                for webhook_id, webhook in self.webhooks.items()
            }
            json.dump(data, f, indent=2)
        logger.debug(
            f"Saved {len(self.webhooks)} webhooks",
            extra={"component": "webhooks.manager", "count": len(self.webhooks)},
        )

    def create_webhook(
        self,
        webhook_id: str,
        name: str,
        type: WebhookType,
        url: str,
        headers: Optional[Dict[str, str]] = None,
        payload_template: Optional[str] = None,
    ) -> Webhook:
        """
        Create a new webhook.

        Args:
            webhook_id: Unique webhook ID.
            name: Human-readable webhook name.
            type: Webhook type (slack, discord, generic).
            url: Webhook URL.
            headers: Optional custom headers.
            payload_template: Optional custom payload template (JSON).

        Returns:
            Created Webhook object.

        Raises:
            ValueError: If webhook_id already exists.
        """
        if webhook_id in self.webhooks:
            raise ValueError(f"Webhook {webhook_id} already exists")

        webhook = Webhook(
            id=webhook_id,
            name=name,
            type=type,
            url=url,
            headers=headers or {},
            payload_template=payload_template,
        )

        self.webhooks[webhook_id] = webhook
        self._save_webhooks()

        logger.info(
            f"Created webhook {webhook_id}",
            extra={
                "component": "webhooks.manager",
                "webhook_id": webhook_id,
                "webhook_type": type.value,
                "webhook_name": name,
            },
        )

        return webhook

    def get_webhook(self, webhook_id: str) -> Optional[Webhook]:
        """Get webhook by ID."""
        return self.webhooks.get(webhook_id)

    def list_webhooks(self) -> List[Webhook]:
        """List all webhooks."""
        return list(self.webhooks.values())

    def update_webhook(
        self,
        webhook_id: str,
        name: Optional[str] = None,
        url: Optional[str] = None,
        enabled: Optional[bool] = None,
        headers: Optional[Dict[str, str]] = None,
        payload_template: Optional[str] = None,
    ) -> Webhook:
        """
        Update a webhook.

        Args:
            webhook_id: Webhook to update.
            name: New name (optional).
            url: New URL (optional).
            enabled: Enable/disable webhook (optional).
            headers: New headers (optional).
            payload_template: New payload template (optional).

        Returns:
            Updated Webhook object.

        Raises:
            ValueError: If webhook not found.
        """
        webhook = self.webhooks.get(webhook_id)
        if not webhook:
            raise ValueError(f"Webhook {webhook_id} not found")

        if name is not None:
            webhook.name = name
        if url is not None:
            webhook.url = url
        if enabled is not None:
            webhook.enabled = enabled
        if headers is not None:
            webhook.headers = headers
        if payload_template is not None:
            webhook.payload_template = payload_template

        webhook.updated_at = datetime.utcnow().isoformat()

        self._save_webhooks()

        logger.info(
            f"Updated webhook {webhook_id}",
            extra={
                "component": "webhooks.manager",
                "webhook_id": webhook_id,
                "fields_updated": [
                    k for k, v in [
                        ("name", name),
                        ("url", url),
                        ("enabled", enabled),
                        ("headers", headers),
                        ("payload_template", payload_template),
                    ]
                    if v is not None
                ],
            },
        )

        return webhook

    def delete_webhook(self, webhook_id: str) -> bool:
        """
        Delete a webhook.

        Args:
            webhook_id: Webhook to delete.

        Returns:
            True if deleted, False if not found.
        """
        if webhook_id not in self.webhooks:
            return False

        del self.webhooks[webhook_id]
        self._save_webhooks()

        logger.info(
            f"Deleted webhook {webhook_id}",
            extra={"component": "webhooks.manager", "webhook_id": webhook_id},
        )

        return True

    def toggle_webhook(self, webhook_id: str) -> Webhook:
        """
        Toggle webhook enabled/disabled status.

        Args:
            webhook_id: Webhook to toggle.

        Returns:
            Updated Webhook object.

        Raises:
            ValueError: If webhook not found.
        """
        webhook = self.webhooks.get(webhook_id)
        if not webhook:
            raise ValueError(f"Webhook {webhook_id} not found")

        webhook.enabled = not webhook.enabled
        webhook.updated_at = datetime.utcnow().isoformat()

        self._save_webhooks()

        logger.info(
            f"Toggled webhook {webhook_id} to {webhook.enabled}",
            extra={
                "component": "webhooks.manager",
                "webhook_id": webhook_id,
                "enabled": webhook.enabled,
            },
        )

        return webhook


class WebhookSender:
    """Sends notifications to webhooks."""

    def __init__(self, manager: WebhookManager):
        """
        Initialize webhook sender.

        Args:
            manager: WebhookManager instance.
        """
        self.manager = manager

    def _build_slack_payload(
        self, title: str, content: str, digest_id: str
    ) -> Dict[str, Any]:
        """Build Slack webhook payload."""
        return {
            "blocks": [
                {
                    "type": "header",
                    "text": {"type": "plain_text", "text": "📰 New Digest"},
                },
                {
                    "type": "section",
                    "text": {"type": "mrkdwn", "text": f"*{title}*\n{content[:500]}"},
                },
                {
                    "type": "actions",
                    "elements": [
                        {
                            "type": "button",
                            "text": {"type": "plain_text", "text": "View Digest"},
                            "url": f"/digests/{digest_id}",
                        }
                    ],
                },
            ]
        }

    def _build_discord_payload(
        self, title: str, content: str, digest_id: str
    ) -> Dict[str, Any]:
        """Build Discord webhook payload."""
        return {
            "embeds": [
                {
                    "title": "📰 " + title,
                    "description": content[:500],
                    "color": 3447003,
                    "url": f"/digests/{digest_id}",
                    "footer": {"text": "AI Digest"},
                    "timestamp": datetime.utcnow().isoformat() + "Z",
                }
            ]
        }

    def _build_generic_payload(
        self, title: str, content: str, digest_id: str
    ) -> Dict[str, Any]:
        """Build generic webhook payload."""
        return {
            "type": "digest_notification",
            "digest_id": digest_id,
            "title": title,
            "content": content,
            "timestamp": datetime.utcnow().isoformat(),
        }

    async def send_to_webhook(
        self, webhook: Webhook, title: str, content: str, digest_id: str
    ) -> bool:
        """
        Send notification to a webhook.

        Args:
            webhook: Webhook to send to.
            title: Digest title.
            content: Digest content.
            digest_id: Digest ID.

        Returns:
            True if sent successfully, False otherwise.
        """
        if not webhook.enabled:
            logger.debug(
                f"Webhook {webhook.id} is disabled, skipping",
                extra={"component": "webhooks.sender", "webhook_id": webhook.id},
            )
            return False

        try:
            # Build payload based on webhook type
            if webhook.type == WebhookType.SLACK:
                payload = self._build_slack_payload(title, content, digest_id)
            elif webhook.type == WebhookType.DISCORD:
                payload = self._build_discord_payload(title, content, digest_id)
            else:
                payload = self._build_generic_payload(title, content, digest_id)

            # Use custom payload template if provided
            if webhook.payload_template:
                try:
                    template = json.loads(webhook.payload_template)
                    payload.update(template)
                except json.JSONDecodeError:
                    logger.warning(
                        f"Invalid JSON in payload template for {webhook.id}",
                        extra={"component": "webhooks.sender", "webhook_id": webhook.id},
                    )

            # Send to webhook
            logger.debug(
                f"Sending webhook {webhook.id} for digest {digest_id}",
                extra={
                    "component": "webhooks.sender",
                    "webhook_id": webhook.id,
                    "digest_id": digest_id,
                    "webhook_type": webhook.type.value,
                },
            )

            try:
                import aiohttp
            except ImportError:
                logger.error(
                    "aiohttp is required for webhooks but is not installed",
                    extra={"component": "webhooks.sender", "webhook_id": webhook.id},
                )
                metrics_module.delivery_failures_total.inc()
                return False

            async with aiohttp.ClientSession() as session:
                headers = {
                    "Content-Type": "application/json",
                    **webhook.headers,
                }

                async with session.post(
                    webhook.url,
                    json=payload,
                    headers=headers,
                    timeout=aiohttp.ClientTimeout(total=10),
                ) as response:
                    if response.status in (200, 201, 204):
                        webhook.last_triggered_at = datetime.utcnow().isoformat()
                        webhook.trigger_count += 1
                        self.manager._save_webhooks()

                        metrics_module.delivery_webhooks_success_total.inc()
                        logger.info(
                            f"Webhook {webhook.id} sent successfully",
                            extra={
                                "component": "webhooks.sender",
                                "webhook_id": webhook.id,
                                "digest_id": digest_id,
                                "status_code": response.status,
                            },
                        )
                        return True
                    else:
                        logger.error(
                            f"Webhook {webhook.id} failed with status {response.status}",
                            extra={
                                "component": "webhooks.sender",
                                "webhook_id": webhook.id,
                                "digest_id": digest_id,
                                "status_code": response.status,
                            },
                        )
                        metrics_module.delivery_failures_total.inc()
                        return False

        except asyncio.TimeoutError:
            logger.error(
                f"Webhook {webhook.id} request timed out",
                extra={
                    "component": "webhooks.sender",
                    "webhook_id": webhook.id,
                    "digest_id": digest_id,
                },
            )
            metrics_module.delivery_failures_total.inc()
            return False
        except Exception as e:
            logger.error(
                f"Webhook {webhook.id} send failed: {str(e)}",
                extra={
                    "component": "webhooks.sender",
                    "webhook_id": webhook.id,
                    "digest_id": digest_id,
                    "error": str(e),
                },
                exc_info=True,
            )
            metrics_module.delivery_failures_total.inc()
            return False

    async def send_to_all(
        self, title: str, content: str, digest_id: str
    ) -> Dict[str, bool]:
        """
        Send notification to all enabled webhooks.

        Args:
            title: Digest title.
            content: Digest content.
            digest_id: Digest ID.

        Returns:
            Dictionary mapping webhook ID to success status.
        """
        webhooks = self.manager.list_webhooks()
        enabled_webhooks = [w for w in webhooks if w.enabled]

        if not enabled_webhooks:
            logger.debug(
                "No enabled webhooks to send to",
                extra={"component": "webhooks.sender", "digest_id": digest_id},
            )
            return {}

        logger.info(
            f"Sending to {len(enabled_webhooks)} webhooks for digest {digest_id}",
            extra={
                "component": "webhooks.sender",
                "digest_id": digest_id,
                "webhook_count": len(enabled_webhooks),
            },
        )

        results = {}
        tasks = [
            self.send_to_webhook(webhook, title, content, digest_id)
            for webhook in enabled_webhooks
        ]

        responses = await asyncio.gather(*tasks)
        for webhook, success in zip(enabled_webhooks, responses):
            results[webhook.id] = success

        return results


# Singleton instance
_webhook_manager: Optional[WebhookManager] = None
_webhook_sender: Optional[WebhookSender] = None


def get_webhook_manager() -> WebhookManager:
    """Get or create webhook manager singleton."""
    global _webhook_manager
    if _webhook_manager is None:
        _webhook_manager = WebhookManager()
    return _webhook_manager


def get_webhook_sender() -> WebhookSender:
    """Get or create webhook sender singleton."""
    global _webhook_sender
    if _webhook_sender is None:
        _webhook_sender = WebhookSender(get_webhook_manager())
    return _webhook_sender
