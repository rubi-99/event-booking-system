FROM python:3.12-slim

# Set environment variables
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    APP_ENV=production \
    APP_PORT=8000

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    curl \
    && rm -rf /var/lib/apt-get/lists/*

# Copy python configuration and install dependencies
COPY pyproject.toml ./
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir \
    fastapi \
    uvicorn[standard] \
    sqlalchemy \
    asyncpg \
    pydantic \
    "pydantic[email]" \
    email-validator \
    python-multipart \
    pydantic-settings \
    pyjwt \
    cryptography \
    httpx \
    supabase \
    slowapi \
    limits \
    redis

RUN pip install --no-cache-dir email-validator "pydantic[email]" python-multipart

# Copy application source code
COPY app /app/app

# Expose port
EXPOSE 8000

# Run Uvicorn server
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
