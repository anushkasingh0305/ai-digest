# REST API Documentation

## Overview

The AI Digest system provides a complete REST API for managing digests, running the pipeline, and controlling the scheduler.

**Base URL**: `http://localhost:5000`

## Endpoints

### Health & Monitoring

#### Health Check
```
GET /health
```

Check if the server is running.

**Response** (200):
```json
{
  "status": "ok",
  "timestamp": 1706535000.123
}
```

#### Metrics
```
GET /metrics
```

Get Prometheus metrics in text format.

**Response** (200):
```
# HELP ai_digest_runs_total Total number of digest runs
# TYPE ai_digest_runs_total counter
ai_digest_runs_total 42.0
...
```

#### System Info
```
GET /info
```

Get system information and version.

**Response** (200):
```json
{
  "name": "AI Digest",
  "version": "0.1.0",
  "status": "running",
  "timestamp": 1706535000.123
}
```

---

### Digest Management

#### List Digests
```
GET /api/digests
```

List recent digests with pagination.

**Query Parameters**:
- `limit` (int, default: 10): Maximum number of digests to return
- `offset` (int, default: 0): Pagination offset
- `days` (int, optional): Filter to last N days

**Example**:
```
GET /api/digests?limit=20&offset=0&days=7
```

**Response** (200):
```json
{
  "digests": [
    {
      "timestamp": "2026-01-29T12:00:00.000000",
      "item_count": 15,
      "path": "out/20260129_120000.json",
      "digest_id": "20260129_120000",
      "duration_seconds": 2.34
    }
  ],
  "count": 1,
  "limit": 20,
  "offset": 0
}
```

#### Get Digest
```
GET /api/digests/{digest_id}
```

Retrieve a specific digest by ID.

**Parameters**:
- `digest_id` (string): The digest ID (e.g., `20260129_120000`)

**Example**:
```
GET /api/digests/20260129_120000
```

**Response** (200):
```json
{
  "metadata": {
    "timestamp": "2026-01-29T12:00:00.000000",
    "item_count": 15,
    "path": "out/20260129_120000.json",
    "digest_id": "20260129_120000",
    "duration_seconds": 2.34
  },
  "items": [
    {
      "title": "Example Story",
      "url": "https://example.com",
      "source": "hacker_news",
      "score": 0.85
    }
  ],
  "summary": null
}
```

**Response** (404):
```json
{
  "error": "Digest not found"
}
```

#### Delete Digest
```
DELETE /api/digests/{digest_id}
```

Delete a digest.

**Parameters**:
- `digest_id` (string): The digest ID

**Example**:
```
DELETE /api/digests/20260129_120000
```

**Response** (200):
```json
{
  "deleted": true,
  "digest_id": "20260129_120000"
}
```

**Response** (404):
```json
{
  "error": "Digest not found"
}
```

---

### Pipeline Execution

#### Trigger Pipeline
```
POST /api/pipeline/run
```

Run the pipeline immediately in the background.

**Request Body**:
```json
{
  "deliver": false
}
```

**Parameters**:
- `deliver` (boolean, default: false): Whether to send digest via email and Telegram

**Example**:
```bash
curl -X POST http://localhost:5000/api/pipeline/run \
  -H "Content-Type: application/json" \
  -d '{"deliver": false}'
```

**Response** (202):
```json
{
  "started": true,
  "deliver": false
}
```

---

### Scheduler Management

#### Scheduler Status
```
GET /api/scheduler/status
```

Get current scheduler status and list scheduled jobs.

**Response** (200):
```json
{
  "running": true,
  "job_count": 1,
  "jobs": [
    {
      "id": "daily_digest_6am",
      "name": "daily at 06:00 UTC",
      "next_run_time": "2026-01-30T06:00:00",
      "trigger": "cron[hour='6', minute='0']"
    }
  ]
}
```

#### Start Scheduler
```
POST /api/scheduler/start
```

Start the background scheduler.

**Request Body**:
```json
{
  "deliver": true,
  "hour": 6,
  "minute": 0
}
```

**Parameters**:
- `deliver` (boolean, default: true): Whether to send digests
- `hour` (int, default: 6): Hour for daily digest (0-23, UTC)
- `minute` (int, default: 0): Minute for daily digest (0-59)

**Example**:
```bash
curl -X POST http://localhost:5000/api/scheduler/start \
  -H "Content-Type: application/json" \
  -d '{"deliver": true, "hour": 14, "minute": 30}'
```

**Response** (200):
```json
{
  "started": true,
  "deliver": true,
  "jobs": [
    {
      "id": "digest_daily_1430",
      "name": "daily at 14:30 UTC",
      "next_run_time": "2026-01-30T14:30:00",
      "trigger": "cron[hour='14', minute='30']"
    }
  ]
}
```

#### Stop Scheduler
```
POST /api/scheduler/stop
```

