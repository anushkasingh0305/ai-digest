# Docker Compose smoke test for AI Digest
# Usage: Open PowerShell as Administrator (or a user with Docker access) and run:
#   .\run_docker_smoke.ps1

function Check-Command($cmd){
    try{ Get-Command $cmd -ErrorAction Stop | Out-Null; return $true } catch { return $false }
}

if (-not (Check-Command 'docker')){
    Write-Error "Docker not found on PATH. Install Docker Desktop or enable WSL and install Docker Engine."
    exit 2
}

# Prefer new "docker compose" but fall back to docker-compose
$composeCmd = 'docker'
$composeArgsPrefix = 'compose'
if (-not (Check-Command 'docker')){
    if (-not (Check-Command 'docker-compose')){
        Write-Error "Neither 'docker' nor 'docker-compose' available on PATH."
        exit 2
    } else {
        $composeCmd = 'docker-compose'
        $composeArgsPrefix = ''
    }
}

Write-Host "Bringing up Docker Compose stack..."
& $composeCmd $composeArgsPrefix up --build -d

Write-Host "Waiting 10s for services to start..."
Start-Sleep -Seconds 10

function Check-Url($url){
    try{
        $res = Invoke-RestMethod -Uri $url -TimeoutSec 5
        Write-Host "OK: $url ->" -ForegroundColor Green
        return $true
    } catch {
        Write-Warning "FAIL: $url -> $_"
        return $false
    }
}

$results = @()
$results += Check-Url 'http://localhost:5000/health'
$results += Check-Url 'http://localhost:5000/metrics'
$results += Check-Url 'http://localhost:9090'
$results += Check-Url 'http://localhost:3000'

Write-Host "If any checks failed, view logs:"
Write-Host "  $composeCmd $composeArgsPrefix logs --tail 200"
Write-Host "When done, bring the stack down with:"
Write-Host "  $composeCmd $composeArgsPrefix down -v"

if ($results -contains $false){
    Write-Warning "Smoke test finished — some endpoints failed. Check logs and retry."
    exit 1
} else {
    Write-Host "Smoke test passed — all endpoints responded." -ForegroundColor Green
}
