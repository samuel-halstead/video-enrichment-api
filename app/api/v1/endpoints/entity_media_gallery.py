import base64
import mimetypes

from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile, status
from fastapi.responses import StreamingResponse

from app.api.dependencies import ManagerFactory
from app.business.entity_media_gallery import EntityMediaGalleryManager
from app.managers.aws.s3 import s3_manager
from app.schemas.entity_media_gallery import (
    EntityMediaGallery,
    EntityMediaGalleryUpdate,
)

router = APIRouter(prefix="/entity-media-gallery", tags=["Entity Media Gallery"])


@router.get(
    "",
    response_model=list[EntityMediaGallery],
    status_code=status.HTTP_200_OK,
)
async def get_all_entity_media_galleries(
    manager: EntityMediaGalleryManager = Depends(ManagerFactory.for_entity_media_gallery),
) -> list[EntityMediaGallery]:
    """
    Get all enabled entity media galleries should respond status OK and 200 HTTP Response Code.

    Args:
        manager(EntityMediaGalleryManager): The manager (domain) with the business logic.

    Returns:
        (json): list of enabled entity media galleries
    """

    return manager.get_all_entity_media_galleries()


@router.get(
    "/{media_gallery_uuid}",
    response_model=EntityMediaGallery,
    status_code=status.HTTP_200_OK,
)
async def get_entity_media_gallery_by_uuid(
    media_gallery_uuid: str,
    manager: EntityMediaGalleryManager = Depends(ManagerFactory.for_entity_media_gallery),
) -> EntityMediaGallery:
    """
    Get entity media gallery by uuid should respond status OK and 200 HTTP Response Code.

    Args:
        media_gallery_uuid(str): The uuid of the entity media gallery.
        manager(EntityMediaGalleryManager): The manager (domain) with the business logic.

    Returns:
        (json): EntityMediaGallery
    """

    return manager.get_entity_media_gallery_by_uuid(media_gallery_uuid=media_gallery_uuid)


@router.get(
    "/by-entity/{entity_id}",
    response_model=list[EntityMediaGallery],
    status_code=status.HTTP_200_OK,
)
async def get_entity_media_galleries_by_entity_id(
    entity_id: int,
    manager: EntityMediaGalleryManager = Depends(ManagerFactory.for_entity_media_gallery),
) -> list[EntityMediaGallery]:
    """
    Get enabled entity media galleries by entity id should respond status OK and 200 HTTP Response Code.

    Args:
        entity_id(int): The entity id to filter media galleries.
        manager(EntityMediaGalleryManager): The manager (domain) with the business logic.

    Returns:
        (json): list of enabled entity media galleries for the entity
    """

    return manager.get_entity_media_galleries_by_entity_id(entity_id=entity_id)


@router.post(
    "",
    response_model=EntityMediaGallery,
    status_code=status.HTTP_200_OK,
)
async def save_entity_media_gallery(
    entity_id: int = Form(...),
    file: UploadFile = File(...),
    manager: EntityMediaGalleryManager = Depends(ManagerFactory.for_entity_media_gallery),
) -> EntityMediaGallery:
    """
    Create entity media gallery with file upload.
    """
    return manager.save_entity_media_gallery_with_file(entity_id, file)


@router.put(
    "/{media_gallery_uuid}",
    response_model=EntityMediaGallery,
    status_code=status.HTTP_200_OK,
)
async def update_entity_media_gallery(
    media_gallery_uuid: str,
    media_gallery_update: EntityMediaGalleryUpdate,
    manager: EntityMediaGalleryManager = Depends(ManagerFactory.for_entity_media_gallery),
) -> EntityMediaGallery:
    """
    Update entity media gallery should respond status OK and 200 HTTP Response Code.

    Args:
        media_gallery_uuid(str): The uuid of the entity media gallery.
        media_gallery_update(EntityMediaGalleryUpdate): The entity media gallery update data.
        manager(EntityMediaGalleryManager): The manager (domain) with the business logic.

    Returns:
        (json): Updated EntityMediaGallery
    """

    return manager.update_entity_media_gallery_by_uuid(
        media_gallery_uuid=media_gallery_uuid, media_gallery_update=media_gallery_update
    )


@router.delete(
    "/{media_gallery_uuid}",
    response_model=None,
    status_code=status.HTTP_200_OK,
)
async def delete_entity_media_gallery(
    media_gallery_uuid: str,
    manager: EntityMediaGalleryManager = Depends(ManagerFactory.for_entity_media_gallery),
) -> None:
    """
    Delete entity media gallery by uuid should respond status OK and 200 HTTP Response Code.

    Args:
        media_gallery_uuid(str): The uuid of the entity media gallery.
        manager(EntityMediaGalleryManager): The manager (domain) with the business logic.

    Returns:
        (json): None
    """

    return manager.delete_entity_media_gallery_by_uuid(media_gallery_uuid=media_gallery_uuid)


@router.get(
    "/{media_gallery_uuid}/image",
    status_code=status.HTTP_200_OK,
)
async def get_entity_media_gallery_image_by_uuid(
    media_gallery_uuid: str,
    manager: EntityMediaGalleryManager = Depends(ManagerFactory.for_entity_media_gallery),
):
    """
    Get the image bytes for a single entity media gallery by uuid.
    """
    gallery = manager.get_entity_media_gallery_by_uuid(media_gallery_uuid=media_gallery_uuid)
    bucket, key = s3_manager.decode_path(gallery.path)
    image_bytes = s3_manager.download_object(bucket, key)
    if image_bytes is None:
        raise HTTPException(status_code=404, detail="Image not found in S3")
    # Guess content type from file extension
    content_type, _ = mimetypes.guess_type(key)
    return StreamingResponse(iter([image_bytes]), media_type=content_type or "application/octet-stream")


@router.get(
    "/by-entity/{entity_id}/images",
    status_code=status.HTTP_200_OK,
)
async def get_entity_media_galleries_images_by_entity_id(
    entity_id: int,
    manager: EntityMediaGalleryManager = Depends(ManagerFactory.for_entity_media_gallery),
):
    """
    Get the image bytes for all enabled entity media galleries for an entity.
    Returns a list of dicts with uuid and image bytes (base64 encoded for JSON compatibility).
    """
    galleries = manager.get_entity_media_galleries_by_entity_id(entity_id=entity_id)
    images = []
    for gallery in galleries:
        bucket, key = s3_manager.decode_path(gallery.path)
        image_bytes = s3_manager.download_object(bucket, key)
        if image_bytes is not None:
            images.append(
                {
                    "uuid": gallery.uuid,
                    "image_base64": base64.b64encode(image_bytes).decode("utf-8"),
                    "content_type": mimetypes.guess_type(key)[0] or "application/octet-stream",
                }
            )
    return images
