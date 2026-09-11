from uuid import UUID

import pytest
from fastapi.testclient import TestClient

from app.main import app, tasks


@pytest.fixture
def client():
    tasks.clear()
    with TestClient(app) as test_client:
        yield test_client
    tasks.clear()


def test_list_tasks_initially_empty(client):
    response = client.get("/tasks")

    assert response.status_code == 200
    assert response.json() == []


def test_create_task_and_retrieve_it(client):
    response = client.post(
        "/tasks",
        json={"title": "  Build the CI pipeline  "},
    )

    assert response.status_code == 201

    task = response.json()
    UUID(task["id"])

    assert task["title"] == "Build the CI pipeline"
    assert task["status"] == "pending"

    listing = client.get("/tasks")

    assert listing.status_code == 200
    assert listing.json() == [task]


@pytest.mark.parametrize(
    "payload",
    [
        {},
        {"title": ""},
        {"title": "   "},
        {"title": "x" * 121},
        {"title": "Valid title", "unexpected": True},
    ],
)
def test_invalid_task_is_rejected(client, payload):
    response = client.post("/tasks", json=payload)

    assert response.status_code == 422
    assert client.get("/tasks").json() == []