FROM python:3.11-slim

WORKDIR /app
ENV PYTHONPATH=/app



RUN pip install --no-cache-dir poetry


COPY pyproject.toml poetry.lock* ./


RUN poetry config virtualenvs.create false && \
    poetry install --no-root --no-interaction --no-ansi
    RUN apt-get update && apt-get install -y postgresql-client && apt-get install -y curl && rm -rf /var/lib/apt/lists/*

COPY init_db.sh /app/
RUN chmod +x /app/init_db.sh

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]