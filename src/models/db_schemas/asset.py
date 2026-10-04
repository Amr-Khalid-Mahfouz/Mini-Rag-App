from pydantic import BaseModel, Field, AfterValidator, ConfigDict
from typing import Optional
from bson.objectid import ObjectId
from datetime import datetime

class Asset(BaseModel):
    id: Optional[ObjectId] = Field(None, alias="_id")
    asset_project_id: ObjectId
    asset_type: str = Field(..., min_length=1)
    asset_name: str = Field(..., min_length=1)
    asset_size: int = Field(ge=0, defualt=None)
    asset_config: dict = Field(default=None)
    asset_pushed_at: datetime = Field(default=datetime.utcnow())

    model_config = ConfigDict(arbitrary_types_allowed=True)

    @classmethod
    def get_indices(cls):
        return [
            {
                "key": [
                    ("asset_project_id", 1) # 1 = ascneding
                ],
                "name": 'asset_project_id_index',
                "unique": False
            },
            {
                "key": [
                    ("asset_project_id", 1),
                    ('asset_name', 1)
                ],
                "name": 'asset_project_id_index_name',
                "unique": True           
            }
        ]