import pytest

@pytest.mark.asyncio
async def test_create_table(client):
    response = await client.post(
        "/tables/",
        json={"name": "VIP", "capacity": 4, "location": "Terrace"}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "VIP"
    assert data["capacity"] == 4

@pytest.mark.asyncio
async def test_get_tables(client):
    # Сначала создаем тестовый столик
    await client.post(
        "/tables/",
        json={"name": "Test", "capacity": 2, "location": "Window"}
    )
    
    response = await client.get("/tables/")
    assert response.status_code == 200
    data = response.json()
    assert len(data) > 0
    assert any(t["name"] == "Test" for t in data)