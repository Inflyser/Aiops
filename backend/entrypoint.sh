#!/bin/bash
set -e

# Wait for PostgreSQL to be ready
echo "Waiting for PostgreSQL to be ready..."
until pg_isready -h $POSTGRES_SERVER -p 5432 -U $POSTGRES_USER; do
  echo "PostgreSQL is unavailable - sleeping"
  sleep 2
done
echo "PostgreSQL is ready!"

echo "Running migrations..."
python -c "
import os
from alembic.config import Config
from alembic import command

alembic_cfg = Config('alembic.ini')
db_url = f'postgresql://{os.getenv(\"POSTGRES_USER\")}:{os.getenv(\"POSTGRES_PASSWORD\")}@{os.getenv(\"POSTGRES_SERVER\")}:5432/{os.getenv(\"POSTGRES_DB\")}'
alembic_cfg.set_main_option('sqlalchemy.url', db_url)
command.upgrade(alembic_cfg, 'head')
"
echo "Migrations completed!"

echo "Starting application..."
exec uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
