# Deployment Guide — AI Digest

## Prerequisites

### Windows (PowerShell)
- Python 3.11+ installed
- Docker Desktop (for Docker Compose deployment) or WSL2
- Administrator access (for scheduling)

### Linux / WSL
- Python 3.11+
- Docker + Docker Compose
- curl, git

## Local Setup (No Docker)

### 1. Clone / Extract Repository
```powershell
cd C:\Users\<you>
git clone <repo-url> ai_digest
cd ai_digest
```

### 2. Create Virtual Environment
```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

### 3. Configure Environment
```powershell
# Copy template and edit
Copy-Item .env.example .env
# Edit .env with your credentials (SMTP, Telegram, Reddit, etc.)
notepad .env
```

### 4. Run Pipeline Manually
```powershell
# One-off digest (no delivery)
python -m src.cli.main

# One-off with email/telegram delivery
python -m src.cli.main --deliver

# With scheduling (runs daily at 9 AM)
python -m src.cli.main --schedule --hour 9 --minute 0
```

### 5. Run Tests
```powershell
python -m pytest -q
# Expected: 8 passed
```

### 6. View Output
```powershell
# Check digest JSON
Get-Content out/digest.json -Raw | ConvertFrom-Json | Format-List
```

---

## Docker Compose Deployment (Recommended)

### Prerequisites
- Docker Desktop (Windows/Mac) with WSL2, or Docker Engine (Linux)
- Ports 5000, 9090, 3000, 11434 available

### 1. Setup
```powershell
cd C:\Users\<you>\ai_digest
Copy-Item .env.example .env
# Edit .env
notepad .env
```

### 2. Build & Start Stack
```powershell
# Build images and start services in background
docker-compose up --build -d

# Wait 10s for services to start
Start-Sleep -Seconds 10

# Check status
docker ps
```

### 3. Verify Endpoints
```powershell
# Health check
curl http://localhost:5000/health

# Metrics endpoint
curl http://localhost:5000/metrics

# Prometheus UI
start http://localhost:9090

# Grafana UI (admin/admin)
start http://localhost:3000
```

### 4. Run the Smoke Test Script
```powershell
.\run_docker_smoke.ps1
# Expected: "Smoke test passed — all endpoints responded."
```

### 5. View Logs
```powershell
# All services
docker-compose logs --tail 100

# Single service
docker-compose logs --tail 100 app
docker-compose logs --tail 100 prometheus
docker-compose logs --tail 100 grafana
```

### 6. Trigger a Pipeline Run
```powershell
# Send HTTP POST to /run endpoint
curl -X POST http://localhost:5000/run

# Check logs
docker-compose logs app
```

### 7. Teardown
```powershell
# Stop and remove containers, networks, and volumes
docker-compose down -v
```

---

## Production Deployment (Linux/Kubernetes)

### Option A: systemd Service (Linux)

1. **Install app to system Python or virtualenv**
```bash
sudo mkdir -p /opt/ai_digest
cd /opt/ai_digest
git clone <repo-url> .
python3 -m venv venv
. venv/bin/activate
pip install -r requirements.txt
```

2. **Create systemd service** (`/etc/systemd/system/ai-digest.service`):
```ini
[Unit]
Description=AI Digest Pipeline
After=network.target

[Service]
Type=simple
User=appuser
WorkingDirectory=/opt/ai_digest
Environment="DATABASE_URL=sqlite:////var/lib/ai_digest/digest.db"
Environment="OLLAMA_URL=http://localhost:11434"
EnvironmentFile=/etc/ai_digest/.env
ExecStart=/opt/ai_digest/venv/bin/python -m src.cli.main --schedule --hour 9
Restart=on-failure
RestartSec=60

[Install]
WantedBy=multi-user.target
```

3. **Start service**
```bash
sudo systemctl daemon-reload
sudo systemctl enable ai-digest
sudo systemctl start ai-digest
sudo systemctl status ai-digest
```

### Option B: Docker Compose on VPS

1. **SSH into VPS**
```bash
ssh user@example.com
cd /opt/ai_digest
git clone <repo-url> .
```

2. **Configure .env and firewall**
```bash
cp .env.example .env
# Edit .env with production values
nano .env

