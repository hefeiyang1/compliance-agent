FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    git \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements files
COPY pyproject.toml ./

# Install Python dependencies
RUN pip install --no-cache-dir -e ".[dev]" && \
    pip install --no-cache-dir gunicorn

# Copy application code
COPY src/ ./src/
COPY config/ ./config/
COPY docs/ ./docs/

# Create directories for logs and data
RUN mkdir -p /app/logs /app/data

# Expose port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD curl -f http://localhost:8000/api/v1/health || exit 1

# Run the application
CMD ["uvicorn", "src.api.main:app", "--host", "0.0.0.0", "--port", "8000"]
