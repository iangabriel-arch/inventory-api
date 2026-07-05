"""
tests/test_api.py

Unit tests for the Flask REST API's CRUD endpoints.
Uses Flask's built-in test client, so no live server is needed.
"""

import pytest
import sys
import os

# Allow importing app.py and data_store.py from the parent directory
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import app as flask_app
import data_store


@pytest.fixture
def client():
    """Provides a Flask test client, resetting the data store before each test."""
    data_store.reset()
    flask_app.app.config["TESTING"] = True
    with flask_app.app.test_client() as client:
        yield client


def test_get_empty_inventory(client):
    response = client.get("/inventory")
    assert response.status_code == 200
    assert response.get_json() == []


def test_create_item(client):
    response = client.post("/inventory", json={
        "name": "Almond Milk",
        "brand": "Silk",
        "price": 3.99,
        "stock": 20
    })
    assert response.status_code == 201

    data = response.get_json()
    assert data["id"] == 1
    assert data["name"] == "Almond Milk"
    assert data["price"] == 3.99


def test_create_item_missing_name(client):
    response = client.post("/inventory", json={"brand": "Silk"})
    assert response.status_code == 400
    assert "error" in response.get_json()


def test_get_single_item(client):
    client.post("/inventory", json={"name": "Oat Milk"})
    response = client.get("/inventory/1")
    assert response.status_code == 200
    assert response.get_json()["name"] == "Oat Milk"


def test_get_nonexistent_item(client):
    response = client.get("/inventory/999")
    assert response.status_code == 404


def test_update_item(client):
    client.post("/inventory", json={"name": "Oat Milk", "stock": 10})
    response = client.patch("/inventory/1", json={"stock": 50})
    assert response.status_code == 200
    assert response.get_json()["stock"] == 50
    # Confirm untouched fields remain
    assert response.get_json()["name"] == "Oat Milk"


def test_update_nonexistent_item(client):
    response = client.patch("/inventory/999", json={"stock": 5})
    assert response.status_code == 404


def test_update_item_no_body(client):
    client.post("/inventory", json={"name": "Oat Milk"})
    response = client.patch("/inventory/1", json=None)
    assert response.status_code == 400


def test_delete_item(client):
    client.post("/inventory", json={"name": "Soy Milk"})
    response = client.delete("/inventory/1")
    assert response.status_code == 200

    # Confirm it's actually gone
    follow_up = client.get("/inventory/1")
    assert follow_up.status_code == 404


def test_delete_nonexistent_item(client):
    response = client.delete("/inventory/999")
    assert response.status_code == 404


def test_full_crud_cycle(client):
    """Integration-style test exercising create -> read -> update -> delete."""
    create = client.post("/inventory", json={"name": "Cereal", "price": 4.5, "stock": 10})
    item_id = create.get_json()["id"]

    read = client.get(f"/inventory/{item_id}")
    assert read.status_code == 200

    update = client.patch(f"/inventory/{item_id}", json={"price": 5.0})
    assert update.get_json()["price"] == 5.0

    delete = client.delete(f"/inventory/{item_id}")
    assert delete.status_code == 200

    final_check = client.get(f"/inventory/{item_id}")
    assert final_check.status_code == 404
