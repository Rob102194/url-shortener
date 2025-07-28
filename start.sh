#!/bin/sh

# Exit immediately if a command exits with a non-zero status.
set -e

# Run database migrations
/app/.venv/bin/alembic upgrade head

# Start the application server
/app/.venv/bin/uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8000}
