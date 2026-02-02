import asyncio
import logging
import json
import os
import uuid
from ..tools.adapters_placeholder import PlaceholderAdapter
from ..services import metrics as metrics_module
from ..services import delivery as delivery_module
from ..services.webhooks import get_webhook_sender
from ..formatters import format_digest_text, format_digest_html
from ..logging_config import get_logger

logger = get_logger(__name__)


class Pipeline:
    def __init__(self):
        self.adapter = PlaceholderAdapter()
        logger.info("Pipeline initialized", extra={"component": "pipeline"})
        self.webhook_sender = get_webhook_sender()

    async def run(self, deliver: bool = False):
        """
        Run the digest pipeline: ingest, embed, deduplicate, evaluate, format, deliver.
        
        Args:
            deliver: Whether to send digest via email and Telegram.
        """
        logger.info(
            "Pipeline run started",
            extra={"deliver": deliver, "component": "pipeline"},
        )

        try:
            # Record a run
            metrics_module.ai_digest_runs_total.inc()
            logger.debug("Run metric incremented", extra={"component": "pipeline"})

            # Fetch items from adapter
            logger.info(
                "Fetching items from adapter",
                extra={"adapter": "placeholder", "hours": 24},
            )
            items = await self.adapter.fetch_items(hours=24)
            logger.info(
                f"Ingested {len(items)} items",
                extra={
                    "item_count": len(items),
                    "component": "pipeline.ingest",
                },
            )
            metrics_module.items_ingested_total.inc(len(items))

            # Mock embedding/deduplication/evaluation
            logger.info(
                "Starting embedding phase",
                extra={"component": "pipeline.embedding"},
            )
            with metrics_module.embeddings_seconds.time():
                await asyncio.sleep(0.1)
            logger.debug(
                "Embedding phase completed",
                extra={"component": "pipeline.embedding"},
            )

            # Create digest
            digest_id = str(uuid.uuid4())
            digest = {"id": digest_id, "items": items}
            out_path = "out/digest.json"
            os.makedirs("out", exist_ok=True)
            with open(out_path, "w", encoding="utf-8") as f:
                json.dump(digest, f, indent=2)
            logger.info(
                f"Wrote digest to {out_path}",
                extra={"path": out_path, "component": "pipeline.output"},
            )

            # Delivery phase
            if deliver:
                logger.info(
                    "Deliver flag set, proceeding with delivery",
                    extra={"component": "pipeline.delivery"},
                )
                body = format_digest_text(digest)
                html = format_digest_html(digest)
                logger.debug(
                    "Digest formatted for delivery",
                    extra={"body_length": len(body), "html_length": len(html)},
                )

                # Email delivery
                delivery_email = os.getenv("DELIVERY_EMAIL", "").strip()
                if delivery_email:
                    try:
                        logger.info(
                            f"Sending email to {delivery_email}",
                            extra={
                                "recipient": delivery_email,
                                "component": "pipeline.delivery.email",
                            },
                        )
                        await delivery_module.send_email(
                            subject="Daily Digest",
                            body=body,
                            to=delivery_email,
                            html=html,
                        )
                        logger.info(
                            "Email delivered successfully",
                            extra={"component": "pipeline.delivery.email"},
                        )
                    except Exception as e:
                        logger.error(
                            f"Email delivery failed: {str(e)}",
                            extra={
                                "component": "pipeline.delivery.email",
                                "error": str(e),
                            },
                            exc_info=True,
                        )
                else:
                    logger.warning(
                        "DELIVERY_EMAIL not configured, skipping email delivery",
                        extra={"component": "pipeline.delivery.email"},
                    )

                # Telegram delivery
                telegram_chat_id = os.getenv("TELEGRAM_CHAT_ID", "").strip()
                if telegram_chat_id:
                    try:
                        logger.info(
                            f"Sending Telegram message to {telegram_chat_id}",
                            extra={
                                "chat_id": telegram_chat_id,
                                "component": "pipeline.delivery.telegram",
                            },
                        )
                        await delivery_module.send_telegram(body)
                        logger.info(
                            "Telegram message delivered successfully",
                            extra={"component": "pipeline.delivery.telegram"},
                        )
                    except Exception as e:
                        logger.error(
                            f"Telegram delivery failed: {str(e)}",
                            extra={
                                "component": "pipeline.delivery.telegram",
                                "error": str(e),
                            },
                            exc_info=True,
                        )
                else:
                    logger.warning(
                        "TELEGRAM_CHAT_ID not configured, skipping Telegram delivery",
                        extra={"component": "pipeline.delivery.telegram"},
                    )

                # Webhook delivery (send to all enabled webhooks)
                try:
                    logger.info(
                        "Sending digest notifications to webhooks",
                        extra={"component": "pipeline.delivery.webhooks", "digest_id": digest_id},
                    )
                    results = await self.webhook_sender.send_to_all(
                        title="Daily Digest",
                        content=body,
                        digest_id=digest_id,
                    )
                    success_count = sum(1 for ok in results.values() if ok)
                    logger.info(
                        f"Webhook delivery completed: {success_count}/{len(results)} succeeded",
                        extra={
                            "component": "pipeline.delivery.webhooks",
                            "digest_id": digest_id,
                            "results": results,
                        },
                    )
                except Exception as e:
                    logger.error(
                        f"Webhook delivery failed: {str(e)}",
                        extra={"component": "pipeline.delivery.webhooks", "error": str(e)},
                        exc_info=True,
                    )

            logger.info(
                "Pipeline run completed successfully",
                extra={"item_count": len(items), "component": "pipeline"},
            )

        except Exception as e:
            logger.error(
                f"Pipeline run failed: {str(e)}",
                extra={"component": "pipeline", "error": str(e)},
                exc_info=True,
            )
            raise
