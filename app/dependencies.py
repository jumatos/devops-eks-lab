import logging
import os
from collections.abc import Iterator

import boto3
from botocore.config import Config
from botocore.exceptions import BotoCoreError, ClientError
from fastapi import HTTPException, status

from app.repositories import DynamoDBTaskRepository


logger = logging.getLogger(__name__)


def get_repository() -> Iterator[DynamoDBTaskRepository]:
    table_name = os.getenv("DYNAMODB_TABLE_NAME", "").strip()

    if not table_name:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Task storage is not configured",
        )

    dynamodb = None

    try:
        session = boto3.Session()
        dynamodb = session.resource(
            "dynamodb",
            region_name=os.getenv("AWS_REGION", "us-east-1"),
            config=Config(
                connect_timeout=2,
                read_timeout=2,
                retries={
                    "mode": "standard",
                    "total_max_attempts": 1,
                },
            ),
        )

        yield DynamoDBTaskRepository(dynamodb.Table(table_name))

    except (BotoCoreError, ClientError) as error:
        logger.warning(
            "Task storage request failed: %s",
            type(error).__name__,
        )
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Task storage is unavailable",
        ) from error

    finally:
        if dynamodb is not None:
            dynamodb.meta.client.close()