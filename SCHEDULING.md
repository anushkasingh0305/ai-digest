# Scheduling Guide

## Overview

The AI Digest system supports automated scheduled digest runs using **APScheduler**. Run digests automatically at specific times daily without manual intervention.

## Quick Start

### Run Scheduler (Daily at 6 AM UTC)

```bash
python -m src.cli.main --schedule --deliver
```

### Run Scheduler (Custom Time)

```bash
# Daily at 2 PM UTC (14:00)
python -m src.cli.main --schedule --deliver --hour 14 --minute 0

# Daily at 9:30 AM UTC
python -m src.cli.main --schedule --deliver --hour 9 --minute 30
```

### Without Delivery

If you only want to generate digests without sending them:

```bash
python -m src.cli.main --schedule
```

## Command-Line Options

| Option | Type | Default | Description |
|--------|------|---------|-------------|
| `--schedule` | flag | - | Enable scheduled mode (background) |
| `--deliver` | flag | - | Send digest via email and Telegram |
| `--hour` | int | 6 | Hour for daily digest (0-23, UTC) |
| `--minute` | int | 0 | Minute for daily digest (0-59) |
| `--log-level` | string | INFO | Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL) |
| `--log-file` | string | logs/ai_digest.log | Path to log file |

## Time Zones

**Important**: All times are in **UTC (Coordinated Universal Time)**. Adjust the `--hour` parameter to match your timezone:

- EST (UTC-5): Use `--hour 11` for 6 AM EST
- PST (UTC-8): Use `--hour 14` for 6 AM PST
- CET (UTC+1): Use `--hour 5` for 6 AM CET
- IST (UTC+5:30): Use `--hour 0` for 5:30 AM IST

## Running Continuously

### Option 1: Terminal (Development)

```bash
python -m src.cli.main --schedule --deliver --hour 6 --minute 0
```

Press `Ctrl+C` to stop gracefully.

### Option 2: systemd Service (Linux Production)

1. **Install the service file:**

```bash
sudo cp ai-digest-scheduler.service /etc/systemd/system/
```

2. **Create user and directories:**

```bash
sudo useradd -r -s /bin/bash ai_digest
sudo mkdir -p /opt/ai_digest /var/log/ai_digest
sudo chown -R ai_digest:ai_digest /opt/ai_digest /var/log/ai_digest
```

3. **Copy project to system location:**

```bash
sudo cp -r . /opt/ai_digest/
sudo chown -R ai_digest:ai_digest /opt/ai_digest
```

4. **Setup virtual environment:**

```bash
cd /opt/ai_digest
sudo -u ai_digest python3 -m venv .venv
sudo -u ai_digest .venv/bin/pip install -r requirements.txt
```

5. **Create .env file:**

```bash
sudo -u ai_digest cp .env.example /opt/ai_digest/.env
# Edit with your credentials
sudo -u ai_digest nano /opt/ai_digest/.env
```

6. **Enable and start service:**

```bash
sudo systemctl daemon-reload
sudo systemctl enable ai-digest-scheduler
sudo systemctl start ai-digest-scheduler
```

7. **Check status:**

```bash
sudo systemctl status ai-digest-scheduler
sudo journalctl -u ai-digest-scheduler -f  # Follow logs
```

### Option 3: Docker (Any Platform)

Add to `docker-compose.yml`:

```yaml
scheduler:
  build: .
  container_name: ai_digest_scheduler
  command: python -m src.cli.main --schedule --deliver --hour 6 --minute 0
  environment:
    - LOG_LEVEL=INFO
  env_file:
    - .env
  volumes:
    - ./logs:/app/logs
  networks:
    - ai_digest_network
  restart: unless-stopped
  depends_on:
    - app  # Optional: wait for app service
```

Start with:

```bash
docker-compose up -d scheduler
docker-compose logs -f scheduler
```

### Option 4: Windows Task Scheduler

1. **Create batch script** (`run_scheduler.bat`):

```batch
@echo off
cd C:\path\to\ai_digest
.\.venv\Scripts\python.exe -m src.cli.main --schedule --deliver --hour 6 --minute 0
pause
```

2. **Create scheduled task:**

```powershell
# Run as Administrator
$taskPath = "AI Digest\"
$taskName = "Daily Digest Scheduler"
$scriptPath = "C:\path\to\ai_digest\run_scheduler.bat"

$action = New-ScheduledTaskAction -Execute $scriptPath
$trigger = New-ScheduledTaskTrigger -Daily -At 6:00am
$settings = New-ScheduledTaskSettingsSet -StartWhenAvailable -RunOnlyIfNetworkAvailable

Register-ScheduledTask -TaskName $taskName -Action $action -Trigger $trigger -Settings $settings -Force
```

Or use Task Scheduler GUI:
- Open Task Scheduler
- Create Basic Task
- Set daily trigger (convert to UTC: 6 AM = offset + local time)
- Action: Start program (`run_scheduler.bat`)
- Enable running with or without login

## Monitoring Scheduled Runs

### View Scheduled Jobs

The scheduler logs all jobs at startup:

```
Scheduled jobs: 1
  - daily at 06:00 UTC (next: 2026-01-30T06:00:00)
```

### View Logs

```bash
# Last 100 lines
tail -n 100 logs/ai_digest.log

# Follow in real-time
tail -f logs/ai_digest.log

# Filter by scheduler component
grep '"component": "scheduler"' logs/ai_digest.log | python -m json.tool

# Filter by job
grep '"job_id"' logs/ai_digest.log
```

### Docker Logs

