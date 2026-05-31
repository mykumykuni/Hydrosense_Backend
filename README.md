# HydroSense Backend

Real-time water quality monitoring backend for the HydroSense platform. Connects to web and mobile frontends via REST API and WebSocket.

## Architecture

```
IoT Sensors
    │
    ▼
FastAPI Service (port 8001)   ──POST /api/sensors/readings/──▶   Django Backend (port 8000)
  sensor ingestion                  X-Api-Key header                  REST API + WebSocket
                                                                            │
                                                                            ▼
                                                                     PostgreSQL (Supabase)
```

| Service | Port | Purpose |
|---------|------|---------|
| Django (Daphne) | 8000 | Main API, auth, WebSocket |
| FastAPI | 8001 | IoT sensor data ingestion |

## Tech Stack

- **Django 4.2** + Django REST Framework
- **FastAPI** (sensor ingestion microservice)
- **Django Channels** + Daphne (WebSocket / ASGI)
- **PostgreSQL** (Supabase or local)
- **JWT** authentication (simplejwt)

## Prerequisites

- Python 3.10+
- PostgreSQL (local) or a Supabase project
- Redis *(optional — only needed for multi-worker WebSocket in production)*

## Setup

### 1. Clone and create virtual environment

```powershell
git clone <repo-url>
cd Hydrosense_Backend
python -m venv .venv
& ".venv\Scripts\Activate.ps1"
```

### 2. Install dependencies

```powershell
# Django backend
cd django_backend
pip install -r requirements.txt

# FastAPI service (separate terminal)
cd ../fastapi_service
pip install -r requirements.txt
```

### 3. Configure environment

Copy `.env.example` to `.env` and fill in your values:

```powershell
Copy-Item .env.example .env
```

Key variables:

| Variable | Description |
|----------|-------------|
| `SECRET_KEY` | Django secret key |
| `DATABASE_URL` | Cloud DB connection string (Supabase/Render/etc.) |
| `DB_*` | Local PostgreSQL credentials (used if `DATABASE_URL` is blank) |
| `INTERNAL_API_KEY` | Shared secret between FastAPI and Django |
| `REDIS_URL` | Redis URL for WebSocket (leave blank for in-memory dev mode) |

### 4. Run migrations

```powershell
cd django_backend
python manage.py migrate
python manage.py createsuperuser
```

### 5. Start the servers

**Django (ASGI — required for WebSocket):**
```powershell
cd django_backend
daphne -p 8000 hydrosense.asgi:application
```

**FastAPI:**
```powershell
cd fastapi_service
uvicorn app.main:app --port 8001 --reload
```

## WebSocket

Connect with a valid JWT access token:

```
ws://localhost:8000/ws/?token=<access_token>
```

**Events pushed to clients:**

| Event type | Trigger |
|------------|---------|
| `sensor.reading` | New sensor reading received |
| `alert.new` | Alert created |
| `alert.resolved` | Alert marked resolved |

## Django Admin

Available at `http://localhost:8000/admin/` after creating a superuser.

## Running Tests

```powershell
cd django_backend
python manage.py test
```
