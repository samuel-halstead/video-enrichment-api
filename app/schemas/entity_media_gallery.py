import uuid
from typing import Optional

from pydantic import Field
from video_enrichment_orm.dao.entity_media_gallery import EntityMediaGalleryDAO
from video_enrichment_orm.schemas.timestamps import Timestamps


class EntityMediaGalleryBase(Timestamps):
    """Base class for EntityMediaGallery schemas to avoid code duplication"""

    uuid: Optional[str] = Field(default_factory=lambda: str(uuid.uuid4()))
    entity_id: int
    path: str
    embedding: None = None
    enabled: Optional[bool] = None


class EntityMediaGallery(EntityMediaGalleryBase):
    """Full EntityMediaGallery schema with ID and UUID for existing entity media galleries"""

    id: Optional[int] = None
    has_embedding: bool = False

    @classmethod
    def from_orm(cls, obj: EntityMediaGalleryDAO) -> "EntityMediaGallery":
        return cls(
            id=obj.id,
            uuid=obj.uuid,
            entity_id=obj.entity_id,
            path=obj.path,
            enabled=obj.enabled,
            has_embedding=obj.embedding is not None,
            created_at=obj.created_at,
            created_by=obj.created_by,
            updated_at=obj.updated_at,
            updated_by=obj.updated_by,
        )


class EntityMediaGalleryCreate(EntityMediaGalleryBase):
    """EntityMediaGallery schema for creating new entity media galleries without ID"""

    @classmethod
    def to_orm(cls, obj: "EntityMediaGalleryCreate") -> EntityMediaGalleryDAO:
        """Convert to EntityMediaGalleryDAO for database insertion"""
        return EntityMediaGalleryDAO(
            uuid=obj.uuid,
            entity_id=obj.entity_id,
            path=obj.path,
            embedding=None,
            enabled=obj.enabled,
            created_at=obj.created_at,
            created_by=obj.created_by,
            updated_at=obj.updated_at,
            updated_by=obj.updated_by,
        )


class EntityMediaGalleryUpdate(Timestamps):
    path: Optional[str] = None
    enabled: Optional[bool] = None
