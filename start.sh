#!/bin/sh

# Exit immediately if a command exits with a non-zero status.
set -e

# Print all environment variables for debugging
echo "--- Printing environment variables ---"
printenv
echo "------------------------------------"

# Wait for the database to be ready
echo "Waiting for database..."
counter=0
while [ -z "$DATABASE_URL" ] && [ $counter -lt 30 ]; do
  sleep 2
  counter=$((counter+2))
done

if [ -z "$DATABASE_URL" ]; then
  echo "Error: DATABASE_URL is not set after 30 seconds."
  exit 1
fi

echo "Database is ready. Running migrations..."

# Run database migrations
/app/.venv/bin/alembic upgrade head

echo "Migrations complete. Starting application server..."

# Start the application server
/app/.venv/bin/uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8000}
