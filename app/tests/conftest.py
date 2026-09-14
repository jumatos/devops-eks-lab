import boto3
import pytest
from fastapi.testclient import TestClient
from moto import mock_aws

from app.dependencies import get_repository
from app.main import app
from app.repositories import DynamoDBTaskRepository


@pytest.fixture
def repository():
    with mock_aws():
        session = boto3.Session(
            region_name="us-east-1",
            aws_access_key_id="testing",
            aws_secret_access_key="testing",
            aws_session_token="testing",
        )

        dynamodb = session.resource("dynamodb")

        table = dynamodb.create_table(
            TableName="tasks-test",
            KeySchema=[
                {"AttributeName": "id", "KeyType": "HASH"},
            ],
            AttributeDefinitions=[
                {"AttributeName": "id", "AttributeType": "S"},
            ],
            BillingMode="PAY_PER_REQUEST",
        )

        try:
            yield DynamoDBTaskRepository(table)
        finally:
            dynamodb.meta.client.close()


@pytest.fixture
def client(repository):
    def override_repository():
        return repository

    previous_overrides = app.dependency_overrides.copy()
    app.dependency_overrides[get_repository] = override_repository

    try:
        with TestClient(app) as test_client:
            yield test_client
    finally:
        app.dependency_overrides.clear()
        app.dependency_overrides.update(previous_overrides)