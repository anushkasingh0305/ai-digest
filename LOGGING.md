# Structured Logging Guide

## Overview

The AI Digest system uses **structured JSON logging** to provide comprehensive visibility into pipeline execution, delivery operations, and system health. All logs are automatically formatted as JSON with timestamps, log levels, component names, and contextual metadata.

## Quick Start

### Command-Line Usage

```bash
# Default (INFO level)
python -m src.cli.main

# With DEBUG logging
python -m src.cli.main --log-level DEBUG

# Custom log file location
python -m src.cli.main --log-file /var/log/ai_digest.log

# Full example
python -m src.cli.main --deliver --log-level DEBUG --log-file logs/custom.log
```

### Environment Variables

Set `LOG_LEVEL` in your `.env` file:

```bash
LOG_LEVEL=DEBUG  # DEBUG, INFO, WARNING, ERROR, CRITICAL (default: INFO)
```

## Log Format

All logs are structured JSON with the following schema:

```json
{
  "timestamp": "2026-01-29T14:30:45.123456",
  "level": "INFO",
  "logger": "src.workflows.pipeline",
  "message": "Pipeline run started",
  "module": "pipeline",
  "function": "run",
  "line": 42,
  "component": "pipeline",
  "deliver": true,
  "exception": null
}
```

### Key Fields

- **timestamp**: ISO 8601 UTC timestamp
- **level**: Log level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
- **logger**: Python logger name (module path)
- **message**: Human-readable log message
- **module**: Python module name
- **function**: Function name where log originated
- **line**: Line number in source code
- **component**: Logical component (e.g., "pipeline", "delivery.email", "server.metrics")
- **exception**: Stack trace (only for ERROR/CRITICAL with exceptions)
- **custom fields**: Additional contextual metadata from the log statement

## Components & Log Examples

### Pipeline Component

```json
{"timestamp": "2026-01-29T14:30:45.123456", "level": "INFO", "message": "Pipeline run started", "component": "pipeline", "deliver": true}
{"timestamp": "2026-01-29T14:30:45.234567", "level": "INFO", "message": "Fetching items from adapter", "component": "pipeline.ingest", "adapter": "placeholder", "hours": 24}
{"timestamp": "2026-01-29T14:30:45.345678", "level": "INFO", "message": "Ingested 5 items", "component": "pipeline.ingest", "item_count": 5}
{"timestamp": "2026-01-29T14:30:45.456789", "level": "INFO", "message": "Starting embedding phase", "component": "pipeline.embedding"}
{"timestamp": "2026-01-29T14:30:45.567890", "level": "INFO", "message": "Wrote digest to out/digest.json", "component": "pipeline.output", "path": "out/digest.json"}
```

### Delivery Email Component

```json
{"timestamp": "2026-01-29T14:30:46.123456", "level": "INFO", "message": "Delivering via email", "component": "pipeline.delivery.email", "recipient": "user@example.com"}
{"timestamp": "2026-01-29T14:30:46.234567", "level": "DEBUG", "message": "Preparing email to user@example.com", "component": "delivery.email", "body_length": 1234, "subject": "Daily Digest"}
{"timestamp": "2026-01-29T14:30:46.345678", "level": "INFO", "message": "Sending email via smtp.gmail.com:587", "component": "delivery.email", "smtp_host": "smtp.gmail.com", "smtp_port": 587}
{"timestamp": "2026-01-29T14:30:47.456789", "level": "INFO", "message": "Email sent successfully to user@example.com", "component": "delivery.email", "recipient": "user@example.com"}
```

### Delivery Telegram Component

```json
{"timestamp": "2026-01-29T14:30:48.123456", "level": "INFO", "message": "Sending Telegram message to 123456789", "component": "delivery.telegram", "chat_id": "123456789"}
{"timestamp": "2026-01-29T14:30:49.234567", "level": "INFO", "message": "Telegram message sent successfully to 123456789", "component": "delivery.telegram", "chat_id": "123456789"}
```

### Error Examples

```json
{"timestamp": "2026-01-29T14:30:50.123456", "level": "WARNING", "message": "DELIVERY_EMAIL not configured, skipping email delivery", "component": "pipeline.delivery.email"}
{"timestamp": "2026-01-29T14:30:51.234567", "level": "ERROR", "message": "Email delivery failed: Connection timeout", "component": "delivery.email", "error": "Connection timeout", "recipient": "user@example.com", "exception": "...stack trace..."}
```

