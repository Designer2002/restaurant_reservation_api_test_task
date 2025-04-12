#сборка бэкенда
FROM python:3.11-slim as backend

WORKDIR backend/app
ENV PYTHONPATH=backend/app

RUN pip install --no-cache-dir poetry


COPY pyproject.toml poetry.lock* ./


RUN poetry config virtualenvs.create false && \
    poetry install --no-root --no-interaction --no-ansi
    RUN apt-get update && apt-get install -y postgresql-client && apt-get install -y curl && rm -rf /var/lib/apt/lists/*

COPY init_db.sh /app/

# Стадия сборки фронтенда
FROM nginx:alpine


COPY ./frontend /usr/share/nginx/html


COPY ./frontend/nginx.conf /etc/nginx/conf.d/default.conf


EXPOSE 80

CMD ["nginx", "-g", "daemon off;"]

FROM backend as final

RUN chmod +x /app/init_db.sh

CMD ["uvicorn", "cd backend && app.main:app", "--host", "0.0.0.0", "--port", "8000"]