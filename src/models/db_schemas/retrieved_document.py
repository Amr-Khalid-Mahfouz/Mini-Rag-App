from pydantic import BaseModel
from typing import Optional

class RetrievedDocument(BaseModel):
    text: str
    score: float