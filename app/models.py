from typing import Literal
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field

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