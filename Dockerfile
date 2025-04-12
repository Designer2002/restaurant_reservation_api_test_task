# Сборка бэкенда
FROM python:3.11-slim as backend

WORKDIR /app
ENV PYTHONPATH=/app

# Установка зависимостей одним слоем
RUN apt-get update && \
    apt-get install -y postgresql-client curl && \
    pip install --no-cache-dir poetry && \
    rm -rf /var/lib/apt/lists/*

# Копируем зависимости и устанавливаем
COPY pyproject.toml poetry.lock* ./
RUN poetry config virtualenvs.create false && \
    poetry install --no-root --no-interaction --no-ansi

# Копируем остальные файлы
COPY . .

# Делаем скрипт исполняемым
RUN chmod +x /app/init_db.sh

# Сборка фронтенда
FROM nginx:alpine as frontend

# Копируем фронтенд файлы
COPY --from=backend /app/frontend /usr/share/nginx/html
COPY --from=backend /app/frontend/nginx.conf /etc/nginx/conf.d/default.conf

EXPOSE 80

# Финальный образ (можно использовать либо backend, либо frontend)
FROM backend as final

# Команда для запуска бэкенда
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]