## Log Levels

### DEBUG
Detailed diagnostic information for troubleshooting.

```python
logger.debug("Embedding phase completed", extra={"component": "pipeline.embedding"})
```

### INFO (Default)
General informational messages about system operations.

```python
logger.info("Pipeline run started", extra={"deliver": True, "component": "pipeline"})
```

### WARNING
Potentially problematic situations (missing configs, retries).

```python
logger.warning("DELIVERY_EMAIL not configured, skipping email delivery", 
               extra={"component": "pipeline.delivery.email"})
```

### ERROR
Errors that don't prevent execution but indicate problems.

```python
logger.error(f"Email delivery failed: {str(e)}", 
             extra={"component": "delivery.email", "error": str(e)},
             exc_info=True)
```

### CRITICAL
Severe errors that may cause system failure.

```python
logger.critical("Database connection failed", 
                extra={"component": "database"},
                exc_info=True)
```

## Integration with Monitoring

### Prometheus Metrics
Logs complement Prometheus metrics:
- **Metrics**: Aggregated counts (emails sent, digests run)
- **Logs**: Detailed per-run information (recipient, errors, timing)

### Log Output Locations

**Console**: All logs to stdout (configurable via environment)
**File**: `logs/ai_digest.log` with rotation (10MB files, 5 backups)

### Parsing Logs

Since all logs are JSON, parse them easily:

```bash
# Pretty-print logs
cat logs/ai_digest.log | python -m json.tool | head -50

# Filter by component
cat logs/ai_digest.log | python -c "import sys, json; [print(json.dumps(j)) for l in sys.stdin if 'delivery' in (j := json.loads(l)).get('component', '')]"

# Filter by level
cat logs/ai_digest.log | python -c "import sys, json; [print(json.dumps(j)) for l in sys.stdin if (j := json.loads(l))['level'] == 'ERROR']"
```

## Docker Logging

In Docker, logs are written to both stdout and `logs/ai_digest.log` inside the container:

```bash
# View logs from running container
docker-compose logs app

# View logs with tail
docker-compose logs --tail 50 -f app
```

Mount the logs directory for persistent access:

```yaml
volumes:
  - ./logs:/app/logs  # Add to docker-compose.yml
```

## Best Practices

1. **Use contextual extra fields**: Include component names and relevant metadata
   ```python
   logger.info("Item processed", extra={"component": "ingest", "item_id": "123", "source": "reddit"})
   ```

2. **Log entry and exit**: Track function boundaries for better tracing
   ```python
   logger.debug("Starting adapter fetch", extra={"adapter": "hacker_news"})
   # ... code ...
   logger.info("Adapter fetch completed", extra={"adapter": "hacker_news", "count": 10})
   ```

3. **Include errors with context**: Always use `exc_info=True` for exceptions
   ```python
   except Exception as e:
       logger.error(f"Operation failed: {str(e)}", 
                    extra={"component": "pipeline", "error": str(e)},
                    exc_info=True)
   ```

4. **Avoid logging sensitive data**: Don't log API keys, passwords, or PII
   ```python
   # BAD
   logger.info(f"Using API key {api_key}")
   
   # GOOD
   logger.info("Using API key", extra={"has_key": bool(api_key)})
   ```

## Performance

Logging has minimal performance impact:
- JSON formatting is fast (json.dumps)
- File I/O uses buffering
- Rotating file handler prevents unbounded growth
- DEBUG logs are suppressed in production (INFO level)

## Troubleshooting

### Logs not appearing

1. Check LOG_LEVEL environment variable:
   ```bash
   echo $LOG_LEVEL  # or $env:LOG_LEVEL on Windows
   ```

2. Verify logs directory exists:
   ```bash
   mkdir -p logs
   ```

3. Check file permissions:
   ```bash
   ls -la logs/
   ```

### Logs too verbose

Set LOG_LEVEL=WARNING or ERROR to reduce verbosity:

```bash
python -m src.cli.main --log-level WARNING
```

### Logs not rotating

The rotating file handler automatically creates backups when logs exceed 10MB. Check that the logs directory has write permissions.

## Future Enhancements

- **Loki integration**: Ship logs to Grafana Loki for centralized storage
- **Custom formatters**: Add colorized console output
- **Sampling**: Reduce verbosity in production with intelligent sampling
- **Metrics from logs**: Extract metrics directly from structured logs
