FROM python:3.12-slim

WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

COPY --from=ghcr.io/astral-sh/uv:0.11.32 /uv /uvx /bin/

COPY pyproject.toml uv.lock ./

RUN uv sync --frozen --no-install-project

COPY app ./app
COPY alembic ./alembic
COPY alembic.ini ./
COPY data ./data
COPY scripts ./scripts
COPY tests ./tests

EXPOSE 8000

CMD ['uv', 'run', '--no-sync', 'uvicorn', 'app.main:app', '--host', '0.0.0.0', '--port', '8000']
