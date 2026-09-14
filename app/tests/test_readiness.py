from unittest.mock import patch

from botocore.exceptions import EndpointConnectionError, NoCredentialsError
from fastapi.testclient import TestClient

from app.main import app


def test_ready_returns_200_with_accessible_storage(client, repository):
    response = client.get("/ready")

    assert response.status_code == 200
    assert response.json() == {"status": "ready"}
    assert repository.list_all() == []


def test_ready_returns_503_when_table_is_missing(client, repository):
    repository.table.delete()

    response = client.get("/ready")

    assert response.status_code == 503
    assert response.json() == {
        "detail": "Task storage is unavailable",
    }

    health = client.get("/health")
    assert health.status_code == 200
    assert health.json() == {"status": "ok"}


def test_ready_returns_503_on_connection_failure(client, repository):
    with patch.object(
        repository.table,
        "get_item",
        side_effect=EndpointConnectionError(
            endpoint_url="https://dynamodb.invalid",
        ),
    ):
        response = client.get("/ready")

    assert response.status_code == 503
    assert response.json() == {
        "detail": "Task storage is unavailable",
    }


def test_ready_returns_503_without_table_configuration(monkeypatch):
    monkeypatch.delenv("DYNAMODB_TABLE_NAME", raising=False)

    # Sin la fixture client: ejercitamos la dependencia original.
    with TestClient(app) as test_client:
        response = test_client.get("/ready")
        health = test_client.get("/health")

    assert response.status_code == 503
    assert response.json() == {
        "detail": "Task storage is not configured",
    }
    assert health.status_code == 200


def test_ready_returns_503_when_client_initialization_fails(monkeypatch):
    monkeypatch.setenv("DYNAMODB_TABLE_NAME", "tasks-test")

    with patch(
        "app.dependencies.boto3.Session",
        side_effect=NoCredentialsError(),
    ):
        with TestClient(app) as test_client:
            response = test_client.get("/ready")

    assert response.status_code == 503
    assert response.json() == {
        "detail": "Task storage is unavailable",
    }