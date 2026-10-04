from pydantic import BaseModel, Field, ConfigDict
from typing import Optional
from bson.objectid import ObjectId

class DataChunk(BaseModel):
    id: Optional[ObjectId] = Field(None, alias="_id")
    chunk_text: str = Field(..., min_length=1)
    meta_data: dict
    chunk_order: int = Field(..., gt=0)
    chunk_project_id: ObjectId

    model_config = ConfigDict(arbitrary_types_allowed=True)

    @classmethod
    def get_indices(cls):
        return [
            {
                "key": [
                    ("chunk_project_id", 1) # 1 = ascneding
                ],
                "name": 'chunk_project_id_index',
                "unique": False
            }
        ]