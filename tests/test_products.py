import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_create_product():
    response = client.post("/products/", json={
        "title": "Test Product",
        "price": 99.99,
        "count": 10
    })
    assert response.status_code == 200
    data = response.json()
    assert data["title"] == "Test Product"
    assert data["price"] == 99.99
    assert data["count"] == 10
    assert "id" in data

def test_get_products():
    response = client.get("/products/")
    assert response.status_code == 200
    assert isinstance(response.json(), list)

def test_get_single_product():
    # Сначала создаем продукт
    create_resp = client.post("/products/", json={"title": "Apple", "price": 50, "count": 5})
    product_id = create_resp.json()["id"]
    
    response = client.get(f"/products/{product_id}")
    assert response.status_code == 200
    assert response.json()["title"] == "Apple"

def test_update_description():
    create_resp = client.post("/products/", json={"title": "Book", "price": 30, "count": 2})
    product_id = create_resp.json()["id"]
    
    response = client.patch(f"/products/{product_id}/description", json={"description": "Interesting book"})
    assert response.status_code == 200
    assert response.json()["description"] == "Interesting book"