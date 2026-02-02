# Contributing to AI Digest

Welcome! We're excited to have you contribute to AI Digest. This guide will help you get started.

## Code of Conduct

Please be respectful, inclusive, and professional in all interactions.

## Getting Started

### 1. Fork & Clone
```bash
git clone https://github.com/<your-username>/ai_digest.git
cd ai_digest
```

### 2. Create Virtual Environment
```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
# or
venv\Scripts\Activate.ps1  # Windows
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Create a Branch
```bash
git checkout -b feature/my-feature
# or
git checkout -b fix/my-bug
```

## Making Changes

### Code Style
- Follow PEP 8
- Use meaningful variable names
- Keep functions focused and testable
- Add docstrings for public functions

### Testing
```bash
# Run all tests
python -m pytest -q

# Run specific test file
python -m pytest tests/test_delivery.py -v

# Run with coverage
pip install pytest-cov
python -m pytest --cov=src tests/
```

**Test coverage target**: 80%+

### Adding a New Adapter

1. Create `src/tools/adapters_<source>.py`:
```python
import asyncio
from typing import List

class MySourceAdapter:
    async def fetch_items(self, hours: int = 24) -> List[dict]:
        # Implement fetching logic
        items = []
        # ... populate items
        return items
```

2. Add tests in `tests/test_adapters.py`

3. Update `README.md` to list the new source

4. Add required env vars to `.env.example`

### Adding a Delivery Channel

1. Add async function to `src/services/delivery.py`:
```python
async def send_slack(text: str, webhook_url: str = None) -> bool:
    # Implement sending logic
    pass
```

2. Add metrics in `src/services/metrics.py`:
```python
delivery_slack_success_total = Counter('ai_digest_delivery_slack_success_total', '...')
```

3. Add tests in `tests/test_delivery.py`

### Adding Metrics

1. Define counter/histogram in `src/services/metrics.py`
2. Increment in relevant code path
3. Add panel to `grafana/dashboards/ai_digest_production.json`
4. Add alert rule to `prometheus/alert_rules.yml` if needed

## Submitting a PR

1. **Push to your fork**:
```bash
git push origin feature/my-feature
```

2. **Open a Pull Request** on GitHub with:
   - Clear title (e.g., "Add Slack delivery adapter")
   - Description of changes
   - Reference any related issues (#123)

3. **Wait for CI/CD**:
   - GitHub Actions runs tests, lint, and Docker build
   - All checks must pass before merge
   - Maintainers review code

4. **Address feedback** (if any):
```bash
git add .
git commit --amend
git push --force-with-lease
```

## Documentation

Update docs if your changes affect:
- User configuration (`.env.example`)
- Deployment process (`DEPLOYMENT.md`)
- Features (`DELIVERABLES.md`)
- APIs (`src/server.py`)
- Architecture (`ARCHITECTURE.md`)

## Reporting Issues

- **Bug report**: Describe steps to reproduce, expected vs actual behavior
- **Feature request**: Explain use case and proposed solution
- **Discussion**: Ask questions in Discussions tab if unsure

## Project Structure

```
ai_digest/
├── src/                  # Source code
│   ├── cli/             # CLI entry points
│   ├── services/        # Core services (delivery, metrics, etc.)
│   ├── tools/           # Adapters (content sources)
│   ├── workflows/       # Pipeline orchestration
│   └── formatters.py    # Output formatting
├── tests/               # Unit tests
├── prometheus/          # Prometheus config & alerts
├── grafana/             # Grafana dashboards & provisioning
├── migrations/          # Alembic DB migrations
├── .github/workflows/   # CI/CD
├── DELIVERABLES.md      # Feature list & roadmap
├── DEPLOYMENT.md        # Setup guide
├── ARCHITECTURE.md      # Design docs
├── README.md            # Quick start
└── pyproject.toml       # Project metadata
```

## Development Workflow

1. **Local testing**: `python -m pytest -q`
2. **Docker testing**: `docker-compose up --build` (requires Docker)
3. **Manual testing**: `python -m src.cli.main --deliver`
4. **Metrics check**: Visit `http://localhost:5000/metrics`
5. **Push & watch CI**: GitHub Actions validates automatically

## Performance Tips

- Use asyncio for I/O-bound work (network, DB)
- Cache FAISS embeddings to avoid recomputation
- Profile bottlenecks with `cProfile` or `py-spy`
- Test with real-world data sizes before optimizing

## Questions?

- **Issues**: GitHub Issues tab
- **Discussions**: GitHub Discussions tab
- **Email**: See README.md for contact info

---

**Thank you for contributing!** 🎉  
Every PR, issue, and discussion makes AI Digest better.

Happy coding! 🚀
