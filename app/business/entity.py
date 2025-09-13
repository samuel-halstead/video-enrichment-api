from fastapi import HTTPException, status
from video_enrichment_orm.managers.db_entity import db_entity_manager
from video_enrichment_orm.managers.db_entity_media_gallery import (
    db_entity_media_gallery_manager,
)
from video_enrichment_orm.managers.db_taxonomy import db_taxonomy_manager
from video_enrichment_orm.schemas.entity import Entity, EntityCreate, EntityUpdate

from app.managers.aws.s3 import s3_manager


class EntityManager:
    def __init__(self) -> None:
        self._db_taxonomy = db_taxonomy_manager
        self._db_entity = db_entity_manager
        self._db_entity_media_gallery = db_entity_media_gallery_manager
        self._s3_manager = s3_manager

    def get_all_entities(self) -> list[Entity]:
        return self._db_entity.get_entities()

    def get_enabled_entities(self) -> list[Entity]:
        return self._db_entity.get_enabled_entities()

    def get_entity_by_id(self, entity_id: int) -> Entity:
        try:
            entity = self._db_entity.get_entity_by_id(entity_id=entity_id)
            return entity
        except ValueError as e:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e)) from e

    def get_entity_by_uuid(self, entity_uuid: str) -> Entity:
        try:
            entity = self._db_entity.get_entity_by_uuid(entity_uuid=entity_uuid)
            return entity
        except ValueError as e:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e)) from e

    def get_entities_by_taxonomy_id(self, taxonomy_id: int) -> list[Entity]:
        # Check if taxonomy exists
        try:
            self._db_taxonomy.get_taxonomy_by_id(taxonomy_id=taxonomy_id)
        except ValueError as e:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e)) from e

        return self._db_entity.get_enabled_entities_by_taxonomy_id(taxonomy_id=taxonomy_id)

    def save_entity(self, entity: EntityCreate) -> Entity:
        # Check if taxonomy exists
        try:
            self._db_taxonomy.get_taxonomy_by_id(taxonomy_id=entity.taxonomy_id)
        except ValueError as e:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e)) from e

        entity_request = EntityCreate(
            uuid=entity.uuid,
            alias=entity.alias,
            enabled=entity.enabled,
            taxonomy_id=entity.taxonomy_id,
        )

        entity = self._db_entity.save_entity(entity=entity_request)
        return entity

    def update_entity_by_uuid(self, entity_uuid: str, entity_update: EntityUpdate) -> Entity:
        try:
            entity = self._db_entity.update_entity(entity_update=entity_update, uuid=entity_uuid)
            return entity
        except ValueError as e:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e)) from e

    def delete_entity_by_id(self, entity_id: int) -> None:
        self.delete_media_galleries_for_entity(entity_id=entity_id)
        return self._db_entity.delete_entity_by_id(entity_id=entity_id)

    def delete_entity_by_uuid(self, entity_uuid: str) -> None:
        self.delete_media_galleries_for_entity(entity_uuid=entity_uuid)
        return self._db_entity.delete_entity_by_uuid(entity_uuid=entity_uuid)

    def soft_delete_entity_by_uuid(self, entity_uuid: str) -> None:
        self.delete_media_galleries_for_entity(entity_uuid=entity_uuid)
        return self._db_entity.soft_delete_entity_by_uuid(entity_uuid=entity_uuid)

    def delete_media_galleries_for_entity(self, entity_id: int = None, entity_uuid: str = None) -> None:
        if not entity_id:
            entity = self.get_entity_by_uuid(entity_uuid=entity_uuid)
            if not entity:
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Entity {entity_uuid} not found")
            entity_id = entity.id

        # Get all media galleries for entity
        media_galleries = self._db_entity_media_gallery.get_entity_media_galleries_by_entity_id(entity_id=entity_id)
        for media_gallery in media_galleries:
            bucket, key = s3_manager.decode_path(media_gallery.path)
            s3_manager.delete_object(bucket, key)
