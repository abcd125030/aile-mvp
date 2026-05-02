"""Knowledge point schemas."""

from pydantic import BaseModel, ConfigDict


class KnowledgePointResponse(BaseModel):
    """Knowledge point payload."""

    model_config = ConfigDict(from_attributes=True)

    id: str
    name: str
    description: str | None
    prerequisite_ids: list[str]
    difficulty: float
    subject: str


class KnowledgePointDetailResponse(KnowledgePointResponse):
    """Knowledge point detail with prerequisite objects."""

    prerequisites: list[KnowledgePointResponse]
