from typing import Literal
from uuid import UUID, uuid4

from fastapi import FastAPI, status
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


tasks: dict[UUID, TaskResponse] = {}


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