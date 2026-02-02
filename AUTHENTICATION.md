# API Authentication & Security

AI Digest provides production-ready security with JWT tokens and API keys. Secure all API endpoints with token-based authentication while maintaining easy access for authorized applications.

## Table of Contents

- [Quick Start](#quick-start)
- [Authentication Methods](#authentication-methods)
- [Login & Token Management](#login--token-management)
- [API Key Management](#api-key-management)
- [Using Authentication](#using-authentication)
- [Security Best Practices](#security-best-practices)

## Quick Start

### Default Credentials (Development)

```
Username: admin
Password: admin
```

**⚠️ IMPORTANT:** Change these credentials immediately in production!

### Login from Dashboard

1. Go to `http://localhost:5000`
2. Enter username and password
3. Click "Login"
4. Token stored in browser localStorage
5. Dashboard becomes accessible

### Login from Command Line

```bash
# Get JWT token
curl -X POST http://localhost:5000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username":"admin","password":"admin"}'

# Response:
{
  "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "user": "admin",
  "expires_in_hours": 24
}
```

## Authentication Methods

AI Digest supports two authentication methods:

### 1. JWT Tokens (Token-Based Auth)

**Best for:** Interactive applications, web dashboards, temporary access

**Format:** Bearer token in Authorization header

```
Authorization: Bearer <jwt_token>
```

**Expiration:** 24 hours (configurable via `JWT_EXPIRATION_HOURS`)

**Example:**
```bash
curl http://localhost:5000/api/config \
  -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
```

### 2. API Keys (Key-Based Auth)

**Best for:** Service-to-service communication, long-term access, multiple applications

**Format:** ApiKey header with key_id and key_secret

```
Authorization: ApiKey <key_id>:<key_secret>
```

**Expiration:** Never (manually revoked)

**Example:**
```bash
curl http://localhost:5000/api/config \
  -H "Authorization: ApiKey key_a1b2c3d4:your-secret-key-here"
```

## Login & Token Management

### Login to Get JWT Token

**Endpoint:** `POST /api/auth/login`

**Request:**
```bash
curl -X POST http://localhost:5000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username":"admin","password":"admin"}'
```

**Response (200):**
```json
{
  "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "user": "admin",
  "expires_in_hours": 24
}
```

**Response (401 Unauthorized):**
```json
{
  "error": "Invalid credentials"
}
```

### Refresh Token Before Expiration

**Endpoint:** `POST /api/auth/refresh`

**Request:**
```bash
curl -X POST http://localhost:5000/api/auth/refresh \
  -H "Authorization: Bearer <current_token>"
```

**Response (200):**
```json
{
  "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
}
```

Use new token in subsequent requests.

### Verify Token is Valid

**Endpoint:** `GET /api/auth/verify`

**Request:**
```bash
curl http://localhost:5000/api/auth/verify \
  -H "Authorization: Bearer <token>"
```

**Response (200):**
```json
{
  "valid": true,
  "user": "admin",
  "auth_type": "token"
}
```

**Response (401):**
```json
{
  "error": "Token has expired"
}
```

## API Key Management

API keys provide persistent authentication for applications and integrations.

### Create API Key

**Endpoint:** `POST /api/auth/keys`

**Request:**
```bash
curl -X POST http://localhost:5000/api/auth/keys \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{"name":"Integration with Slack"}'
```

**Response (201):**
```json
{
  "key_id": "key_a1b2c3d4",
  "key_secret": "your-secret-key-here",
  "message": "Save the key_secret - it will not be shown again!"
}
```

⚠️ **Important:** Save the `key_secret` immediately - it won't be shown again!

### List API Keys

**Endpoint:** `GET /api/auth/keys`

**Request:**
```bash
curl http://localhost:5000/api/auth/keys \
  -H "Authorization: Bearer <token>"
```

**Response (200):**
```json
{
  "keys": [
    {
      "key_id": "key_a1b2c3d4",
      "name": "Integration with Slack",
      "user_id": "admin",
      "created_at": "2024-01-29T10:30:00",
      "last_used": "2024-01-29T15:45:00",
      "active": true
    },
    {
      "key_id": "key_x9y8z7w6",
      "name": "Mobile App",
      "user_id": "admin",
      "created_at": "2024-01-28T09:00:00",
      "last_used": null,
      "active": false
    }
  ]
}
```

### Revoke (Deactivate) API Key

**Endpoint:** `DELETE /api/auth/keys/<key_id>`

**Request:**
```bash
curl -X DELETE http://localhost:5000/api/auth/keys/key_a1b2c3d4 \
  -H "Authorization: Bearer <token>"
```

**Response (200):**
```json
{
  "revoked": true,
  "key_id": "key_a1b2c3d4"
}
```

Revoked keys can no longer authenticate requests.

### Permanently Delete API Key

Use revoke for deactivation. Revoked keys remain in history for audit purposes.

## Using Authentication

### Protected Endpoints

All API endpoints except `/api/auth/login` require authentication:

- **GET /api/config** - Protected ✓
- **POST /api/pipeline/run** - Protected ✓
- **GET /api/scheduler/status** - Protected ✓
- **GET /api/digests** - Protected ✓
- **etc.**

### Request Without Auth → Error

```bash
curl http://localhost:5000/api/config
# Response: 401 Unauthorized
# Body: {"error": "Missing authorization header"}
```

### Request With Invalid Token → Error

```bash
curl http://localhost:5000/api/config \
  -H "Authorization: Bearer invalid_token"
# Response: 401 Unauthorized
# Body: {"error": "Invalid token"}
```

### Request With Valid Token → Success

```bash
curl http://localhost:5000/api/config \
  -H "Authorization: Bearer eyJhbGc..."
# Response: 200 OK
# Body: {...full configuration...}
```

## Authentication Examples

### Python Client with JWT

```python
import requests
import json

BASE_URL = "http://localhost:5000"

# Login
response = requests.post(f"{BASE_URL}/api/auth/login", json={
    "username": "admin",
    "password": "admin"
})
token = response.json()["token"]

# Use token in requests
headers = {"Authorization": f"Bearer {token}"}

# Get configuration
config = requests.get(f"{BASE_URL}/api/config", headers=headers).json()
print(json.dumps(config, indent=2))

# Run pipeline
result = requests.post(f"{BASE_URL}/api/pipeline/run", 
    json={"deliver": True}, 
    headers=headers).json()
print(f"Pipeline started: {result}")
```

### JavaScript Client with JWT

```javascript
// Login
const response = await fetch('http://localhost:5000/api/auth/login', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ username: 'admin', password: 'admin' })
});

const { token } = await response.json();

// Use token
const headers = { 'Authorization': `Bearer ${token}` };

// Get config
const config = await fetch('http://localhost:5000/api/config', 
    { headers }).then(r => r.json());

console.log(config);
```

### Using API Keys for Service-to-Service

```python
import requests

BASE_URL = "http://localhost:5000"
KEY_ID = "key_a1b2c3d4"
KEY_SECRET = "your-secret-key-here"

# Set up auth header
headers = {
    "Authorization": f"ApiKey {KEY_ID}:{KEY_SECRET}"
}

# Use normally
config = requests.get(f"{BASE_URL}/api/config", headers=headers).json()
print(config)
```

### cURL with API Key

```bash
curl http://localhost:5000/api/config \
  -H "Authorization: ApiKey key_a1b2c3d4:your-secret-key-here"
```

## Security Best Practices

### 1. Change Default Credentials

```bash
# DO NOT use default admin/admin in production
# Implement proper user management with hashed passwords
```

### 2. Use HTTPS in Production

```bash
# Development (HTTP)
http://localhost:5000

# Production (HTTPS)
https://your-domain.com
```

### 3. Store Secrets Securely

```bash
# Environment variables
export JWT_SECRET_KEY="your-very-long-random-secret-key"
export API_KEYS_FILE="/secure/path/api_keys.json"

# .env file (never commit to git)
JWT_SECRET_KEY=...
JWT_EXPIRATION_HOURS=24
```

### 4. Rotate Tokens Regularly

```javascript
// Refresh token before expiration
const newToken = await API.refreshToken(currentToken);
// Use new token for subsequent requests
```

### 5. Revoke Unused API Keys

```bash
# List all keys
curl http://localhost:5000/api/auth/keys \
  -H "Authorization: Bearer <token>"

# Revoke old/unused keys
curl -X DELETE http://localhost:5000/api/auth/keys/key_old \
  -H "Authorization: Bearer <token>"
```

### 6. Monitor Authentication Activity

Check logs for failed login attempts:

```bash
tail -f logs/ai_digest.log | grep "auth"
```

Look for:
- Failed authentication attempts
- Token validation errors
- API key revocations

### 7. Secure Token Storage

**Browser (Web Dashboard):**
```javascript
// Tokens stored in localStorage (same-origin only)
localStorage.setItem('auth_token', token);

// Cleared on logout
localStorage.removeItem('auth_token');
```

**Server/CLI Applications:**
```python
# Store tokens in environment or secure file
import os
token = os.getenv('AI_DIGEST_TOKEN')

# Never log tokens
logger.debug(f"Auth success")  # Good
logger.debug(f"Token: {token}")  # Never do this!
```

### 8. Audit API Key Creation

```bash
# Check api_keys.json for all created keys
cat api_keys.json | jq '.[] | {key_id, name, user_id, created_at, last_used}'
```

## Configuration

### Environment Variables

```bash
# JWT Configuration
JWT_SECRET_KEY=your-secret-key-change-in-production
JWT_EXPIRATION_HOURS=24

# API Keys File Location
API_KEYS_FILE=api_keys.json
```

### Default Settings

- **Token Expiration:** 24 hours
- **Token Algorithm:** HS256
- **API Key Format:** key_<random16>
- **Secret Key Format:** urlsafe base64 (32 bytes)

## Production Deployment Checklist

- [ ] Change default admin/admin credentials
- [ ] Set strong JWT_SECRET_KEY (32+ characters, random)
- [ ] Enable HTTPS/SSL certificates
- [ ] Use environment variables for secrets (.env in .gitignore)
- [ ] Set up regular token rotation
- [ ] Monitor authentication logs
- [ ] Implement rate limiting on /api/auth/login
- [ ] Set up audit logging for API key creation/revocation
- [ ] Use API keys instead of tokens for service-to-service
- [ ] Document your authentication policy
- [ ] Consider multi-factor authentication for future versions

## Troubleshooting

### "Missing authorization header"

**Cause:** Request made without Authorization header

**Solution:**
```bash
# Add header to request
curl http://localhost:5000/api/config \
  -H "Authorization: Bearer <token>"
```

### "Token has expired"

**Cause:** Token is older than 24 hours

**Solution:**
```python
# Refresh token
new_token = await API.refreshToken(old_token)

# Or login again
response = await API.login(username, password)
token = response['token']
```

### "Invalid token"

**Cause:** Token is malformed or tampered with

**Solution:**
```bash
# Generate new token via login
curl -X POST http://localhost:5000/api/auth/login \
  -d '{"username":"admin","password":"admin"}'
```

### "Invalid API key"

**Cause:** Key ID doesn't exist, secret is wrong, or key is revoked

**Solution:**
```bash
# List keys to find correct key_id
curl http://localhost:5000/api/auth/keys \
  -H "Authorization: Bearer <token>"

# Check API key hasn't been revoked
# Verify you have both key_id and key_secret correct
```

## Advanced Topics

### Custom User Authentication

Implement before deploying to production:

1. Create user database table
2. Hash passwords with bcrypt
3. Replace simple username/password check
4. Add password reset functionality
5. Implement rate limiting on login

### Multi-Tenant API Keys

Create separate API keys per tenant/organization:

```python
api_key = auth_mgr.create_key(
    name="Tenant A Integration", 
    user_id="tenant_a"
)
```

### Token Blacklisting

For enhanced security, implement token revocation:

```python
# Blacklist token on logout
# Check against blacklist on each request
# Clean up expired tokens periodically
```

---

**Version:** 0.1.0  
**Last Updated:** 2024  
**See Also:** [API.md](API.md), [DASHBOARD.md](DASHBOARD.md), [DEPLOYMENT.md](DEPLOYMENT.md)
