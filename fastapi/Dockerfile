# STAGE 1: сборка (хотя тут только Python, но структура готова к усложнению)
FROM python:3.12-slim AS base

# Устанавливаем зависимости
WORKDIR /app

# Создаём non-root пользователя
RUN addgroup --system --gid 1001 appuser && \
    adduser --system --uid 1001 --gid 1001 appuser

# Копируем зависимости
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# STAGE 2: production
FROM base AS production

WORKDIR /app

# Копируем только код
COPY . .
# Создаём папку для логов и даём права
# RUN mkdir -p /app/logs && chown -R appuser:appuser /app/logs
RUN chown -R appuser:appuser /app

# WORKDIR /app
# Переключаемся на non-root пользователя
USER appuser

RUN chmod +x /app/entrypoint.sh

EXPOSE 8123

# CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8123"]
# Запускаем обёртку
ENTRYPOINT ["/app/entrypoint.sh"]

# В requirements.txt добавить: gunicorn[uvicorn]
# CMD ["gunicorn", "-k", "uvicorn.workers.UvicornWorker", "app.main:app", "--bind", "0.0.0.0:8123"]