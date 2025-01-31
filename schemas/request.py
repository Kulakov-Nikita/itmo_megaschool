from typing import List

from pydantic import BaseModel, HttpUrl
from typing import Optional


class PredictionRequest(BaseModel):
    id: int
    query: str


class PredictionResponse(BaseModel):
    id: int
    answer: Optional[int]
    reasoning: str
    sources: List[HttpUrl]
