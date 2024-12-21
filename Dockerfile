FROM python:3.10-buster as builder

# Установка Poetry
RUN pip install poetry

# Установка переменных окружения
ENV POETRY_NO_INTERACTION=1 \
    POETRY_VIRTUALENVS_IN_PROJECT=1 \
    POETRY_VIRTUALENVS_CREATE=1 \
    POETRY_CACHE_DIR=/tmp/poetry_cache

# Копируем файлы проекта
WORKDIR /app
COPY pyproject.toml poetry.lock ./

# Установка зависимостей без корневого пакета и без dev-зависимостей
RUN poetry install --no-root --no-dev

# Второй этап сборки для уменьшения размера образа
FROM python:3.10-slim-buster

# Переменные окружения для виртуального окружения
ENV VIRTUAL_ENV=/app/.venv \
    PATH="/app/.venv/bin:$PATH"

# Копируем виртуальное окружение из билд-образа
COPY --from=builder /app/.venv /app/.venv

# Устанавливаем рабочую директорию
WORKDIR /app

# Установка клиента PostgreSQL
RUN apt update && apt install -y postgresql-client

# Настройки для Python
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Копируем оставшиеся файлы проекта
COPY . .