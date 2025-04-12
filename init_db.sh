#!/bin/bash

until psql postgresql://postgres:postgres@db -c "select 1" >/dev/null 2>&1; do
  sleep 2
done

if ! psql postgresql://postgres:postgres@db/restaurant -c '\dt' | grep tables; then
  echo "Creating initial migration..."
  alembic revision --autogenerate -m "Initial tables"
  alembic upgrade head
fi

python app/db/drop_data_for_testing.py
python app/db/init_data_for_testing.py


exec "$@"