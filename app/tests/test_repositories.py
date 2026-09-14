from uuid import uuid4

import pytest

from app.models import TaskResponse
from app.repositories import (
    TaskAlreadyExistsError,
    TaskNotFoundError,
)


def test_repository_crud(repository):
    task = TaskResponse(
        id=uuid4(),
        title="Test DynamoDB storage",
        status="pending",
    )

    assert repository.list_all() == []
    assert repository.create(task) == task
    assert repository.get(task.id) == task
    assert repository.list_all() == [task]

    updated = repository.update_status(task.id, "completed")

    assert updated.status == "completed"
    assert updated.title == task.title
    assert repository.get(task.id) == updated

    repository.delete(task.id)

    assert repository.list_all() == []

    with pytest.raises(TaskNotFoundError):
        repository.get(task.id)


@pytest.mark.parametrize("operation", ["get", "update", "delete"])
def test_missing_task(repository, operation):
    task_id = uuid4()

    with pytest.raises(TaskNotFoundError):
        if operation == "get":
            repository.get(task_id)
        elif operation == "update":
            repository.update_status(task_id, "completed")
        else:
            repository.delete(task_id)

    assert repository.list_all() == []


def test_duplicate_id_does_not_overwrite_task(repository):
    original = TaskResponse(
        id=uuid4(),
        title="Original task",
        status="pending",
    )
    repository.create(original)

    duplicate = original.model_copy(
        update={"title": "Replacement"},
    )

    with pytest.raises(TaskAlreadyExistsError):
        repository.create(duplicate)

    assert repository.get(original.id) == original