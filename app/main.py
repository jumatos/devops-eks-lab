from typing import Literal
from uuid import UUID, uuid4

from fastapi import FastAPI, HTTPException, Response, status
from pydantic import BaseModel, ConfigDict, Field


app = FastAPI(
    title="Task API",
    description="Task management API for the DevOps EKS lab.",
    version="0.2.0",
)


class TaskCreate(BaseModel):
    model_config = ConfigDict(
        str_strip_whitespace=True,
        extra="forbid",
    )

    title: str = Field(min_length=1, max_length=120)


class TaskResponse(BaseModel):
    id: UUID
    title: str
    status: Literal["pending", "completed"]


class TaskUpdate(BaseModel):
    model_config = ConfigDict(extra="forbid")

    status: Literal["pending", "completed"]


# Temporary storage: data is lost when the process restarts.
tasks: dict[UUID, TaskResponse] = {}


def find_task(task_id: UUID) -> TaskResponse:
    task = tasks.get(task_id)

    if task is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found",
        )

    return task


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.post(
    "/tasks",
    response_model=TaskResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_task(payload: TaskCreate) -> TaskResponse:
    task = TaskResponse(
        id=uuid4(),
        title=payload.title,
        status="pending",
    )

    tasks[task.id] = task
    return task


@app.get("/tasks", response_model=list[TaskResponse])
def list_tasks() -> list[TaskResponse]:
    return list(tasks.values())


@app.get("/tasks/{task_id}", response_model=TaskResponse)
def get_task(task_id: UUID) -> TaskResponse:
    return find_task(task_id)


@app.patch("/tasks/{task_id}", response_model=TaskResponse)
def update_task(
    task_id: UUID,
    payload: TaskUpdate,
) -> TaskResponse:
    task = find_task(task_id)

    updated_task = task.model_copy(
        update={"status": payload.status},
    )

    tasks[task_id] = updated_task
    return updated_task


@app.delete(
    "/tasks/{task_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    response_class=Response,
)
def delete_task(task_id: UUID) -> Response:
    find_task(task_id)
    del tasks[task_id]

    return Response(status_code=status.HTTP_204_NO_CONTENT)
