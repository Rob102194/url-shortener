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

# Set the working directory
WORKDIR /app

# Copy the virtual environment from the builder stage
COPY --from=builder /app/.venv ./.venv

# Copy the application code
COPY . .

# Activate the virtual environment and run the application
CMD ["/app/.venv/bin/uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
