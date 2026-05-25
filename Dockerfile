FROM python:3.11-slim

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc libpq-dev curl \
    && rm -rf /var/lib/apt/lists/*

COPY backend/requirements.txt ./backend/
RUN pip install --no-cache-dir -r ./backend/requirements.txt

COPY backend/ ./backend/
COPY Craftsman2.html api-config.js ./
COPY Images/ ./Images/
COPY Cities/ ./Cities/
COPY Patterns/ ./Patterns/
COPY Naqshlar/ ./Naqshlar/
COPY Schools/ ./Schools/
COPY Videos/ ./Videos/

WORKDIR /app/backend

HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD curl -f http://localhost:${PORT:-8000}/health || exit 1

CMD uvicorn main:app --host 0.0.0.0 --port ${PORT:-8000}
