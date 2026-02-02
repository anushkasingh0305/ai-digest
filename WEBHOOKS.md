# Webhooks

Webhooks enable AI Digest to send real-time notifications to external services when new digests are generated. Support for Slack, Discord, and generic HTTP endpoints provides flexible integration with your existing workflows.

## Table of Contents

- [Quick Start](#quick-start)
- [Webhook Types](#webhook-types)
- [Configuration](#configuration)
- [API Reference](#api-reference)
- [Dashboard Management](#dashboard-management)
- [Payload Formats](#payload-formats)
- [Security Best Practices](#security-best-practices)
- [Examples](#examples)
- [Troubleshooting](#troubleshooting)

## Quick Start

### 1. Create a Webhook via Dashboard

1. Navigate to **🔔 Webhooks** tab
2. Fill in webhook details:
   - **ID**: Unique identifier (e.g., `slack-main`)
   - **Name**: Human-readable name (e.g., `Main Slack Channel`)
   - **Type**: Select `slack`, `discord`, or `generic`
   - **URL**: Your webhook endpoint URL
3. Click **Create Webhook**
4. Test with the **Test** button

### 2. Create a Webhook via API

```bash
curl -X POST http://localhost:5000/api/webhooks \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "id": "slack-main",
    "name": "Main Slack Channel",
    "type": "slack",
    "url": "https://hooks.slack.com/services/YOUR/WEBHOOK/URL"
  }'
```

### 3. Enable Automatic Delivery

Webhooks automatically send notifications when:
- Pipeline runs with `deliver=true`
- Scheduled digest completes with delivery enabled

No additional configuration needed once webhooks are created and enabled.

## Webhook Types

### Slack

**Purpose:** Send formatted digest notifications to Slack channels

**Features:**
- Rich formatting with message blocks
- Interactive "View Digest" button
- Header with emoji icon
- Content preview (first 500 chars)

**Setup:**
1. Create Slack incoming webhook: https://api.slack.com/messaging/webhooks
2. Copy webhook URL
3. Create webhook with type `slack`

**Example:**
```json
{
  "id": "slack-team",
  "name": "Team Slack Channel",
  "type": "slack",
  "url": "https://hooks.slack.com/services/T00000000/B00000000/XXXXXXXXXXXXXXXXXXXX"
}
```

### Discord

**Purpose:** Send embedded digest notifications to Discord channels

**Features:**
- Rich embed with colored border
- Title and description formatting
- Footer with timestamp
- Clickable digest link

**Setup:**
1. Discord → Server Settings → Integrations → Webhooks
2. Create webhook, copy URL
3. Create webhook with type `discord`

**Example:**
```json
{
  "id": "discord-general",
  "name": "Discord General Channel",
  "type": "discord",
  "url": "https://discord.com/api/webhooks/123456789/XXXXXXXXXXXXXXXXXXXX"
}
```

### Generic

**Purpose:** Send JSON payloads to any HTTP endpoint

**Features:**
- Standard JSON structure
- Customizable with headers
- Payload template support
- Compatible with Zapier, IFTTT, n8n, Make.com

**Setup:**
1. Set up receiving endpoint
2. Create webhook with type `generic`
3. Add custom headers if needed
4. Test with sample payload

**Example:**
```json
{
  "id": "zapier-workflow",
  "name": "Zapier Integration",
  "type": "generic",
  "url": "https://hooks.zapier.com/hooks/catch/123456/XXXXXX/",
  "headers": {
    "X-Custom-Header": "value"
  }
}
```

## Configuration

### Required Fields

| Field | Type | Description | Example |
|-------|------|-------------|---------|
| `id` | string | Unique webhook identifier | `"slack-main"` |
| `name` | string | Human-readable name | `"Main Slack Channel"` |
| `type` | string | Webhook type: `slack`, `discord`, `generic` | `"slack"` |
| `url` | string | HTTPS endpoint URL | `"https://hooks.slack.com/..."` |

### Optional Fields

| Field | Type | Description | Example |
|-------|------|-------------|---------|
| `enabled` | boolean | Enable/disable webhook (default: `true`) | `true` |
| `headers` | object | Custom HTTP headers | `{"Authorization": "Bearer token"}` |
| `payload_template` | string | Custom JSON payload overlay | `{"channel": "#alerts"}` |

### Webhook Object Structure

```json
{
  "id": "webhook-id",
  "name": "Webhook Name",
  "type": "slack",
  "url": "https://...",
  "enabled": true,
  "headers": {},
  "payload_template": null,
  "created_at": "2026-01-29T10:00:00.000000",
  "updated_at": "2026-01-29T10:00:00.000000",
  "last_triggered_at": "2026-01-29T10:30:00.000000",
  "trigger_count": 5
}
```

## API Reference

### List Webhooks

```http
GET /api/webhooks
Authorization: Bearer YOUR_TOKEN
```

**Response:**
```json
[
  {
    "id": "slack-main",
    "name": "Main Slack Channel",
    "type": "slack",
    "url": "https://...",
    "enabled": true,
    "trigger_count": 12
  }
]
```

### Get Webhook

```http
GET /api/webhooks/{webhook_id}
Authorization: Bearer YOUR_TOKEN
```

**Response:**
```json
{
  "id": "slack-main",
  "name": "Main Slack Channel",
  "type": "slack",
  "url": "https://...",
  "enabled": true,
  "created_at": "2026-01-29T10:00:00.000000"
}
```

### Create Webhook

```http
POST /api/webhooks
Authorization: Bearer YOUR_TOKEN
Content-Type: application/json

{
  "id": "discord-alerts",
  "name": "Discord Alerts",
  "type": "discord",
  "url": "https://discord.com/api/webhooks/...",
  "headers": {},
  "payload_template": null
}
```

**Response:** `201 Created` with webhook object

### Update Webhook

```http
PUT /api/webhooks/{webhook_id}
Authorization: Bearer YOUR_TOKEN
Content-Type: application/json

{
  "name": "Updated Name",
  "url": "https://new-url.com",
  "enabled": true
}
```

**Response:** `200 OK` with updated webhook object

### Delete Webhook

```http
DELETE /api/webhooks/{webhook_id}
Authorization: Bearer YOUR_TOKEN
```

**Response:** `200 OK` with `{"message": "Webhook deleted"}`

### Toggle Webhook

```http
POST /api/webhooks/{webhook_id}/toggle
Authorization: Bearer YOUR_TOKEN
```

**Response:** `200 OK` with updated webhook object (enabled state flipped)

### Test Webhook

```http
POST /api/webhooks/{webhook_id}/test
Authorization: Bearer YOUR_TOKEN
```

**Response:** `200 OK` if test succeeds, `500 Internal Server Error` if fails

**Test Payload:**
- Title: "Test Digest"
- Content: "This is a test notification from AI Digest"
- Digest ID: "test-digest"

## Dashboard Management

### Creating Webhooks

1. Navigate to **🔔 Webhooks** tab
2. Right panel: **Create Webhook** form
3. Fill in required fields (ID, Name, Type, URL)
4. Optional: Add custom headers (JSON format)
5. Optional: Add payload template (JSON string)
6. Click **Create Webhook**
7. Success message appears
8. Webhook appears in left panel list

### Editing Webhooks

1. Find webhook in list
2. Click **Edit** button
3. Form populates with current values
4. Modify fields (ID cannot be changed)
5. Click **Save Changes**
6. Click **Cancel** to discard changes

### Testing Webhooks

1. Find webhook in list
2. Click **Test** button
3. Test notification sent immediately
4. Check external service for test message
5. Success/failure message appears in dashboard

### Toggling Webhooks

1. Find webhook in list
2. Click **Enable**/**Disable** button
3. Webhook state toggles
4. Disabled webhooks skip notifications
5. Re-enable anytime without reconfiguration

### Deleting Webhooks

1. Find webhook in list
2. Click **Delete** button
3. Confirm deletion in dialog
4. Webhook removed permanently
5. Cannot be recovered (create new if needed)

## Payload Formats

### Slack Payload

```json
{
  "blocks": [
    {
      "type": "header",
      "text": {
        "type": "plain_text",
        "text": "📰 New Digest"
      }
    },
    {
      "type": "section",
      "text": {
        "type": "mrkdwn",
        "text": "*Daily Digest*\nDigest content preview (first 500 chars)..."
      }
    },
    {
      "type": "actions",
      "elements": [
        {
          "type": "button",
          "text": {
            "type": "plain_text",
            "text": "View Digest"
          },
          "url": "/digests/{digest_id}"
        }
      ]
    }
  ]
}
```

### Discord Payload

```json
{
  "embeds": [
    {
      "title": "📰 Daily Digest",
      "description": "Digest content preview (first 500 chars)...",
      "color": 3447003,
      "url": "/digests/{digest_id}",
      "footer": {
        "text": "AI Digest"
      },
      "timestamp": "2026-01-29T10:30:00.000000Z"
    }
  ]
}
```

### Generic Payload

```json
{
  "type": "digest_notification",
  "digest_id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
  "title": "Daily Digest",
  "content": "Full digest content...",
  "timestamp": "2026-01-29T10:30:00.000000"
}
```

### Custom Payload Templates

Override default payloads by providing `payload_template` (merged with base payload):

**Example - Slack with custom channel:**
```json
{
  "payload_template": "{\"channel\": \"#ai-digests\"}"
}
```

**Example - Generic with metadata:**
```json
{
  "payload_template": "{\"priority\": \"high\", \"tags\": [\"ai\", \"digest\"]}"
}
```

**Note:** Invalid JSON in `payload_template` is logged but doesn't prevent delivery (template ignored).

## Security Best Practices

### 1. Use HTTPS URLs Only

**Why:** Prevent eavesdropping on digest content
**How:** Ensure webhook URLs start with `https://`
**Example:** ❌ `http://example.com` → ✅ `https://example.com/webhooks`

### 2. Rotate Webhook URLs

**Why:** Limit exposure if URLs leak
**How:** Regenerate webhook URLs quarterly
**Steps:**
1. Generate new webhook in external service
2. Update webhook URL in AI Digest
3. Test with **Test** button
4. Delete old webhook in external service

### 3. Use Secret Tokens

**Why:** Verify requests come from AI Digest
**How:** Add authentication headers
**Example:**
```json
{
  "headers": {
    "X-Webhook-Secret": "your-secret-token-here"
  }
}
```

### 4. Monitor Trigger Counts

**Why:** Detect anomalies or abuse
**How:** Check `trigger_count` in webhook list
**Action:** Investigate if count spikes unexpectedly

### 5. Disable Unused Webhooks

**Why:** Reduce attack surface
**How:** Click **Disable** instead of deleting
**Benefit:** Easy re-enable if needed later

### 6. Review Logs

**Why:** Audit webhook delivery
**How:** Check `logs/ai_digest.log` for webhook events
**Filter:** Search for `component: "webhooks.sender"`

### 7. Validate Endpoints

**Why:** Prevent sending data to wrong services
**How:** Always test with **Test** button after creation
**Check:** Verify correct channel/endpoint receives test message

## Examples

### Example 1: Slack Notification

**Goal:** Notify team Slack channel when digest completes

**Setup:**
1. Slack → Settings → Custom Integrations → Incoming Webhooks
2. Create webhook for `#team-updates` channel
3. Copy URL: `https://hooks.slack.com/services/T123/B456/abc123`

**Create Webhook:**
```bash
curl -X POST http://localhost:5000/api/webhooks \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "id": "slack-team-updates",
    "name": "Team Updates Channel",
    "type": "slack",
    "url": "https://hooks.slack.com/services/T123/B456/abc123"
  }'
```

**Test:**
```bash
curl -X POST http://localhost:5000/api/webhooks/slack-team-updates/test \
  -H "Authorization: Bearer YOUR_TOKEN"
```

**Result:** Slack channel receives formatted message with digest preview

---

### Example 2: Discord with Custom Headers

**Goal:** Send digest to Discord with authentication header

**Setup:**
1. Discord → Server → Integrations → Create Webhook
2. Copy webhook URL
3. Add custom auth header for additional verification

**Create Webhook:**
```bash
curl -X POST http://localhost:5000/api/webhooks \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "id": "discord-secure",
    "name": "Secure Discord Channel",
    "type": "discord",
    "url": "https://discord.com/api/webhooks/987654321/xyz789",
    "headers": {
      "X-Custom-Auth": "secret-token-here"
    }
  }'
```

---

### Example 3: Zapier Integration

**Goal:** Trigger Zapier workflow when digest is generated

**Setup:**
1. Zapier → Create Zap → Webhooks by Zapier → Catch Hook
2. Copy webhook URL: `https://hooks.zapier.com/hooks/catch/123456/abcdef/`
3. Use generic webhook type

**Create Webhook:**
```bash
curl -X POST http://localhost:5000/api/webhooks \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "id": "zapier-workflow",
    "name": "Zapier Integration",
    "type": "generic",
    "url": "https://hooks.zapier.com/hooks/catch/123456/abcdef/"
  }'
```

**Zapier Workflow:**
1. Receive webhook → Extract `digest_id`, `title`, `content`
2. Send to Google Sheets
3. Post to Twitter
4. Email summary to subscribers

---

### Example 4: Multiple Webhooks

**Goal:** Send to both Slack and Discord simultaneously

**Setup:**
```bash
# Create Slack webhook
curl -X POST http://localhost:5000/api/webhooks \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "id": "slack-main",
    "name": "Slack Main",
    "type": "slack",
    "url": "https://hooks.slack.com/services/..."
  }'

# Create Discord webhook
curl -X POST http://localhost:5000/api/webhooks \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "id": "discord-main",
    "name": "Discord Main",
    "type": "discord",
    "url": "https://discord.com/api/webhooks/..."
  }'
```

**Result:** Each pipeline delivery sends to ALL enabled webhooks in parallel

---

### Example 5: Conditional Webhooks (Disable/Enable)

**Goal:** Only notify Discord on weekdays, Slack on weekends

**Manual Approach:**
```bash
# Monday - Disable Discord, Enable Slack
curl -X POST http://localhost:5000/api/webhooks/discord-main/toggle \
  -H "Authorization: Bearer YOUR_TOKEN"

# Friday - Enable Discord, Disable Slack
curl -X POST http://localhost:5000/api/webhooks/slack-main/toggle \
  -H "Authorization: Bearer YOUR_TOKEN"
```

**Automated Approach:** Create cron job or external scheduler to toggle webhooks via API

## Troubleshooting

### Issue: Webhook Not Receiving Notifications

**Symptoms:**
- Dashboard shows webhook enabled
- Pipeline completes successfully
- No message in external service

**Diagnosis:**
1. Check webhook enabled status: `GET /api/webhooks/{id}`
2. Review logs: `logs/ai_digest.log` → search `webhook_id`
3. Test webhook: `POST /api/webhooks/{id}/test`

**Solutions:**
- ✅ Ensure webhook `enabled: true`
- ✅ Verify URL is correct and HTTPS
- ✅ Check external service is online
- ✅ Review firewall/network blocking outbound requests
- ✅ Confirm pipeline runs with `deliver=true`

---

### Issue: Test Succeeds, Real Delivery Fails

**Symptoms:**
- Test button works
- Scheduled/manual delivery doesn't trigger webhook

**Diagnosis:**
```bash
# Check recent digests
curl http://localhost:5000/api/digests?limit=5 \
  -H "Authorization: Bearer YOUR_TOKEN"

# Review pipeline logs
grep "webhook" logs/ai_digest.log | tail -20
```

**Solutions:**
- ✅ Verify pipeline runs with delivery enabled
- ✅ Check `trigger_count` increments (indicates successful sends)
- ✅ Review `last_triggered_at` timestamp
- ✅ Ensure digest generation doesn't fail before delivery

---

### Issue: Invalid JSON in Headers/Payload Template

**Symptoms:**
- Webhook creation fails
- Error message: "Invalid headers JSON" or "Invalid payload template"

**Solutions:**
- ✅ Validate JSON with online tool (jsonlint.com)
- ✅ Use double quotes for keys and string values
- ✅ Escape special characters: `\"` for quotes
- ✅ Example valid header: `{"Authorization": "Bearer token"}`
- ✅ Example invalid header: `{Authorization: 'Bearer token'}` (single quotes)

---

### Issue: Webhook Times Out

**Symptoms:**
- Logs show "Webhook request timed out"
- External service slow to respond

**Diagnosis:**
```bash
# Check webhook timeout setting (default: 10 seconds)
grep "timeout" src/services/webhooks.py
```

**Solutions:**
- ✅ Verify external service responds quickly (< 5s)
- ✅ Check network latency to webhook URL
- ✅ Use faster endpoint if available
- ✅ Disable webhook temporarily if service down

---

### Issue: Slack/Discord Messages Don't Format

**Symptoms:**
- Webhook delivers but plain text instead of rich format
- No buttons, embeds, or formatting

**Diagnosis:**
- Check webhook type matches service (Slack→slack, Discord→discord)
- Review payload in logs

**Solutions:**
- ✅ Ensure `type: "slack"` for Slack webhooks
- ✅ Ensure `type: "discord"` for Discord webhooks
- ✅ Don't use `generic` type for Slack/Discord
- ✅ Recreate webhook with correct type if needed

---

### Issue: Too Many Webhooks Slow Delivery

**Symptoms:**
- Pipeline takes longer to complete
- Many webhooks configured (10+)

**Solutions:**
- ✅ Disable unused webhooks instead of deleting
- ✅ Combine multiple channels into single webhook with routing
- ✅ Use webhook aggregator services (Zapier multi-path)
- ✅ Review `trigger_count` to find unused webhooks

---

### Common Error Messages

| Error | Meaning | Solution |
|-------|---------|----------|
| `Webhook {id} already exists` | ID not unique | Use different ID |
| `Webhook {id} not found` | Invalid webhook ID | Check ID spelling |
| `Invalid webhook type` | Type not slack/discord/generic | Use valid type |
| `Missing required fields` | Required field empty | Provide id, name, type, url |
| `aiohttp is required` | Missing dependency | `pip install aiohttp>=3.9` |

---

## Advanced Usage

### Webhook Monitoring Script

**Monitor webhook health:**
```python
import requests

AUTH_TOKEN = "your-token"
API_URL = "http://localhost:5000"

headers = {"Authorization": f"Bearer {AUTH_TOKEN}"}
response = requests.get(f"{API_URL}/api/webhooks", headers=headers)
webhooks = response.json()

for webhook in webhooks:
    print(f"{webhook['id']}: enabled={webhook['enabled']}, triggers={webhook['trigger_count']}")
```

### Bulk Webhook Creation

**Create multiple webhooks from config:**
```python
import requests

webhooks_config = [
    {"id": "slack-1", "name": "Slack Team", "type": "slack", "url": "https://..."},
    {"id": "discord-1", "name": "Discord Server", "type": "discord", "url": "https://..."},
]

for config in webhooks_config:
    response = requests.post(
        "http://localhost:5000/api/webhooks",
        headers={"Authorization": "Bearer YOUR_TOKEN", "Content-Type": "application/json"},
        json=config
    )
    print(f"Created {config['id']}: {response.status_code}")
```

### Webhook Event Logger

**Log all webhook events to file:**
```bash
# Filter webhook logs
grep "webhooks.sender" logs/ai_digest.log > webhook_events.log

# Count successful deliveries
grep "sent successfully" webhook_events.log | wc -l

# Find failed deliveries
grep "send failed" webhook_events.log
```

---

## Dependencies

Webhooks require the `aiohttp` library for HTTP requests:

**Install:**
```bash
pip install aiohttp>=3.9
```

**Verify:**
```bash
python -c "import aiohttp; print(aiohttp.__version__)"
```

**Included in:**
- `requirements.txt`
- `pyproject.toml`

If missing, webhook delivery gracefully fails with error logged (doesn't crash pipeline).

---

## Architecture

### Webhook Flow

1. **Pipeline Execution** → Digest generated with `digest_id`
2. **Delivery Phase** → Check for enabled webhooks
3. **Parallel Dispatch** → Send to all enabled webhooks simultaneously
4. **Format Payload** → Build Slack/Discord/Generic payload
5. **HTTP POST** → Send to webhook URL with timeout (10s)
6. **Handle Response** → Log success/failure, update `trigger_count`
7. **Update Metadata** → Save `last_triggered_at` timestamp

### Components

- **`src/services/webhooks.py`** - WebhookManager, WebhookSender classes
- **`webhooks.json`** - Persistent webhook storage
- **`src/server.py`** - REST API endpoints (/api/webhooks/*)
- **`src/workflows/pipeline.py`** - Integration point for delivery

---

## Related Documentation

- [Authentication Guide](AUTHENTICATION.md) - API token setup
- [Dashboard Guide](DASHBOARD.md) - Web UI management
- [Delivery Configuration](CONFIGURATION.md#delivery) - Email/Telegram setup
- [API Reference](API.md) - Complete REST API documentation
- [Deployment Guide](DEPLOYMENT.md) - Production setup

---

## Support

**Questions or Issues:**
- Check [Troubleshooting](#troubleshooting) section
- Review `logs/ai_digest.log` for webhook errors
- Test webhooks individually with **Test** button
- Verify external service webhook endpoints are active

**Need Help:**
- GitHub Issues: https://github.com/example/ai_digest/issues
- Documentation: https://github.com/example/ai_digest/blob/main/README.md
