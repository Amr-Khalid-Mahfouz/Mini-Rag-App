from .minirag_base import SQLAlchemyBase
from sqlalchemy import column, Integer, String, DateTime, func, ForeignKey, Index
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship
import uuid

class DataChunk(SQLAlchemyBase):
    __tablename__ = 'chunks'

    chunk_uuid = column(UUID(as_uuid=True), defualt=uuid.uuid4, unique=True, nullable=False)

    chunk_text = column(String, nullable=False)
    meta_data =  column(JSONB)
    chunk_order = column(Integer, nullable=False)
    
    chunk_project_id = column(String, ForeignKey('projects.project_id')) 
    project = relationship("Project", back_populates='chunks')
    
    chunk_asset_id = column(String, ForeignKey("assets.asset_id"))
    asset = relationship("Asset", back_populates='chunks')

    created_at = column(DateTime(timezone=True), server_default=func.now())
    updated_at = column(DateTime(timezone=True), onupdate=func.now(), nullable=True)

    __table_args__ = {
            Index("index_chunk_asset_id", chunk_asset_id),
            Index("index_chunk_project_id", chunk_project_id)
        }