# ============================================================
# SmartDocChecker Backend — Multi-stage Docker Build
# ============================================================
# Build context: backend/
# Run: docker build -t smartdocchecker-backend ./backend
# ============================================================

# ── Stage 1: Builder ─────────────────────────────────────────
FROM python:3.12-slim AS builder

WORKDIR /build

# System deps for building native extensions (psycopg2, scipy, etc.)
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Copy only requirements first (Docker layer caching)
COPY requirements.txt .

# Install all Python deps into a virtual-env so we can copy it cleanly
RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Download spaCy language model
RUN python -m spacy download en_core_web_sm


# ── Stage 2: Runtime ─────────────────────────────────────────
FROM python:3.12-slim

LABEL maintainer="SmartDocChecker"
LABEL description="SmartDocChecker FastAPI Backend"

WORKDIR /app

# Runtime system deps only (no build tools)
RUN apt-get update && apt-get install -y --no-install-recommends \
    libpq5 \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy the virtual-env from builder
COPY --from=builder /opt/venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# Copy backend source code
COPY . .

# Create directory for ML model cache
RUN mkdir -p /app/.model_cache

# ── Environment defaults (override via docker run -e or .env) ──
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    MODEL_CACHE_DIR=/app/.model_cache \
    PORT=8000

# Expose the API port
EXPOSE ${PORT}

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=120s --retries=3 \
    CMD curl -f http://localhost:${PORT}/api/auth/me || exit 1

# Start uvicorn
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "1"]
