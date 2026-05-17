import pytest
from httpx import AsyncClient, ASGITransport
from app.main import app
from faker import Faker

fake = Faker()

# Фикстура для очистки in-memory хранилища
@pytest.fixture(autouse=True)
def clean_db():
    from app.routers import users
    users.db.clear()
    yield
    users.db.clear()

@pytest.mark.asyncio
async def test_create_user():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        response = await ac.post("/users/", json={
            "username": fake.user_name(),
            "age": 25,
            "email": fake.email(),
            "password": "secret123",
            "phone": fake.phone_number()
        })
        assert response.status_code == 201
        data = response.json()
        assert "id" in data
        assert data["username"] is not None
        assert data["age"] == 25

@pytest.mark.asyncio
async def test_get_existing_user():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        # Создаем пользователя
        create_resp = await ac.post("/users/", json={
            "username": "john_doe",
            "age": 30,
            "email": "john@example.com",
            "password": "securepwd",
            "phone": "123456"
        })
        user_id = create_resp.json()["id"]
        
        # Получаем его
        response = await ac.get(f"/users/{user_id}")
        assert response.status_code == 200
        assert response.json()["username"] == "john_doe"

@pytest.mark.asyncio
async def test_get_nonexistent_user():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        response = await ac.get("/users/99999")
        assert response.status_code == 404
        assert "User not found" in response.json()["detail"]

@pytest.mark.asyncio
async def test_delete_existing_user():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        create_resp = await ac.post("/users/", json={
            "username": "to_delete",
            "age": 22,
            "email": "delete@example.com",
            "password": "delete123",
            "phone": "000"
        })
        user_id = create_resp.json()["id"]
        
        delete_resp = await ac.delete(f"/users/{user_id}")
        assert delete_resp.status_code == 204

@pytest.mark.asyncio
async def test_delete_nonexistent_user():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        response = await ac.delete("/users/99999")
        assert response.status_code == 404

@pytest.mark.asyncio
async def test_delete_twice():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        create_resp = await ac.post("/users/", json={
            "username": "twice",
            "age": 28,
            "email": "twice@example.com",
            "password": "twice123",
            "phone": "111"
        })
        user_id = create_resp.json()["id"]
        
        # Первое удаление
        resp1 = await ac.delete(f"/users/{user_id}")
        assert resp1.status_code == 204
        
        # Второе удаление
        resp2 = await ac.delete(f"/users/{user_id}")
        assert resp2.status_code == 404