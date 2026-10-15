from .minirag_base import SQLAlchemyBase
from sqlalchemy import column, Integer, String, DateTime, func, ForeignKey, Index
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship
import uuid

class Asset(SQLAlchemyBase):
    __tablename__ = "assets"

    asset_id = column(Integer, primary_key=True, unique=True, nullable=False, autoincrement=True)
    asset_uuid = column(UUID(as_uuid=True), defualt=uuid.uuid4, unique=True, nullable=False)
    
    asset_project_id = column(String, ForeignKey("projects.project_id"), unique=False, nullable=False)
    project = relationship("Project", back_populates="assets")
    
    asset_type = column(String, nullable=False)
    asset_name = column(String, nullable=False)
    asset_size = column(Integer, nullable=False)

    asset_config = column(JSONB, nullable=True)
    asset_pushed_at = column(DateTime, nullable= False, server_default=func.now())

    created_at = column(DateTime(timezone=True), server_default=func.now())
    updated_at = column(DateTime(timezone=True), onupdate=func.now(), nullable=True)

    # indexes the table on those columns
    __table_args__ = {
            Index("index_asset_project_id", asset_project_id),
            Index("index_asset_type", asset_type)
        }