#!/bin/bash

API_URL="http://localhost:8000"
FAILED_RESERVATIONS=0

echo "=== Создаем столики ==="

# Массив данных для столиков
tables=(
  '{"name": "VIP У окна", "seats": 4, "location": "У панорамного окна"}'
  '{"name": "Барная стойка", "seats": 2, "location": "Правая сторона бара"}'
  '{"name": "Уютный уголок", "seats": 3, "location": "Тихий угол ресторана"}'
  '{"name": "Центральный", "seats": 6, "location": "Центр зала"}'
  '{"name": "Для компании", "seats": 8, "location": "Зал для мероприятий"}'
  '{"name": "Романтический", "seats": 2, "location": "Возле камина"}'
)

for table in "${tables[@]}"; do
  echo "Создаем столик: $table"
  curl -s -X POST "$API_URL/tables/" \
    -H "Content-Type: application/json" \
    -d "$table"
  echo ""
  sleep 0.5
done

echo ""
echo "=== Создаем брони ==="

# Текущее время для расчета дат бронирований
NOW=$(date +%s)

# Массив данных для броней
reservations=(
  '{"customer_name": "Александр Петров", "table_id": 1, "reservation_time": "'$(date -u -d "@$((NOW + 86400))" +"%Y-%m-%dT19:00:00Z")'", "duration_minutes": 90}'
  '{"customer_name": "Екатерина Смирнова", "table_id": 2, "reservation_time": "'$(date -u -d "@$((NOW + 90000))" +"%Y-%m-%dT21:30:00Z")'", "duration_minutes": 60}'
  '{"customer_name": "Дмитрий Иванов", "table_id": 3, "reservation_time": "'$(date -u -d "@$((NOW + 172800))" +"%Y-%m-%dT20:00:00Z")'", "duration_minutes": 120}'
  '{"customer_name": "Ольга Васильева", "table_id": 4, "reservation_time": "'$(date -u -d "@$((NOW + 3600))" +"%Y-%m-%dT13:00:00Z")'", "duration_minutes": 150}'
  '{"customer_name": "Тестировщик (займет занятый столик)", "table_id": 4, "reservation_time": "'$(date -u -d "@$((NOW + 1))" +"%Y-%m-%dT13:00:00Z")'", "duration_minutes": 50}'
  '{"customer_name": "Тестировщик (займёт столик которого нет)", "table_id": 14, "reservation_time": "'$(date -u -d "@$((NOW + 3600))" +"%Y-%m-%dT13:00:00Z")'", "duration_minutes": 150}'
  '{"customer_name": "Тестировщик (опоздун)", "table_id": 6, "reservation_time": "'$(date -u -d "@$((NOW - 3600))" +"%Y-%m-%dT13:00:00Z")'", "duration_minutes": 150}'
)

for reservation in "${reservations[@]}"; do
  echo "Создаем бронь: $reservation"
  response=$(curl -s -w "\n%{http_code}" -X POST "$API_URL/reservations/" \
    -H "Content-Type: application/json" \
    -d "$reservation")
  
  http_code=$(echo "$response" | tail -n1)
  body=$(echo "$response" | sed '$d')
  
  if [ "$http_code" -ge 200 ] && [ "$http_code" -lt 300 ]; then
    echo "Успешно (HTTP $http_code)"
  else
    echo "ОШИБКА (HTTP $http_code): $body"
    ((FAILED_RESERVATIONS++))
  fi
  
  echo ""
  sleep 0.5
done

echo ""
echo "=== Инициализация завершена ==="
echo "Создано:"
echo "- 6 столиков"
echo "- ${#reservations[@]} попыток бронирования, из них $FAILED_RESERVATIONS неудачных"