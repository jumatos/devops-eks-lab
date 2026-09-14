from typing import Literal
from uuid import UUID

from botocore.exceptions import ClientError

from app.models import TaskResponse


class TaskNotFoundError(Exception):
    pass


class TaskAlreadyExistsError(Exception):
    pass


class DynamoDBTaskRepository:
    def __init__(self, table):
        self.table = table

    def check_readiness(self) -> None:
        self.table.get_item(
            Key={"id": "__readiness__"},
            ConsistentRead=False,
        )

    def create(self, task: TaskResponse) -> TaskResponse:
        try:
            self.table.put_item(
                Item=task.model_dump(mode="json"),
                ConditionExpression="attribute_not_exists(id)",
            )
        except ClientError as error:
            if error.response["Error"]["Code"] == "ConditionalCheckFailedException":
                raise TaskAlreadyExistsError(str(task.id)) from error
            raise

        return task

    def get(self, task_id: UUID) -> TaskResponse:
        response = self.table.get_item(
            Key={"id": str(task_id)},
            ConsistentRead=True,
        )

        item = response.get("Item")
        if item is None:
            raise TaskNotFoundError(str(task_id))

        return TaskResponse.model_validate(item)

    def list_all(self) -> list[TaskResponse]:
        items = []
        options = {"ConsistentRead": True}

        while True:
            response = self.table.scan(**options)
            items.extend(response.get("Items", []))

            last_key = response.get("LastEvaluatedKey")
            if not last_key:
                break

            options["ExclusiveStartKey"] = last_key

        return [TaskResponse.model_validate(item) for item in items]

    def update_status(
        self,
        task_id: UUID,
        new_status: Literal["pending", "completed"],
    ) -> TaskResponse:
        try:
            response = self.table.update_item(
                Key={"id": str(task_id)},
                UpdateExpression="SET #task_status = :task_status",
                ExpressionAttributeNames={
                    "#task_status": "status",
                },
                ExpressionAttributeValues={
                    ":task_status": new_status,
                },
                ConditionExpression="attribute_exists(id)",
                ReturnValues="ALL_NEW",
            )
        except ClientError as error:
            if error.response["Error"]["Code"] == "ConditionalCheckFailedException":
                raise TaskNotFoundError(str(task_id)) from error
            raise

        return TaskResponse.model_validate(response["Attributes"])

    def delete(self, task_id: UUID) -> None:
        try:
            self.table.delete_item(
                Key={"id": str(task_id)},
                ConditionExpression="attribute_exists(id)",
            )
        except ClientError as error:
            if error.response["Error"]["Code"] == "ConditionalCheckFailedException":
                raise TaskNotFoundError(str(task_id)) from error
            raise
