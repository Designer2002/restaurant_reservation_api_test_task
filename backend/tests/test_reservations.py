import pytest
from datetime import datetime, timedelta

@pytest.mark.asyncio
async def test_create_reservation(client):
    # Сначала создаем столик
    table_resp = await client.post(
        "/tables/",
        json={"name": "Reservation Test", "capacity": 4, "location": "Main Hall"}
    )
    table_id = table_resp.json()["id"]
    
    # Бронируем столик
    reservation_time = (datetime.now() + timedelta(days=1)).isoformat()
    response = await client.post(
        "/reservations/",
        json={
            "table_id": table_id,
            "customer_name": "John Doe",
            "reservation_time": reservation_time,
            "guests_count": 3
        }
    )
    assert response.status_code == 200
    data = response.json()
    assert data["customer_name"] == "John Doe"

@pytest.mark.asyncio
async def test_get_reservations(client):
    response = await client.get("/reservations/")
    assert response.status_code == 200
    assert isinstance(response.json(), list)