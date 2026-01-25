# todo2

Full‑stack aplikacja ToDo: backend w **FastAPI (Python)** + **PostgreSQL**, frontend w **React + Vite**.

## Szybki start (Docker)
Wymagania: Docker + Docker Compose.

```bash
docker compose up -d --build
```

Aplikacja: `http://localhost:8080`

## Development (opcjonalnie)

### Backend (Python)

```bash
cd backend
cp .env.example .env
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### Frontend (React/Vite)

```bash
cd frontend
npm install
npm run dev
```

Konfiguracja API: `VITE_API_URL` (np. `http://localhost:8000/api`).

## Docker (tylko backend)

```bash
cd backend
docker compose up --build
```
