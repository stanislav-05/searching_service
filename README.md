# Поисковый сервис (searching_service)

Простой поисковый сервис по текстам документов.

## Стек технологий

* Python 3.12
* FastAPI
* Pydantic
* SQLAlchemy 2
* Alembic
* PostgreSQL
* Elasticsearch
* Pytest / pytest-asyncio
* uv
* Docker

## Запуск проекта

Клонируйте репозиторий:

```bash
git clone <url-репозитория>
cd searching_service
```

Создайте .env как в примере .env.example

Запуск через Docker:
```bash
docker compose up --build -d
```

Проверка:
```bash
docker compose ps
```

Миграции применяются автоматически.
Загрузка данных из data/posts.csv:
```bash
docker compose exec api uv run python -m scripts.load_data
```

## Документация API

После запуска сервиса доступны:

Swagger UI: http://localhost:8000/docs
OpenAPI: http://localhost:8000/openapi.json

Файл OpenAPI-документации docs.json также находится в репозитории.

Поиск:

GET /api/v1/documents/search?q=<query>

Удаление:

DELETE /api/v1/documents/{id}


## Тесты

Для запуска тестов создайте тестовую БД:

```bash
docker compose exec postgres \
  psql -U postgres -d postgres \
  -c "CREATE DATABASE searching_service_test;"
```

После этого:
```bash
docker compose exec api uv run pytest -v
```

## Остановка:

Остановка контейнеров:

```bash
docker compose down
```

Остановка с полным удалением данных:

```bash
docker compose down -v
```
