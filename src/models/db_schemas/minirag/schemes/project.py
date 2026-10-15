from .minirag_base import SQLAlchemyBase
from sqlalchemy import column, String, DateTime, func
from sqlalchemy.dialects.postgresql import UUID
import uuid

class Project(SQLAlchemyBase):

    __tablename__ = "projects" # the name of the table used by SQLAlchemy
    
    project_id = column(String, primary_key=True, unique=True, nullable=False)
    project_uuid = column(UUID(as_uuid=True), defualt=uuid.uuid4, unique=True, nullable=False)

    created_at = column(DateTime(timezone=True), server_default=func.now())
    updated_at = column(DateTime(timezone=True), onupdate=func.now(), nullable=True)