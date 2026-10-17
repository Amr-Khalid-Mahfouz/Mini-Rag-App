from .minirag_base import SQLAlchemyBase
from sqlalchemy import Column, String, DateTime, func
from sqlalchemy.dialects.postgresql import UUID
import uuid

class Project(SQLAlchemyBase):

    __tablename__ = "projects" # the name of the table used by SQLAlchemy
    
    project_id = Column(String, primary_key=True, unique=True, nullable=False)
    project_uuid = Column(UUID(as_uuid=True), default=uuid.uuid4, unique=True, nullable=False)

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now(), nullable=True)