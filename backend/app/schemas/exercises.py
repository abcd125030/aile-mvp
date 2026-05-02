"""Exercise schemas."""

from typing import Any

from pydantic import BaseModel, ConfigDict


class ExerciseItemResponse(BaseModel):
    """Exercise payload returned to the client."""

    model_config = ConfigDict(from_attributes=True)

    id: str
    stem: str
    options: list[str] | None
    knowledge_point_ids: list[str]
    difficulty: float
    metadata: dict[str, Any]
