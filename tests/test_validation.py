import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_validation_error_age_too_young():
    response = client.post("/users/", json={
        "username": "young",
        "age": 17,  # должно быть > 18
        "email": "young@example.com",
        "password": "password123",
        "phone": "123"
    })
    assert response.status_code == 422
    data = response.json()
    # Проверяем, что ошибка связана с возрастом
    error_str = str(data)
    assert "age" in error_str.lower() or "17" in error_str

def test_validation_error_invalid_email():
    response = client.post("/users/", json={
        "username": "bad_email",
        "age": 25,
        "email": "not-an-email",
        "password": "password123",
        "phone": "123"
    })
    assert response.status_code == 422
    data = response.json()
    error_str = str(data)
    assert "email" in error_str.lower() or "invalid" in error_str.lower()

def test_validation_error_short_password():
    response = client.post("/users/", json={
        "username": "short_pwd",
        "age": 25,
        "email": "valid@example.com",
        "password": "short",  # меньше 8 символов
        "phone": "123"
    })
    assert response.status_code == 422

def test_custom_exception_a():
    response = client.get("/test-exception-a?trigger=true")
    assert response.status_code == 400
    assert response.json()["error_code"] == "CUSTOM_A"

def test_custom_exception_b():
    response = client.get("/test-exception-b/100")  # не 42
    assert response.status_code == 404
    assert response.json()["error_code"] == "CUSTOM_B"