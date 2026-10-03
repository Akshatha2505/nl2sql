from typing import Any

from pydantic import BaseModel, Field


class QueryRequest(BaseModel):
    question: str = Field(..., min_length=1, description="Natural language question")


class QueryResponse(BaseModel):
    question: str
    sql: str
    columns: list[str]
    rows: list[dict[str, Any]]
    row_count: int
    attempts: int = Field(..., ge=1, le=2)
