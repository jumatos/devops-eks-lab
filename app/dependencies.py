import os
from collections.abc import Iterator

import boto3
from fastapi import HTTPException, status

from app.repositories import DynamoDBTaskRepository


def get_repository() -> Iterator[DynamoDBTaskRepository]:
    table_name = os.getenv("DYNAMODB_TABLE_NAME", "").strip()

    if not table_name:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Task storage is not configured",
        )

    session = boto3.Session()
    dynamodb = session.resource(
        "dynamodb",
        region_name=os.getenv("AWS_REGION", "us-east-1"),
    )

    try:
        yield DynamoDBTaskRepository(dynamodb.Table(table_name))
    finally:
        dynamodb.meta.client.close()