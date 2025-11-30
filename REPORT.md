# Assignment 2 Report: DevOps Improvements

## Executive Summary

This report documents the improvements made to the Blackjack application from Assignment 1, focusing on code quality, testing, CI/CD pipeline implementation, deployment automation, and monitoring.

---

## 1. Code Quality and Refactoring

### 1.1 Code Smells Removed

**Before:** The original application had several code smells:
- All code in a single `main.py` file (~150 lines)
- Global mutable state (`game_state = Game()`)
- Hardcoded values (balance=100, dealer threshold=17)
- No separation of concerns
- No database persistence (in-memory only)

**After:** The refactored application follows clean architecture:

```
app/
├── core/           # Configuration and infrastructure
│   ├── config.py   # Centralized configuration
│   └── database.py # Database connection
├── models/         # Domain models
│   ├── card.py     # Card, Deck value objects
│   ├── database.py # SQLAlchemy ORM models
│   └── schemas.py  # Pydantic validation schemas
├── routes/         # API endpoints
│   ├── game.py     # Game endpoints
│   └── health.py   # Health/metrics endpoints
└── services/       # Business logic
    ├── game_service.py    # Game logic
    └── metrics_service.py # Metrics collection
```

### 1.2 SOLID Principles Applied

| Principle | Implementation |
|-----------|----------------|
| **Single Responsibility** | Each module has one purpose: `card.py` handles cards, `game_service.py` handles game logic |
| **Open/Closed** | Configuration via environment variables allows behavior changes without code modification |
| **Liskov Substitution** | Database abstraction allows SQLite/PostgreSQL interchangeability |
| **Interface Segregation** | Separate schemas for different API operations |
| **Dependency Injection** | Database sessions injected via FastAPI's `Depends()` |

### 1.3 Key Improvements

1. **Configuration Management**
   - Environment variables via `pydantic-settings`
   - Centralized in `app/core/config.py`
   - No hardcoded values

2. **Database Persistence**
   - SQLAlchemy ORM with proper models
   - Session-based player tracking
   - Game state persisted across requests

3. **Type Safety**
   - Pydantic models for validation
   - Type hints throughout codebase
   - Immutable Card value objects (`@dataclass(frozen=True)`)

---

## 2. Testing and Coverage

### 2.1 Test Suite Overview

| Test File | Tests | Description |
|-----------|-------|-------------|
| `test_card.py` | 17 | Card and Deck unit tests |
| `test_game_service.py` | 19 | Game logic unit tests |
| `test_api.py` | 18 | API integration tests |
| `test_metrics.py` | 11 | Metrics service tests |
| **Total** | **72** | |

### 2.2 Coverage Report

```
Name                              Cover
─────────────────────────────────────────
app/core/config.py                100%
app/core/database.py               67%
app/models/card.py                100%
app/models/database.py             98%
app/models/schemas.py             100%
app/routes/game.py                 97%
app/routes/health.py               92%
app/services/game_service.py       78%
app/services/metrics_service.py   100%
─────────────────────────────────────────
TOTAL                             89.58%
```

**Coverage achieved: 89.58%** (Required: 70%)

### 2.3 Test Categories

- **Unit Tests**: Card operations, score calculations, business logic
- **Integration Tests**: API endpoints, database interactions
- **Edge Cases**: Invalid bets, session handling, blackjack scenarios

---

## 3. CI/CD Pipeline

### 3.1 Pipeline Stages

```yaml
Stages:
  1. Build
     ├── Setup Python 3.11
     ├── Install dependencies
     ├── Run Ruff linter
     ├── Run Black formatter check
     ├── Run MyPy type checker
     ├── Execute pytest with coverage
     └── Publish test results and coverage

  2. DockerBuild (main branch only)
     ├── Login to Azure Container Registry
     └── Build and push Docker image

  3. Deploy (main branch only)
     ├── Deploy to Azure Web App
     └── Post-deployment health check
```

### 3.2 Quality Gates

| Gate | Threshold | Failure Behavior |
|------|-----------|------------------|
| Test Coverage | 70% | Pipeline fails |
| Test Results | 100% passing | Pipeline fails |
| Linting | No errors | Warning (continues) |
| Health Check | 200 OK | Pipeline fails |

### 3.3 Pipeline Configuration

The pipeline is defined in `azure-pipelines.yml` with:
- Automatic triggers on `main` and `develop` branches
- Pull request validation
- Dependency caching for faster builds
- Artifact publishing for coverage reports

---

## 4. Deployment and Containerization

### 4.1 Docker Configuration

**Multi-stage Dockerfile:**
- Build stage: Installs dependencies in virtual environment
- Production stage: Minimal runtime image with non-root user

**Features:**
- Based on `python:3.11-slim`
- Non-root user (`appuser`) for security
- Built-in health check
- Optimized layer caching

### 4.2 Docker Compose Stack

```yaml
Services:
  - app (port 8000)       # FastAPI application
  - db (port 5432)        # PostgreSQL database
  - prometheus (port 9090) # Metrics collection
  - grafana (port 3000)    # Visualization dashboard
```

### 4.3 Azure Deployment

**Target Platform:** Azure Web App for Containers

**Configuration:**
- Azure Container Registry for image storage
- Environment-based configuration via App Settings
- Automatic deployment on main branch push
- Database via Azure Database for PostgreSQL

---

## 5. Monitoring and Health Checks

### 5.1 Health Endpoints

| Endpoint | Purpose | Response |
|----------|---------|----------|
| `/health` | Full health check | Status, version, database, uptime |
| `/live` | Liveness probe | Simple alive status |
| `/ready` | Readiness probe | Database connectivity |
| `/metrics` | JSON metrics | Request counts, response times |
| `/metrics/prometheus` | Prometheus format | Scrape-ready metrics |

### 5.2 Metrics Exposed

```
blackjack_requests_total      # Total HTTP requests
blackjack_errors_total        # Total errors
blackjack_response_time_ms    # Average response time
blackjack_active_games        # Games in progress
blackjack_total_players       # Registered players
blackjack_uptime_seconds      # Application uptime
```

### 5.3 Grafana Dashboard

Pre-configured dashboard includes:
- Request rate panels
- Error tracking
- Response time graphs
- Active games gauge
- Player count
- Uptime counter

---

## 6. Documentation

### 6.1 Files Created

| File | Purpose |
|------|---------|
| `README.md` | Comprehensive setup and usage guide |
| `REPORT.md` | This improvement summary |
| `.env.example` | Environment variable template |
| `requirements.txt` | Python dependencies |
| `pyproject.toml` | Tool configurations |

### 6.2 Code Documentation

- Docstrings on all public functions
- Type hints throughout
- Inline comments for complex logic
- Clear module-level documentation

---

## 7. Summary of Improvements

| Category | Before | After |
|----------|--------|-------|
| **Lines of Code** | ~150 (1 file) | ~1500 (organized modules) |
| **Test Coverage** | 0% | 89.58% |
| **Database** | In-memory | Persistent (SQLite/PostgreSQL) |
| **Configuration** | Hardcoded | Environment variables |
| **Deployment** | Manual | Automated CI/CD |
| **Monitoring** | None | Health checks + Prometheus + Grafana |
| **Documentation** | None | README + REPORT + docstrings |

---

## 8. How to Run

```bash
# Local development
pip install -r requirements.txt
python main.py

# Docker (with database and monitoring)
docker-compose up --build

# Run tests
pytest --cov=app --cov-report=html
```

---

*Report generated for Individual Assignment 2 - IE University SDDO 2025*
