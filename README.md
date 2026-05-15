# CMP9134 Robot Management System

A web-based Ground Control Station for monitoring and controlling a virtual autonomous robot. Built for the CMP9134 Software Engineering module at the University of Lincoln.

## Stack

| Layer | Technology |
|---|---|
| Backend | FastAPI (Python 3.12), SQLModel, Alembic |
| Frontend | React + TypeScript, Vite |
| Database | PostgreSQL 17 |
| Cache / Locks | Redis |
| Robot Simulator | `ghcr.io/francescodelduchetto/cmp9134_2526_robotsim` |
| Containerisation | Docker + Docker Compose |
| CI/CD | GitHub Actions |

## Features

- Real-time robot telemetry via WebSocket
- 2D grid map display with live robot position
- Navigation commands (UP, DOWN, LEFT, RIGHT) with boundary clamping
- Role-Based Access Control: Viewer (read-only) and Commander (can move/reset robot)
- Mission audit log — every command is persisted with timestamp and user
- Connection status indicators: Connecting, Reconnecting, Signal Lost
- JWT authentication with refresh token rotation

---

## Quick Start (Docker)

### Prerequisites

- [Docker](https://docs.docker.com/get-docker/) and Docker Compose installed
- Port `8080` (frontend), `8000` (backend), and `5555` (robot) available

### 1. Clone the repository

```bash
git clone https://github.com/dakohhh/cmp9134-2526.git
cd cmp9134-2526/backend
```

### 2. Start the full stack

```bash
docker compose up --build
```

This starts:
- `robot-frontend` → [http://localhost:8080](http://localhost:8080)
- `robot-backend` → [http://localhost:8000](http://localhost:8000)
- `database` (PostgreSQL)
- `redis`
- `cmp9134_2526_robot` (virtual robot simulator)

Alembic migrations run automatically on backend startup. A default commander account is seeded on first run.

### 3. Open the dashboard

Navigate to [http://localhost:8080](http://localhost:8080) and log in with the default commander credentials:

| Field    | Value               |
|----------|---------------------|
| Email    | `admin@robot.com`   |
| Password | `password`          |

> **Note:** Change the default password after first login. All newly registered users are assigned the **Viewer** role and can be promoted to **Commander** via the Users page (visible to commanders only).

---

## Local Development

### Prerequisites

- Python 3.12
- [Poetry](https://python-poetry.org/docs/#installation)
- Node.js 18+

### Backend

```bash
# Install dependencies
poetry install

# Copy and fill in environment variables
cp .env.example .env

# Start dev services (Postgres + Redis + Robot)
docker compose -f docker-compose-dev.yaml up -d

# Run migrations
alembic upgrade head

# Start the backend
uvicorn app.main:create_app --factory --reload
```

### Frontend

```bash
cd frontend
npm install
npm run dev
```

### Environment Variables

| Variable | Description | Example |
|---|---|---|
| `PYTHON_ENV` | Environment (`development` / `production` / `testing`) | `development` |
| `JWT_SECRET_KEY` | Secret key for signing JWTs | `change-me-in-production` |
| `DATABASE_URL` | PostgreSQL connection string | `postgresql+asyncpg://user:pass@localhost:5433/db` |
| `REDIS_URL` | Redis connection string | `redis://localhost:6379/0` |
| `BASE_ROBOT_API_URL` | Base URL of the robot simulator | `http://localhost:5555` |

---

## Testing

### API Tests (no services needed beyond test DB)

```bash
# Start test database
docker compose -f docker-compose-test.yaml up -d test_db

# Run unit + API tests
poetry run pytest tests/unit/ tests/api/ -v
```

### Integration Tests (requires real robot + Redis)

```bash
# Start all test services
docker compose -f docker-compose-test.yaml up -d

# Run integration tests
poetry run pytest tests/integration/ -v
```

### Type Checking

```bash
poetry run mypy .
```

---

## CI/CD

GitHub Actions workflow (`.github/workflows/test.yml`) runs on every pull request to `main`:

1. **lint** — runs `mypy` type checking
2. **test** — runs unit tests and API tests against a live PostgreSQL container

---

## Project Structure

```
backend/
├── app/
│   ├── auth/          # JWT authentication
│   ├── user/          # User model and roles
│   ├── robot/         # Robot navigation service
│   ├── map/           # Map retrieval and caching
│   ├── audit_log/     # Mission logging
│   ├── admin/         # Role management
│   ├── cache/         # Redis / in-memory cache
│   ├── common/        # Shared dependencies, exceptions, response models
│   └── main.py        # FastAPI app factory + lifespan
├── frontend/          # React + TypeScript dashboard
├── tests/
│   ├── unit/          # Pure logic tests (no I/O)
│   ├── api/           # Full HTTP tests with mocked external services
│   └── integration/   # Tests against real robot container and Redis
├── migrations/        # Alembic migration scripts
├── settings/          # Pydantic settings config
├── docker-compose.yaml
├── docker-compose-dev.yaml
├── docker-compose-test.yaml
└── AI_USAGE.md        # AI assistance log
```
