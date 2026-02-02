# Configuration Management

AI Digest provides comprehensive configuration management via both JSON files and REST API endpoints. Configure adapters, delivery channels, scheduling, and logging without restarting the system.

## Table of Contents

- [Configuration Overview](#configuration-overview)
- [Configuration File](#configuration-file)
- [Configuration Schema](#configuration-schema)
- [REST API Endpoints](#rest-api-endpoints)
- [Configuration Examples](#configuration-examples)
- [Runtime Configuration](#runtime-configuration)
- [Best Practices](#best-practices)

## Configuration Overview

AI Digest configuration is organized into four main sections:

1. **Adapters** - Enable/disable content adapters (Reddit, RSS, ProductHunt, etc.)
2. **Delivery** - Email and Telegram delivery settings
3. **Scheduler** - Automated digest schedule configuration
4. **Logging** - Logging level, output, and file handling

Configuration persists to `config.json` in the project root and can be modified:
- Via REST API (recommended for runtime changes)
- Directly in JSON file (requires reload)
- Via environment variables (`.env`)

## Configuration File

### Location

The configuration file is stored at:
```
./config.json
```

### Default Configuration

If `config.json` doesn't exist, a default configuration is created automatically:

```json
{
  "adapters": {},
  "delivery": {
    "email_enabled": false,
    "email_address": null,
    "telegram_enabled": false,
    "telegram_chat_id": null
  },
  "scheduler": {
    "enabled": false,
    "hour": 6,
    "minute": 0,
    "delivery_enabled": true
  },
  "logging": {
    "level": "INFO",
    "file_enabled": true,
    "file_path": "logs/ai_digest.log",
    "console_enabled": true
  }
}
```

### File Format

Configuration is stored as JSON with the following structure:
- `adapters` - Dictionary of adapter configurations
- `delivery` - Delivery channel settings
- `scheduler` - Scheduler timing and settings
- `logging` - Logging configuration

## Configuration Schema

### Adapter Configuration

Each adapter can be configured individually:

```json
{
  "name": "reddit",
  "enabled": true,
  "settings": {
    "subreddits": ["python", "programming"],
    "limit": 20,
    "time_filter": "day"
  }
}
```

**Properties:**
- `name` (string) - Adapter identifier (reddit, rss, producthunt, etc.)
- `enabled` (boolean) - Whether adapter is active
- `settings` (object) - Adapter-specific configuration

### Delivery Configuration

Configure how digests are delivered:

```json
{
  "email_enabled": true,
  "email_address": "user@example.com",
  "telegram_enabled": true,
  "telegram_chat_id": "123456789"
}
```

**Properties:**
- `email_enabled` (boolean) - Enable email delivery
- `email_address` (string, nullable) - Email recipient address
- `telegram_enabled` (boolean) - Enable Telegram delivery
- `telegram_chat_id` (string, nullable) - Telegram chat ID

### Scheduler Configuration

Configure automated digest generation:

```json
{
  "enabled": true,
  "hour": 6,
  "minute": 0,
  "delivery_enabled": true
}
```

**Properties:**
- `enabled` (boolean) - Enable scheduler
- `hour` (integer 0-23) - Hour in UTC
- `minute` (integer 0-59) - Minute in UTC
- `delivery_enabled` (boolean) - Deliver digest after generation

### Logging Configuration

Configure system logging:

```json
{
  "level": "INFO",
  "file_enabled": true,
  "file_path": "logs/ai_digest.log",
  "console_enabled": true
}
```

**Properties:**
- `level` (string) - Log level: DEBUG, INFO, WARNING, ERROR, CRITICAL
- `file_enabled` (boolean) - Write logs to file
- `file_path` (string) - Path to log file
- `console_enabled` (boolean) - Output logs to console

## REST API Endpoints

All configuration endpoints return JSON and support both `GET` (retrieve) and `POST` (update) methods.

### Get Complete Configuration

**Request:**
```http
GET /api/config
```

**Response (200 OK):**
```json
{
  "adapters": {
    "reddit": {
      "name": "reddit",
      "enabled": true,
      "settings": {}
    }
  },
  "delivery": {
    "email_enabled": true,
    "email_address": "user@example.com",
    "telegram_enabled": false,
    "telegram_chat_id": null
  },
  "scheduler": {
    "enabled": true,
    "hour": 6,
    "minute": 0,
    "delivery_enabled": true
  },
  "logging": {
    "level": "INFO",
    "file_enabled": true,
    "file_path": "logs/ai_digest.log",
    "console_enabled": true
  }
}
```

### Update Complete Configuration

**Request:**
```http
POST /api/config
Content-Type: application/json

{
  "adapters": {
    "reddit": {
      "name": "reddit",
      "enabled": true,
      "settings": {}
    }
  },
  "delivery": {
    "email_enabled": true,
    "email_address": "user@example.com",
    "telegram_enabled": false,
    "telegram_chat_id": null
  },
  "scheduler": {
    "enabled": true,
    "hour": 6,
    "minute": 0,
    "delivery_enabled": true
  },
  "logging": {
    "level": "DEBUG",
    "file_enabled": true,
    "file_path": "logs/ai_digest.log",
    "console_enabled": true
  }
}
```

**Response (200 OK):**
Returns updated configuration (same format as GET)

**Error (400 Bad Request):**
```json
{
  "error": "Validation error message"
}
```

### Get Adapter Configurations

**Request:**
```http
GET /api/config/adapters
```

**Response (200 OK):**
```json
{
  "adapters": {
    "reddit": {
      "name": "reddit",
      "enabled": true,
      "settings": {}
    },
    "rss": {
      "name": "rss",
      "enabled": false,
      "settings": {}
    }
  }
}
```

### Update Adapter Configuration

**Request:**
```http
POST /api/config/adapters/reddit
Content-Type: application/json

{
  "enabled": true,
  "settings": {
    "subreddits": ["python", "programming"],
    "limit": 20
  }
}
```

**Response (200 OK):**
```json
{
  "adapter": {
    "name": "reddit",
    "enabled": true,
    "settings": {
      "subreddits": ["python", "programming"],
      "limit": 20
    }
  }
}
```

### Get Delivery Configuration

**Request:**
```http
GET /api/config/delivery
```

**Response (200 OK):**
```json
{
  "email_enabled": true,
  "email_address": "user@example.com",
  "telegram_enabled": false,
  "telegram_chat_id": null
}
```

### Update Delivery Configuration

**Request:**
```http
POST /api/config/delivery
Content-Type: application/json

{
  "email_enabled": true,
  "email_address": "user@example.com",
  "telegram_enabled": true,
  "telegram_chat_id": "123456789"
}
```

**Response (200 OK):**
Returns updated delivery configuration

### Get Scheduler Configuration

**Request:**
```http
GET /api/config/scheduler
```

**Response (200 OK):**
```json
{
  "enabled": true,
  "hour": 6,
  "minute": 0,
  "delivery_enabled": true
}
```

### Update Scheduler Configuration

**Request:**
```http
POST /api/config/scheduler
Content-Type: application/json

{
  "enabled": true,
  "hour": 8,
  "minute": 30,
  "delivery_enabled": true
}
```

**Response (200 OK):**
Returns updated scheduler configuration

### Get Logging Configuration

**Request:**
```http
GET /api/config/logging
```

**Response (200 OK):**
```json
{
  "level": "INFO",
  "file_enabled": true,
  "file_path": "logs/ai_digest.log",
  "console_enabled": true
}
```

### Update Logging Configuration

**Request:**
```http
POST /api/config/logging
Content-Type: application/json

{
  "level": "DEBUG",
  "file_enabled": true,
  "file_path": "logs/ai_digest.log",
  "console_enabled": true
}
```

**Response (200 OK):**
Returns updated logging configuration

## Configuration Examples

### Example 1: Enable Email Delivery

```bash
curl -X POST http://localhost:5000/api/config/delivery \
  -H "Content-Type: application/json" \
  -d '{
    "email_enabled": true,
    "email_address": "digest@example.com",
    "telegram_enabled": false,
    "telegram_chat_id": null
  }'
```

### Example 2: Configure Reddit Adapter

```bash
curl -X POST http://localhost:5000/api/config/adapters/reddit \
  -H "Content-Type: application/json" \
  -d '{
    "enabled": true,
    "settings": {
      "subreddits": ["python", "programming", "artificial"],
      "limit": 20,
      "time_filter": "day"
    }
  }'
```

### Example 3: Set Daily Schedule at 8 AM UTC

```bash
curl -X POST http://localhost:5000/api/config/scheduler \
  -H "Content-Type: application/json" \
  -d '{
    "enabled": true,
    "hour": 8,
    "minute": 0,
    "delivery_enabled": true
  }'
```

### Example 4: Enable Debug Logging

```bash
curl -X POST http://localhost:5000/api/config/logging \
  -H "Content-Type: application/json" \
  -d '{
    "level": "DEBUG",
    "file_enabled": true,
    "file_path": "logs/ai_digest.log",
    "console_enabled": true
  }'
```

### Example 5: Python Configuration Script

```python
import requests
import json

BASE_URL = "http://localhost:5000/api/config"

# Get current configuration
response = requests.get(BASE_URL)
config = response.json()
print("Current config:", json.dumps(config, indent=2))

# Update delivery settings
delivery_config = {
    "email_enabled": True,
    "email_address": "digest@example.com",
    "telegram_enabled": False,
    "telegram_chat_id": None
}
response = requests.post(f"{BASE_URL}/delivery", json=delivery_config)
print("Updated delivery:", response.json())

# Configure scheduler
scheduler_config = {
    "enabled": True,
    "hour": 9,
    "minute": 0,
    "delivery_enabled": True
}
response = requests.post(f"{BASE_URL}/scheduler", json=scheduler_config)
print("Updated scheduler:", response.json())
```

## Runtime Configuration

Configuration changes via REST API take effect immediately without restart:

1. **Delivery Settings** - Apply immediately to next digest
2. **Adapter Settings** - Apply immediately to next pipeline run
3. **Scheduler Settings** - Applied immediately; requires scheduler restart to take effect
4. **Logging Settings** - File settings apply immediately; log level requires next message

### Applying Scheduler Changes

After updating scheduler configuration via API, restart the scheduler:

```bash
# Stop current scheduler
curl -X POST http://localhost:5000/api/scheduler/stop

# Start with new configuration
curl -X POST http://localhost:5000/api/scheduler/start \
  -H "Content-Type: application/json" \
  -d '{
    "deliver": true,
    "hour": 8,
    "minute": 30
  }'
```

## Best Practices

### 1. Validate Before Updating

Retrieve current configuration before making changes:

```bash
curl http://localhost:5000/api/config
```

### 2. Use Specific Endpoints

Update specific sections rather than full config:

```bash
# Good - Update only delivery
curl -X POST http://localhost:5000/api/config/delivery \
  -H "Content-Type: application/json" \
  -d '{"email_enabled": true, "email_address": "test@example.com", "telegram_enabled": false, "telegram_chat_id": null}'

# Less ideal - Update entire config
curl -X POST http://localhost:5000/api/config \
  -H "Content-Type: application/json" \
  -d '{...full config...}'
```

### 3. Monitor Logs After Changes

Check logs for successful application of configuration:

```bash
tail -f logs/ai_digest.log | grep "config"
```

### 4. Backup Configuration

Keep backups of working configurations:

```bash
cp config.json config.json.backup
```

### 5. Use Environment Variables for Sensitive Data

Store credentials in `.env`, not in `config.json`:

```bash
# .env
GMAIL_APP_PASSWORD=your_password
TELEGRAM_BOT_TOKEN=your_token
```

### 6. Test Changes with Manual Runs

Test configuration changes before scheduling:

```bash
# Trigger manual pipeline run with current config
curl -X POST http://localhost:5000/api/pipeline/run \
  -H "Content-Type: application/json" \
  -d '{"deliver": true}'
```

### 7. Document Custom Settings

Add comments to JSON file for custom adapter settings:

```json
{
  "adapters": {
    "reddit": {
      "name": "reddit",
      "enabled": true,
      "settings": {
        "_comment": "Monitoring Python and ML communities",
        "subreddits": ["python", "MachineLearning"],
        "limit": 30,
        "time_filter": "week"
      }
    }
  }
}
```

## Troubleshooting

### Configuration Not Updating

1. Check API response for error messages
2. Verify JSON syntax is valid
3. Ensure all required fields are present
4. Check `/health` endpoint to confirm server is running

### Changes Not Taking Effect

1. Verify configuration was saved: `GET /api/config`
2. For scheduler changes, restart scheduler
3. Check logs for configuration load errors: `tail logs/ai_digest.log`
4. Ensure no validation errors in API response

### Invalid Configuration Error

Configuration is validated via Pydantic models. Common issues:

- Missing required fields
- Invalid data types (string vs number)
- Out-of-range values (hour 0-23, minute 0-59)
- Invalid log level (use: DEBUG, INFO, WARNING, ERROR, CRITICAL)

Check the error message in API response for details.

## Advanced Configuration

### Custom Adapter Settings

Each adapter supports custom settings specific to its function:

```json
{
  "reddit": {
    "enabled": true,
    "settings": {
      "subreddits": ["python", "programming"],
      "limit": 20,
      "time_filter": "day"
    }
  },
  "producthunt": {
    "enabled": true,
    "settings": {
      "limit": 10,
      "days_lookback": 1
    }
  }
}
```

### Deployment-Specific Configuration

Different configurations for different environments:

```bash
# Development
curl -X POST http://localhost:5000/api/config/logging \
  -d '{"level": "DEBUG", ...}'

# Production
curl -X POST http://localhost:5000/api/config/logging \
  -d '{"level": "WARNING", ...}'
```

### Configuration Versioning

Track configuration changes in git:

```bash
git add config.json
git commit -m "Update: Enable Telegram delivery, set schedule to 8 AM"
```

---

**Version:** 0.1.0  
**Last Updated:** 2024  
**See Also:** [API.md](API.md), [SCHEDULING.md](SCHEDULING.md), [LOGGING.md](LOGGING.md)
