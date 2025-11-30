# Blackjack Game - DevOps Edition

A web-based Blackjack game built with FastAPI, featuring comprehensive DevOps practices including CI/CD, containerization, monitoring, and automated testing.

## Features

- 🎰 Classic Blackjack gameplay
- 💾 Persistent game state with database storage
- 📊 Real-time metrics and monitoring
- 🐳 Docker containerization
- 🔄 CI/CD pipeline with Azure DevOps
- ✅ 70%+ test coverage

## Tech Stack

- **Backend**: FastAPI, SQLAlchemy
- **Database**: SQLite (dev) / PostgreSQL (production)
- **Testing**: pytest, pytest-cov
- **Monitoring**: Prometheus, Grafana
- **CI/CD**: Azure DevOps
- **Container**: Docker, Docker Compose

## Project Structure

```
blackjack-devops/
├── app/
│   ├── core/           # Configuration and database
│   ├── models/         # Data models and schemas
│   ├── routes/         # API endpoints
│   └── services/       # Business logic
├── tests/              # Test suite
├── static/             # CSS and JavaScript
├── templates/          # HTML templates
├── monitoring/         # Prometheus and Grafana config
├── Dockerfile
├── docker-compose.yml
├── azure-pipelines.yml
└── requirements.txt
```

## Quick Start

### Local Development

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd blackjack-devops
   ```

2. **Create virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure environment** (optional)
   ```bash
   cp .env.example .env
   # Edit .env as needed
   ```

5. **Run the application**
   ```bash
   python main.py
   # Or with uvicorn:
   uvicorn main:app --reload
   ```

6. **Open in browser**
   ```
   http://localhost:8000
   ```

### Using Docker

1. **Build and run with Docker Compose**
   ```bash
   docker-compose up --build
   ```

2. **Access services**
   - Application: http://localhost:8000
   - Prometheus: http://localhost:9090
   - Grafana: http://localhost:3000 (admin/admin)

## Running Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=app --cov-report=html

# Run specific test file
pytest tests/test_game_service.py -v

# Run with verbose output
pytest -v --tb=short
```

## API Endpoints

### Game Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/` | Home page |
| POST | `/api/start-game?bet={amount}` | Start new game |
| POST | `/api/hit` | Draw a card |
| POST | `/api/stand` | Stand (dealer plays) |
| GET | `/api/stats` | Get player statistics |
| POST | `/api/reset` | Reset player balance |

### Monitoring Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/health` | Health check |
| GET | `/metrics` | JSON metrics |
| GET | `/metrics/prometheus` | Prometheus format |
| GET | `/ready` | Readiness probe |
| GET | `/live` | Liveness probe |

## Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `DATABASE_URL` | `sqlite:///./blackjack.db` | Database connection string |
| `INITIAL_BALANCE` | `100` | Starting player balance |
| `MIN_BET` | `1` | Minimum bet amount |
| `MAX_BET` | `1000` | Maximum bet amount |
| `DEBUG` | `false` | Enable debug mode |

## CI/CD Pipeline

The Azure DevOps pipeline includes:

1. **Build Stage**
   - Install dependencies
   - Run linters (Ruff, Black)
   - Execute tests with coverage
   - Fail if coverage < 70%

2. **Docker Build Stage**
   - Build Docker image
   - Push to Azure Container Registry

3. **Deploy Stage**
   - Deploy to Azure Web App
   - Post-deployment health check

## Monitoring

### Metrics Available

- `blackjack_requests_total` - Total HTTP requests
- `blackjack_errors_total` - Total errors
- `blackjack_response_time_ms` - Average response time
- `blackjack_active_games` - Games in progress
- `blackjack_total_players` - Registered players
- `blackjack_uptime_seconds` - Application uptime

### Grafana Dashboard

Pre-configured dashboard includes:
- Request rate visualization
- Error rate tracking
- Response time graphs
- Active games counter
- Player statistics

## Deployment to Azure

### Prerequisites

1. Azure subscription
2. Azure Container Registry
3. Azure Web App for Containers
4. Azure Database for PostgreSQL (optional)

### Azure DevOps Setup

1. Create a new Azure DevOps project
2. Import this repository
3. Create a new pipeline using `azure-pipelines.yml`
4. Configure pipeline variables:
   - `DOCKER_REGISTRY` - ACR login server
   - `AZURE_SUBSCRIPTION` - Service connection name
   - `AZURE_WEBAPP_NAME` - Web app name
   - `AZURE_RESOURCE_GROUP` - Resource group name

### Manual Deployment

```bash
# Build Docker image
docker build -t blackjack-app .

# Tag for Azure Container Registry
docker tag blackjack-app <registry>.azurecr.io/blackjack-app:latest

# Push to ACR
docker push <registry>.azurecr.io/blackjack-app:latest
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Run tests and ensure coverage >= 70%
5. Submit a pull request

## License

MIT License - see LICENSE file for details.
