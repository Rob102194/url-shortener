# Stage 1: Build the application
FROM python:3.12-slim as builder

# Install poetry
RUN pip install poetry

# Set the working directory
WORKDIR /app

# Copy the dependency files
COPY poetry.lock pyproject.toml ./

# Configure poetry to create the virtualenv in the project's root
RUN poetry config virtualenvs.in-project true

# Install dependencies
RUN poetry install --without dev --no-root

# Copy the application code
COPY . .

# Stage 2: Create the final image
FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Create a non-root user
RUN addgroup --system app && adduser --system --group app

# Set the working directory
WORKDIR /app

# Copy the virtual environment from the builder stage
COPY --from=builder /app/.venv ./.venv

# Copy the application code from the builder stage
COPY --from=builder /app/app /app/app
COPY --from=builder /app/alembic /app/alembic
COPY --from=builder /app/alembic.ini /app/alembic.ini

# Set ownership of the app directory
RUN chown -R app:app /app

# Switch to the non-root user
USER app

# Activate the virtual environment, run migrations, and then run the application
CMD sleep 5 && /app/.venv/bin/alembic upgrade head && /app/.venv/bin/uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8000}