Stop the background scheduler.

**Example**:
```bash
curl -X POST http://localhost:5000/api/scheduler/stop
```

**Response** (200):
```json
{
  "stopped": true
}
```

---

## Usage Examples

### Python Requests

```python
import requests

BASE_URL = "http://localhost:5000"

# List digests
response = requests.get(f"{BASE_URL}/api/digests?limit=10")
digests = response.json()
print(f"Found {digests['count']} digests")

# Get specific digest
digest = requests.get(f"{BASE_URL}/api/digests/20260129_120000").json()
print(f"Items: {digest['metadata']['item_count']}")

# Trigger pipeline
response = requests.post(
    f"{BASE_URL}/api/pipeline/run",
    json={"deliver": False}
)
print(f"Pipeline started: {response.json()['started']}")

# Start scheduler
response = requests.post(
    f"{BASE_URL}/api/scheduler/start",
    json={"deliver": True, "hour": 14, "minute": 0}
)
jobs = response.json()['jobs']
print(f"Scheduler running with {len(jobs)} job(s)")

# Check scheduler status
response = requests.get(f"{BASE_URL}/api/scheduler/status")
status = response.json()
print(f"Scheduler running: {status['running']}")
```

### cURL

```bash
# List recent digests
curl http://localhost:5000/api/digests?limit=5

# Get specific digest
curl http://localhost:5000/api/digests/20260129_120000

# Trigger pipeline with delivery
curl -X POST http://localhost:5000/api/pipeline/run \
  -H "Content-Type: application/json" \
  -d '{"deliver": true}'

# Start scheduler at 2 PM UTC
curl -X POST http://localhost:5000/api/scheduler/start \
  -H "Content-Type: application/json" \
  -d '{"deliver": true, "hour": 14, "minute": 0}'

# Check scheduler status
curl http://localhost:5000/api/scheduler/status

# Stop scheduler
curl -X POST http://localhost:5000/api/scheduler/stop
```

### JavaScript/Fetch

```javascript
const BASE_URL = "http://localhost:5000";

// List digests
async function listDigests(limit = 10) {
  const response = await fetch(`${BASE_URL}/api/digests?limit=${limit}`);
  return await response.json();
}

// Get digest
async function getDigest(digestId) {
  const response = await fetch(`${BASE_URL}/api/digests/${digestId}`);
  return await response.json();
}

// Trigger pipeline
async function triggerPipeline(deliver = false) {
  const response = await fetch(`${BASE_URL}/api/pipeline/run`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ deliver }),
  });
  return await response.json();
}

// Start scheduler
async function startScheduler(hour = 6, minute = 0, deliver = true) {
  const response = await fetch(`${BASE_URL}/api/scheduler/start`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ hour, minute, deliver }),
  });
  return await response.json();
}

// Check status
async function getSchedulerStatus() {
  const response = await fetch(`${BASE_URL}/api/scheduler/status`);
  return await response.json();
}

// Usage
(async () => {
  const digests = await listDigests();
  console.log("Digests:", digests);
  
  const status = await getSchedulerStatus();
  console.log("Scheduler running:", status.running);
})();
```

---

## Error Handling

All endpoints return appropriate HTTP status codes and JSON error responses.

### Common Status Codes

| Code | Meaning |
|------|---------|
| 200 | Success |
| 202 | Accepted (async operation) |
| 400 | Bad request (invalid parameters) |
| 404 | Not found |
| 500 | Internal server error |

### Error Response Format

```json
{
  "error": "Description of the error"
}
```

---

## Authentication

Currently, the API has no authentication. For production use, consider adding:

- API key authentication
- JWT tokens
- OAuth 2.0
- Rate limiting

See [DEPLOYMENT.md](DEPLOYMENT.md) for security recommendations.

---

## Pagination

List endpoints support pagination:

- `limit`: Maximum results (default: 10, max: 100)
- `offset`: Pagination offset (default: 0)

Example:
```
GET /api/digests?limit=20&offset=40  # Items 40-59
```

---

## Response Formats

All responses use JSON format with appropriate HTTP status codes.

### Success Response
```json
{
  "status": "ok",
  "data": { ... }
}
```

### Error Response
```json
{
  "error": "Error message"
}
```

---

## Rate Limiting

Currently not implemented. Add to production deployment:

```
X-RateLimit-Limit: 100
X-RateLimit-Remaining: 99
X-RateLimit-Reset: 1706535000
```

---

## Webhooks (Future)

Planned webhooks for digest completion:

```bash
POST /webhooks/digest-completed
{
  "digest_id": "20260129_120000",
  "item_count": 15,
  "timestamp": "2026-01-29T12:00:00Z"
}
```

---

## Versioning

Current API version: `1.0.0`

Future versions will use URL prefix:
```
/api/v1/digests
/api/v2/digests  # Future
```
