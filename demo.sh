#!/usr/bin/env bash
# Demo script: End-to-end AI Digest walkthrough
# Usage: ./demo.sh

set -euo pipefail

echo "========================================="
echo "AI Digest Demo — End-to-End Walkthrough"
echo "========================================="
echo ""

# Step 1: Check Python
echo "[1/6] Checking Python environment..."
python --version
echo "✓ Python is available"
echo ""

# Step 2: Install dependencies (if not already done)
echo "[2/6] Installing dependencies..."
if [ ! -d ".venv" ]; then
    python -m venv .venv
    source .venv/bin/activate
    pip install -q -r requirements.txt
else
    source .venv/bin/activate
fi
echo "✓ Dependencies installed"
echo ""

# Step 3: Copy .env.example if .env doesn't exist
echo "[3/6] Setting up configuration..."
if [ ! -f ".env" ]; then
    cp .env.example .env
    echo "  Created .env from .env.example"
    echo "  NOTE: Edit .env with your SMTP/Telegram credentials if desired"
fi
echo "✓ Configuration ready"
echo ""

# Step 4: Run tests
echo "[4/6] Running unit tests..."
python -m pytest tests/ -q --tb=short
echo "✓ All tests passed"
echo ""

# Step 5: Run pipeline
echo "[5/6] Running AI Digest pipeline..."
echo "  Ingesting items from placeholder adapter..."
python -m src.cli.main
echo "✓ Pipeline completed"
echo ""

# Step 6: Show results
echo "[6/6] Pipeline output:"
if [ -f "out/digest.json" ]; then
    echo "  Digest saved to: out/digest.json"
    echo "  Contents:"
    python -c "import json; data = json.load(open('out/digest.json')); print('    - Items:', len(data.get('items', []))); [print(f'      * {i.get(\"title\", \"(no title)\")}') for i in data.get('items', [])]"
else
    echo "  (No output file found)"
fi
echo ""

echo "========================================="
echo "Demo Complete!"
echo "========================================="
echo ""
echo "Next steps:"
echo "1. Configure .env with real credentials (SMTP, Telegram, etc.)"
echo "2. Run with delivery: python -m src.cli.main --deliver"
echo "3. Start Docker stack: docker-compose up --build -d"
echo "4. Visit Grafana: http://localhost:3000"
echo ""
echo "For more info, see:"
echo "  - README.md — Quick start"
echo "  - DEPLOYMENT.md — Full setup guide"
echo "  - DELIVERABLES.md — Features & roadmap"
echo ""
