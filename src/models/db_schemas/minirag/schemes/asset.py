from .minirag_base import SQLAlchemyBase
from sqlalchemy import Column, Integer, String, DateTime, func, ForeignKey, Index
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship
import uuid

class Asset(SQLAlchemyBase):
    __tablename__ = "assets"

    asset_id = Column(Integer, primary_key=True, unique=True, nullable=False, autoincrement=True)
    asset_uuid = Column(UUID(as_uuid=True), unique=True, nullable=False, default=uuid.uuid4)
    
    asset_project_id = Column(String, ForeignKey("projects.project_id"), unique=False, nullable=False)
    project = relationship("Project", back_populates="assets")
    
    asset_type = Column(String, nullable=False)
    asset_name = Column(String, nullable=False)
    asset_size = Column(Integer, nullable=False)

    asset_config = Column(JSONB, nullable=True)
    asset_pushed_at = Column(DateTime, nullable= False, server_default=func.now())

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now(), nullable=True)

    # indexes the table on those columns
    __table_args__ = (
            Index("index_asset_project_id", asset_project_id),
            Index("index_asset_type", asset_type)
    )