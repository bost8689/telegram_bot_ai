#!/bin/sh
# set -e

# Применяем миграции
# echo "⏳ Applying database migrations..."
# alembic upgrade head

# Запускаем приложение
# echo "🚀 Starting FastAPI application..."
# exec uvicorn app.main:app --host 0.0.0.0 --port 8123
# Запускаем ТО, что передано в command (из docker-compose)
echo "🚀 Executing: $@"
exec "$@"