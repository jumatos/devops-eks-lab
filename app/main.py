from typing import Annotated
from uuid import UUID, uuid4

from fastapi import Depends, FastAPI, Request, Response, status
from fastapi.responses import JSONResponse

from app.dependencies import get_repository
from app.models import TaskCreate, TaskResponse, TaskUpdate
from app.repositories import (
    DynamoDBTaskRepository,
    TaskAlreadyExistsError,
    TaskNotFoundError,
)


app = FastAPI(
    title="Task API",
    description="Task management API for the DevOps EKS lab.",
    version="0.3.0",
)

RepositoryDependency = Annotated[
    DynamoDBTaskRepository,
    Depends(get_repository),
]


@app.exception_handler(TaskNotFoundError)
async def task_not_found_handler(
    request: Request,
    exc: TaskNotFoundError,
) -> JSONResponse:
    return JSONResponse(
        status_code=status.HTTP_404_NOT_FOUND,
        content={"detail": "Task not found"},
    )


@app.exception_handler(TaskAlreadyExistsError)
async def task_already_exists_handler(
    request: Request,
    exc: TaskAlreadyExistsError,
) -> JSONResponse:
    return JSONResponse(
        status_code=status.HTTP_409_CONFLICT,
        content={"detail": "Task already exists"},
    )


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.post(
    "/tasks",
    response_model=TaskResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_task(
    payload: TaskCreate,
    repository: RepositoryDependency,
) -> TaskResponse:
    task = TaskResponse(
        id=uuid4(),
        title=payload.title,
        status="pending",
    )

    return repository.create(task)


@app.get("/tasks", response_model=list[TaskResponse])
def list_tasks(
    repository: RepositoryDependency,
) -> list[TaskResponse]:
    return repository.list_all()


@app.get("/tasks/{task_id}", response_model=TaskResponse)
def get_task(
    task_id: UUID,
    repository: RepositoryDependency,
) -> TaskResponse:
    return repository.get(task_id)


@app.patch("/tasks/{task_id}", response_model=TaskResponse)
def update_task(
    task_id: UUID,
    payload: TaskUpdate,
    repository: RepositoryDependency,
) -> TaskResponse:
    return repository.update_status(task_id, payload.status)


@app.delete(
    "/tasks/{task_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    response_class=Response,
)
def delete_task(
    task_id: UUID,
    repository: RepositoryDependency,
) -> Response:
    repository.delete(task_id)

    return Response(status_code=status.HTTP_204_NO_CONTENT)