#!/bin/bash

API_URL="http://localhost:8000"

echo "=== Удаляем столики ==="

# Удаляем столики с ID от 1 до 6
for id in {1..6}; do
  echo "Удаляем столик с ID: $id"
  response=$(curl -s -o /dev/null -w "%{http_code}" -X DELETE "$API_URL/tables/$id")
  
  if [ "$response" -eq 204 ]; then
    echo "Успешно удалён"
  else
    echo "Не удалось удалить (HTTP $response)"
  fi
  sleep 0.5
done

echo ""
echo "=== Удаляем брони ==="

# Удаляем брони с ID от 1 до 4
for id in {1..4}; do
  echo "Удаляем бронь с ID: $id"
  response=$(curl -s -o /dev/null -w "%{http_code}" -X DELETE "$API_URL/reservations/$id")
  
  if [ "$response" -eq 204 ]; then
    echo "Успешно удалена"
  else
    echo "Не удалось удалить (HTTP $response)"
  fi
  sleep 0.5
done

echo ""
echo "=== Удаление завершено ==="