# Open ports (if behind firewall)
sudo ufw allow 5000/tcp  # App
sudo ufw allow 9090/tcp  # Prometheus
sudo ufw allow 3000/tcp  # Grafana
```

3. **Start stack**
```bash
docker-compose up --build -d
```

4. **Setup SSL/TLS** (optional, using reverse proxy like nginx):
```bash
# Example nginx config
# Listen 443, forward to localhost:5000
# Let's Encrypt certificates
```

### Option C: Kubernetes (Helm, future)

```bash
# Helm chart coming soon
helm install ai-digest ./helm/ai-digest \
  --set image.repository=<your-registry>/ai-digest:latest \
  --set config.OLLAMA_URL=http://ollama:11434 \
  --values production-values.yaml
```

---

## Database Backup & Migration

### SQLite (Local)
```powershell
# Backup
Copy-Item ai_digest.db ai_digest.db.backup

# Alembic migrations (future)
alembic upgrade head
```

### PostgreSQL (Production)
```bash
# Set DATABASE_URL
export DATABASE_URL=postgresql://user:pass@postgres:5432/ai_digest

# Run migrations
alembic upgrade head

# Backup
pg_dump $DATABASE_URL > backup.sql
```

---

## Monitoring & Alerting

### Prometheus
- **UI**: http://localhost:9090
- **Health**: http://localhost:9090/-/healthy
- **Rules**: http://localhost:9090/api/v1/rules
- **Alerts**: http://localhost:9090/api/v1/alerts

### Grafana
- **UI**: http://localhost:3000
- **Default creds**: admin / admin
- **Dashboards**: `Configuration → Dashboards`
- **Data Sources**: `Configuration → Data Sources`

### Alert Rules (defined in `prometheus/alert_rules.yml`)
- `HighDeliveryFailureRate`: > 10% failures over 5m
- `EmbeddingLatencyHigh`: p95 > 2s over 5m

---

## Troubleshooting

### Docker Compose Won't Start
```powershell
# Check logs
docker-compose logs --tail 200

# Check port conflicts
netstat -ano | findstr :5000

# Try rebuilding
docker-compose down -v
docker-compose up --build -d
```

### Prometheus Can't Scrape App
- Ensure app is running: `curl http://localhost:5000/health`
- Check container networking: `docker network ls`
- View Prometheus targets: http://localhost:9090/targets

### Grafana Dashboards Not Showing
- Verify datasource: `Configuration → Data Sources → Prometheus`
- Check test connection
- Import dashboards manually from `grafana/dashboards/*.json` if not auto-provisioned

### SMTP/Telegram Not Sending
- Verify credentials in `.env`: `SMTP_HOST`, `SMTP_USER`, `SMTP_PASS`, etc.
- Check logs: `docker-compose logs app`
- Test credentials manually:
```powershell
$cred = [System.Management.Automation.PSCredential]::new('user', (ConvertTo-SecureString 'pass' -AsPlainText -Force))
Send-MailMessage -From 'sender@example.com' -To 'to@example.com' -Subject 'test' -Body 'test' -SmtpServer 'smtp.example.com' -Credential $cred
```

### Pipeline Not Running (Scheduled)
- Check scheduled task (Windows):
  ```powershell
  Get-ScheduledTask -TaskName "ai-digest*"
  ```
- Check systemd status (Linux):
  ```bash
  sudo systemctl status ai-digest
  sudo journalctl -u ai-digest -n 50
  ```

---

## Performance Tuning

### Increase Embedding Batch Size
Edit `src/workflows/pipeline.py`:
```python
batch_size = 100  # default 1, increase for throughput
```

### Use Lighter LLM Model
In `.env`:
```
OLLAMA_URL=http://localhost:11434
# Pull a smaller model: ollama pull orca-mini
```

### Horizontal Scaling (Kubernetes)
```yaml
# Scale app replicas
kubectl scale deployment ai-digest --replicas=3
```

---

## Cleanup

### Local
```powershell
Remove-Item -Recurse .venv
Remove-Item ai_digest.db
Remove-Item -Recurse out/
```

### Docker
```powershell
docker-compose down -v
docker rmi ai_digest:latest
```

---

## Next Steps

1. **Set up email delivery**: Configure SMTP credentials
2. **Add content sources**: Update adapter config (Reddit, ProductHunt)
3. **Customize LLM prompts**: Edit `src/services/prompts.py`
4. **Create Grafana dashboards**: Import `grafana/dashboards/ai_digest_production.json`
5. **Schedule daily runs**: Use `--schedule` flag or systemd
6. **Monitor alerts**: Check Prometheus/Grafana for anomalies

---

**Status**: Beta v0.1.0  
**Support**: See DELIVERABLES.md, README.md, ARCHITECTURE.md
