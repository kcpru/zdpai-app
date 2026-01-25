# todo2 backend (Python)

Python rewrite of the existing todo2 backend using FastAPI + SQLAlchemy + Alembic.

## Requirements
- Python 3.12+
- PostgreSQL 16+

## Local setup
Create a virtual environment and install dependencies:

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

Create `.env` from the example:

```bash
cp .env.example .env
```

Run the app:

```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

Seed data automatically on startup when using Docker. For local runs, seed manually:

```bash
python -c "from app.db.init_db import seed_data; seed_data()"
```

## Migrations
Generate and apply migrations with Alembic:

```bash
alembic revision --autogenerate -m "initial"
alembic upgrade head
```

## Seed data
Seed demo data (optional) from a Python REPL:

```bash
python -c "from app.db.init_db import seed_data; seed_data()"
```

## Docker
Backend only (from this folder):

```bash
docker compose up --build
```

Full stack (backend + frontend + postgres) from repo root:

```bash
cd ..
docker compose up --build
```
