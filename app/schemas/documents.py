from datetime import datetime

from pydantic import BaseModel, ConfigDict


class DocumentCreate(BaseModel):
    rubrics: list[str]
    text: str
    created_date: datetime


class DocumentResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    rubrics: list[str]
    text: str
    created_date: datetime