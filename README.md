# AI Digest � Local-first Intelligence Digest

## Quickstart

1. Create and activate a virtualenv:

\\\powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
\\\

2. Copy \.env.example\ to \.env\ and set any credentials.

3. Run a simple pipeline run:

\\\powershell
python -m src.cli.main --deliver
\\\

For debugging with detailed logs:

\\\powershell
python -m src.cli.main --deliver --log-level DEBUG
\\\

See [LOGGING.md](LOGGING.md) for structured logging documentation.

## Docker Compose (Optional)

\\\powershell
docker-compose up --build
\\\

Note: In this environment Docker was not available on PATH; if you see "docker: not found", install Docker Desktop or run the stack inside WSL/Linux.

### Health Checks and Verification

\\\powershell
# Prometheus UI (if compose started):
http://localhost:9090

# Grafana UI:
http://localhost:3000 (default admin/admin)

# App health (if your app exposes /health):
http://localhost:5000/health

# Metrics endpoint:
http://localhost:5000/metrics
\\\

## Logging

All operations are logged with structured JSON format. Configure logging via:

- **CLI flag**: \--log-level DEBUG|INFO|WARNING|ERROR|CRITICAL\
- **Environment**: \LOG_LEVEL=INFO\ in .env
- **Output**: Console (stdout) and file (\logs/ai_digest.log\)

Example with detailed logging:

\\\powershell
python -m src.cli.main --deliver --log-level DEBUG --log-file logs/custom.log
\\\

See [LOGGING.md](LOGGING.md) for complete documentation on log levels, components, parsing, and best practices.

## Benchmark

Run performance benchmarks for embedding/deduplication:

\\\powershell
python benchmark.py --mode full --count 200
\\\

## Final Docker Checklist

- Install Docker Desktop (Windows) and enable WSL2 integration, or install Docker Engine in Linux/WSL.
- Ensure ports 5000, 9090, 3000, and 11434 are free or adjust \docker-compose.yml\.
- Copy \.env.example\ to \.env\ and set any credentials (e.g., \DATABASE_URL\, \SMTP_*\, \TELEGRAM_*\).
- Start the stack and run the smoke test script:

**Windows PowerShell:**

\\\powershell
cd C:\Users\<you>\ai_digest
.\run_docker_smoke.ps1
\\\

**WSL / Linux:**

\\\ash
cd ~/ai_digest
chmod +x run_docker_smoke.sh
./run_docker_smoke.sh
\\\

If anything fails, check container status and logs:

\\\powershell
docker ps -a
docker compose logs --tail 200
docker compose down -v
\\\

## Notes on Grafana Provisioning

- Grafana will load dashboards and datasource from \./grafana/provisioning\ and dashboards from \./grafana/dashboards\.
- If dashboards don't appear, open Grafana UI and check \Configuration  Data Sources\ and \Configuration  Dashboards\.

## Documentation

- [LOGGING.md](LOGGING.md) � Structured JSON logging guide
- [DEPLOYMENT.md](DEPLOYMENT.md) � Setup and deployment guides
- [CONTRIBUTING.md](CONTRIBUTING.md) � Contributing guidelines
- [DELIVERABLES.md](DELIVERABLES.md) � Feature checklist and tech stack
- [ROADMAP.md](ROADMAP.md) � Future roadmap

This scaffold provides a runnable skeleton; customize adapters, LLM client, and delivery channels for your use case.
