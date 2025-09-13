from fastapi import HTTPException, status
from video_enrichment_orm.managers.db_entity import db_entity_manager
from video_enrichment_orm.managers.db_entity_media_gallery import (
    db_entity_media_gallery_manager,
)

from app.core.config import settings
from app.managers.aws.s3 import s3_manager
from app.schemas.entity_media_gallery import (
    EntityMediaGallery,
    EntityMediaGalleryCreate,
    EntityMediaGalleryUpdate,
)


class EntityMediaGalleryManager:
    def __init__(self) -> None:
        self._db_entity = db_entity_manager
        self._db_entity_media_gallery = db_entity_media_gallery_manager

    def get_all_entity_media_galleries(self) -> list[EntityMediaGallery]:
        return self._db_entity_media_gallery.get_enabled_entity_media_galleries()

    def get_entity_media_gallery_by_uuid(self, media_gallery_uuid: str) -> EntityMediaGallery:
        try:
            media_gallery = self._db_entity_media_gallery.get_entity_media_gallery_by_uuid(
                media_gallery_uuid=media_gallery_uuid
            )
            return media_gallery
        except ValueError as e:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e)) from e

    def get_entity_media_galleries_by_entity_id(self, entity_id: int) -> list[EntityMediaGallery]:
        try:
            entity = self._db_entity.get_entity_by_id(entity_id=entity_id)
            if not entity:
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Entity {entity_id} not found")
        except ValueError as e:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e)) from e

        return self._db_entity_media_gallery.get_enabled_entity_media_galleries_by_entity_id(entity_id=entity_id)

    def save_entity_media_gallery(self, media_gallery: EntityMediaGalleryCreate) -> EntityMediaGallery:
        bucket, key = s3_manager.decode_path(media_gallery.path)
        if not s3_manager.exists(bucket, key):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail=f"media gallery {media_gallery.path} not exists"
            )

        try:
            entity = self._db_entity.get_entity_by_id(entity_id=media_gallery.entity_id)
            if not entity:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND, detail=f"Entity {media_gallery.entity_id} not found"
                )
        except ValueError as e:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e)) from e

        media_gallery_request = EntityMediaGalleryCreate(
            uuid=media_gallery.uuid,
            entity_id=media_gallery.entity_id,
            path=media_gallery.path,
            embedding=media_gallery.embedding,
            enabled=media_gallery.enabled,
        )

        media_gallery = self._db_entity_media_gallery.save_entity_media_gallery(media_gallery=media_gallery_request)
        return media_gallery

    def save_entity_media_gallery_with_file(self, entity_id, file):
        # Get entity uuid
        entity = self._db_entity.get_entity_by_id(entity_id=entity_id)
        if not entity:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Entity {entity_id} not found")
        entity_uuid = entity.uuid

        # Validate entity exists
        entity = self._db_entity.get_entity_by_id(entity_id=entity_id)
        if not entity:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Entity {entity_id} not found")
        # S3 path: S3_GALLERY_PATH/entity_uuid/file_name
        file_name = file.filename
        s3_path = f"{settings.S3_GALLERY_PATH}/{entity_uuid}/{file_name}"
        bucket, key = s3_manager.decode_path(s3_path)
        # Upload file to S3
        file_content = file.file.read()
        if not s3_manager.upload_object(bucket, key, file_content):
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to upload file to S3")
        # Save DB record
        media_gallery_request = EntityMediaGalleryCreate(
            entity_id=entity_id,
            path=s3_path,
            embedding=None,
            enabled=True,
        )
        media_gallery = self._db_entity_media_gallery.save_entity_media_gallery(media_gallery=media_gallery_request)
        return media_gallery

    def update_entity_media_gallery_by_uuid(
        self, media_gallery_uuid: str, media_gallery_update: EntityMediaGalleryUpdate
    ) -> EntityMediaGallery:
        try:
            media_gallery = self._db_entity_media_gallery.update_entity_media_gallery(
                media_gallery_update=media_gallery_update, uuid=media_gallery_uuid
            )
            return media_gallery
        except ValueError as e:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e)) from e

    def delete_entity_media_gallery_by_uuid(self, media_gallery_uuid: str) -> None:
        media_gallery = self._db_entity_media_gallery.get_entity_media_gallery_by_uuid(
            media_gallery_uuid=media_gallery_uuid
        )
        if not media_gallery:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail=f"Media gallery {media_gallery_uuid} not found"
            )
        bucket, key = s3_manager.decode_path(media_gallery.path)
        s3_manager.delete_object(bucket, key)
        return self._db_entity_media_gallery.delete_entity_media_gallery_by_uuid(media_gallery_uuid=media_gallery_uuid)

    def soft_delete_entity_media_gallery_by_uuid(self, media_gallery_uuid: str) -> None:
        return self._db_entity_media_gallery.soft_delete_entity_media_gallery_by_uuid(
            media_gallery_uuid=media_gallery_uuid
        )
