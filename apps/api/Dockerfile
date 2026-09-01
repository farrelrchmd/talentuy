# Backend TalentPulse — FastAPI + SQLAlchemy.
FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1

WORKDIR /app

# Dependency build untuk psycopg dan reportlab.
RUN apt-get update \
    && apt-get install -y --no-install-recommends build-essential libpq-dev curl \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Aplikasi berjalan sebagai pengguna non-root.
RUN useradd --create-home --uid 1001 talentpulse \
    && chown -R talentpulse:talentpulse /app
USER talentpulse

EXPOSE 8000

HEALTHCHECK --interval=20s --timeout=5s --start-period=25s --retries=5 \
    CMD curl -fsS http://localhost:8000/health || exit 1

# Migration dijalankan sebelum server menerima request.
CMD ["sh", "-c", "alembic upgrade head && uvicorn app.main:app --host 0.0.0.0 --port 8000"]
