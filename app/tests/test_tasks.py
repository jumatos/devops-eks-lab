from uuid import UUID, uuid4

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


def test_get_task_by_id(client):
    created = client.post(
        "/tasks",
        json={"title": "Test task lookup"},
    ).json()

    response = client.get(f"/tasks/{created['id']}")

    assert response.status_code == 200
    assert response.json() == created


def test_update_task_status(client):
    created = client.post(
        "/tasks",
        json={"title": "Test task update"},
    ).json()

    response = client.patch(
        f"/tasks/{created['id']}",
        json={"status": "completed"},
    )

    assert response.status_code == 200
    assert response.json() == {
        **created,
        "status": "completed",
    }

    fetched = client.get(f"/tasks/{created['id']}")

    assert fetched.status_code == 200
    assert fetched.json()["status"] == "completed"


def test_delete_task(client):
    created = client.post(
        "/tasks",
        json={"title": "Test task deletion"},
    ).json()

    response = client.delete(f"/tasks/{created['id']}")

    assert response.status_code == 204
    assert response.content == b""
    assert client.get(f"/tasks/{created['id']}").status_code == 404
    assert client.get("/tasks").json() == []


@pytest.mark.parametrize("method", ["get", "patch", "delete"])
def test_missing_task_returns_404(client, method):
    options = (
        {"json": {"status": "completed"}}
        if method == "patch"
        else {}
    )

    response = client.request(
        method,
        f"/tasks/{uuid4()}",
        **options,
    )

    assert response.status_code == 404
    assert response.json() == {"detail": "Task not found"}


@pytest.mark.parametrize(
    "payload",
    [
        {},
        {"status": "invalid"},
        {"status": "completed", "title": "Unexpected change"},
    ],
)
def test_invalid_update_does_not_change_task(client, payload):
    created = client.post(
        "/tasks",
        json={"title": "Keep this task unchanged"},
    ).json()

    response = client.patch(
        f"/tasks/{created['id']}",
        json=payload,
    )

    assert response.status_code == 422
    assert client.get(f"/tasks/{created['id']}").json() == created


@pytest.mark.parametrize("method", ["get", "patch", "delete"])
def test_invalid_task_id_returns_422(client, method):
    options = (
        {"json": {"status": "completed"}}
        if method == "patch"
        else {}
    )

    response = client.request(
        method,
        "/tasks/not-a-uuid",
        **options,
    )

    assert response.status_code == 422
