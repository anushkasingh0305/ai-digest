#!/usr/bin/env bash
# Docker Compose smoke test for AI Digest (WSL / Linux)
# Usage: ./run_docker_smoke.sh
set -euo pipefail

COMPOSE_CMD="docker compose"
if ! command -v docker >/dev/null 2>&1; then
  echo "docker not found on PATH. Install Docker or run in environment with Docker." >&2
  exit 2
fi

echo "Bringing up Docker Compose stack..."
$COMPOSE_CMD up --build -d

echo "Waiting 10s for services to start..."
sleep 10

check_url(){
  url=$1
  if curl -fsS --max-time 5 "$url" >/dev/null; then
    echo "OK: $url"
  else
    echo "FAIL: $url" >&2
  fi
}

check_url http://localhost:5000/health
check_url http://localhost:5000/metrics
check_url http://localhost:9090
check_url http://localhost:3000

echo "If any checks failed, view logs:"
echo "  $COMPOSE_CMD logs --tail 200"
echo "When done, bring the stack down with:"
echo "  $COMPOSE_CMD down -v"
