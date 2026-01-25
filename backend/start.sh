#!/usr/bin/env sh
set -e

echo "Running migrations..."
alembic upgrade head

if [ "${SEED_ON_STARTUP:-true}" = "true" ]; then
  echo "Seeding database..."
  python -c "from app.db.init_db import seed_data; seed_data()"
fi

echo "Starting server..."
exec uvicorn app.main:app --host 0.0.0.0 --port 8000
