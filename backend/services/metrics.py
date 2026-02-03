from prometheus_client import Counter, Histogram

ai_digest_runs_total = Counter('ai_digest_runs_total', 'Number of pipeline runs')
items_ingested_total = Counter('ai_digest_items_ingested_total', 'Number of items ingested')
embeddings_seconds = Histogram('ai_digest_embeddings_seconds', 'Time spent generating embeddings')

# Delivery metrics
delivery_email_success_total = Counter('ai_digest_delivery_email_success_total', 'Number of successful email deliveries')
delivery_telegram_success_total = Counter('ai_digest_delivery_telegram_success_total', 'Number of successful telegram deliveries')
delivery_failures_total = Counter('ai_digest_delivery_failures_total', 'Number of delivery failures (any channel)')

