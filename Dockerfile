FROM python:3.13-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Copy project definition
COPY pyproject.toml uv.lock ./

# Install uv
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

# Install dependencies
RUN uv sync --frozen

# Add virtualenv to PATH
ENV PATH="/app/.venv/bin:$PATH"

# Copy project code
COPY . .

EXPOSE 8000

# Run the application
# Note: For production, add 'gunicorn' to your dependencies and use:
# CMD ["gunicorn", "--bind", "0.0.0.0:8000", "core.wsgi:application"]
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]
