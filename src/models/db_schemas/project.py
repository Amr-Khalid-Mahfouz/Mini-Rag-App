from pydantic import BaseModel, Field, AfterValidator, ConfigDict
from typing import Optional, Annotated
from bson.objectid import ObjectId

def validate_project_id(value:str) -> str:
    if not value.isalnum():
        raise ValueError('project_id should be alphanumeric')
    return value

class Project(BaseModel):
    
    id: Optional[ObjectId] = Field(None, alias="_id")
    project_id: Annotated[str, Field(..., min_length=1), AfterValidator(validate_project_id)]

    model_config = ConfigDict(arbitrary_types_allowed=True)

    @classmethod
    def get_indices(cls):
        return [
            {
                "key": [
                    ("project_id", 1) # 1 = ascneding
                ],
                "name": 'project_id_index',
                "unique": True
            }
        ]