```bash
docker-compose logs -f scheduler
```

### systemd Logs

```bash
# Last 50 lines
sudo journalctl -u ai-digest-scheduler -n 50

# Follow in real-time
sudo journalctl -u ai-digest-scheduler -f

# Since last boot
sudo journalctl -u ai-digest-scheduler -b
```

## Logging

Scheduled runs produce detailed JSON logs including:

- **Job start/stop**: When digest run starts and finishes
- **Component breakdown**: Ingest, embedding, delivery stages
- **Errors with context**: Full exception traces and error details
- **Timing**: When each job will run next

Example log output:

```json
{"timestamp": "2026-01-29T06:00:00.123456", "level": "INFO", "message": "Scheduled pipeline run started", "component": "scheduler", "deliver": true}
{"timestamp": "2026-01-29T06:00:05.234567", "level": "INFO", "message": "Scheduled pipeline run completed", "component": "scheduler"}
```

## Graceful Shutdown

### Terminal

Press `Ctrl+C` to stop gracefully:

```
Interrupt signal received, shutting down scheduler
Scheduler stopped.
```

### systemd

```bash
sudo systemctl stop ai-digest-scheduler
```

### Docker

```bash
docker-compose down scheduler
```

The scheduler waits for any running jobs to complete before exiting (up to 30 seconds for systemd, 10 seconds for Docker).

## Advanced Configuration

### Multiple Jobs

Schedule digests at multiple times:

```python
from src.services.scheduler import start_scheduler, schedule_job

# Start scheduler
scheduler = start_scheduler(deliver=True)

# Morning digest at 6 AM
schedule_job("morning", hour=6, minute=0, deliver=True)

# Evening digest at 6 PM
schedule_job("evening", hour=18, minute=0, deliver=True)
```

Or via CLI (start scheduler, then manually call scheduler functions in a script):

```python
# Example: manual_schedule.py
import sys
sys.path.insert(0, '.')
from src.services.scheduler import start_scheduler, schedule_job, list_jobs

scheduler = start_scheduler(deliver=True)
schedule_job("morning", hour=6, minute=0, deliver=True)
schedule_job("evening", hour=18, minute=0, deliver=True)

jobs = list_jobs()
for job in jobs:
    print(f"{job['name']}: {job['next_run_time']}")
```

### Pause/Resume Jobs

```python
from src.services.scheduler import pause_job, resume_job

pause_job("daily_digest_6am")   # Temporarily stop
resume_job("daily_digest_6am")  # Resume
```

### Remove Jobs

```python
from src.services.scheduler import remove_job

remove_job("daily_digest_6am")  # Permanently remove
```

## Troubleshooting

### Scheduler doesn't start

1. Check that APScheduler is installed:
   ```bash
   pip list | grep APScheduler
   ```

2. Check logging output for errors:
   ```bash
   python -m src.cli.main --schedule --log-level DEBUG
   ```

3. Verify time parameters:
   ```bash
   python -m src.cli.main --schedule --hour 24  # ERROR: hour must be 0-23
   ```

### Jobs not running at expected time

1. **Timezone issue**: All times are UTC. Verify `--hour` is correct for your timezone.

2. **Machine clock off**: Check system time:
   ```bash
   date  # Unix/Linux
   Get-Date  # PowerShell
   ```

3. **System sleep**: Ensure system doesn't sleep. On systemd, service runs in background.

4. **Permissions**: Check logs for permission errors:
   ```bash
   sudo journalctl -u ai-digest-scheduler -n 20 --no-pager
   ```

### Memory/CPU issues

1. Check resource limits in service file:
   ```bash
   grep -E "^Memory|^CPU" ai-digest-scheduler.service
   ```

2. Monitor during run:
   ```bash
   watch -n 1 'ps aux | grep python'
   ```

### No delivery emails/messages

1. Verify delivery credentials in `.env`:
   ```bash
   grep -E "DELIVERY|SMTP|TELEGRAM" .env
   ```

2. Check delivery logs:
   ```bash
   grep '"component": "delivery' logs/ai_digest.log | tail -5
   ```

3. Test delivery manually:
   ```bash
   python -m src.cli.main --deliver
   ```

## Best Practices

1. **Start early**: Run digests early in the day so users see them fresh
   - Recommendation: 6-8 AM local time

2. **Avoid peak hours**: Don't run during high system load
   - Recommendation: Off-peak hours (early morning, late evening)

3. **Monitor logs regularly**: Set up log rotation to prevent disk fill
   - Default: 10MB files with 5 backups

4. **Test delivery**: Run `python -m src.cli.main --deliver` once manually to verify

5. **Use systemd**: For production Linux deployments, systemd handles restarts and logging

6. **Docker for consistency**: Use Docker Compose for consistent deployments across environments

## Example Setups

### Personal Use (6 AM Daily)

```bash
python -m src.cli.main --schedule --deliver
```

### Team (Morning & Evening)

```python
from src.services.scheduler import start_scheduler, schedule_job
scheduler = start_scheduler(deliver=True)
schedule_job("morning", hour=6, minute=0)
schedule_job("evening", hour=18, minute=0)
```

### Production Linux (systemd)

```bash
sudo systemctl enable ai-digest-scheduler
sudo systemctl start ai-digest-scheduler
sudo journalctl -u ai-digest-scheduler -f
```

### Production Docker

```bash
docker-compose up -d scheduler
docker-compose logs -f scheduler
```

### Development (Debug Mode)

```bash
python -m src.cli.main --schedule --deliver --log-level DEBUG
```
