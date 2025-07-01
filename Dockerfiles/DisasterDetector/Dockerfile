# ----------- Builder Stage -----------
FROM python:3.11-alpine AS builder

# Install build dependencies
RUN apk add --no-cache \
    gcc \
    musl-dev \
    libffi-dev \
    openssl-dev \
    python3-dev \
    build-base

WORKDIR /app

# Copy and install Python dependencies
COPY requirements.txt .
RUN pip install --upgrade pip && \
    pip install --prefix=/install -r requirements.txt

# ----------- Runtime Stage -----------
FROM python:3.11-alpine

# Install only runtime dependencies
RUN apk add --no-cache libffi openssl

WORKDIR /app

# Copy installed Python dependencies from builder
COPY --from=builder /install /usr/local

# Copy application code
COPY . .

# Metadata labels
LABEL maintainer="Platform Engineering Team"
LABEL org.opencontainers.image.title="DisasterDetector"
LABEL org.opencontainers.image.version="1.0.0"
LABEL org.opencontainers.image.description="Production image for DisasterDetector microservice"

# Expose default port
EXPOSE 8000

# Use non-root user for security (recommended)
RUN addgroup -S appuser && adduser -S appuser -G appuser && chown -R appuser:appuser /app
USER appuser

# Entrypoint and default command
ENTRYPOINT ["uvicorn", "main:app"]
CMD ["--host", "0.0.0.0", "--port", "8000"]

# ----------- End of Dockerfile -----------
