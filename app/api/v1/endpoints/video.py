import io

from fastapi import APIRouter, Depends, File, Form, UploadFile, status
from fastapi.responses import StreamingResponse
from video_enrichment_orm.schemas.video import Video

from app.api.dependencies import ManagerFactory
from app.business.video import VideoManager
from app.schemas.video import EntityIdsRequest

router = APIRouter(prefix="/video", tags=["Video"])


@router.get(
    "",
    response_model=list[Video],
    status_code=status.HTTP_200_OK,
)
async def get_all_videos(
    manager: VideoManager = Depends(ManagerFactory.for_video),
) -> list[Video]:
    """
    Get all videos should respond status OK and 200 HTTP Response Code.

    Args:
        manager(VideoManager): The manager (domain) with the business logic.

    Returns:
        (json): list of videos
    """

    return manager.get_all_videos()


@router.post(
    "/by-entities",
    response_model=list[Video],
    status_code=status.HTTP_200_OK,
)
async def get_videos_by_entity_ids(
    request: EntityIdsRequest,
    manager: VideoManager = Depends(ManagerFactory.for_video),
) -> list[Video]:
    """
    Get videos by entity IDs should respond status OK and 200 HTTP Response Code.

    Args:
        request(EntityIdsRequest): Request containing list of entity IDs to filter by.
        manager(VideoManager): The manager (domain) with the business logic.

    Returns:
        (json): list of videos that contain detections of the specified entities
    """
    return manager.get_videos_by_entity_ids(request.entity_ids)


@router.get(
    "/{video_uuid}",
    response_model=Video,
    status_code=status.HTTP_200_OK,
)
async def get_video_by_uuid(
    video_uuid: str,
    manager: VideoManager = Depends(ManagerFactory.for_video),
) -> Video:
    """
    Get video by id should respond status OK and 200 HTTP Response Code.

    Args:
        video_uuid(str): The uuid of the video.
        manager(VideoManager): The manager (domain) with the business logic.

    Returns:
        (json): Video
    """

    return manager.get_video_by_uuid(video_uuid=video_uuid)


@router.get(
    "/{video_uuid}/thumbnail",
    status_code=status.HTTP_200_OK,
)
async def get_video_thumbnail(
    video_uuid: str,
    manager: VideoManager = Depends(ManagerFactory.for_video),
) -> StreamingResponse:
    """
    Get video thumbnail by UUID should respond status OK and 200 HTTP Response Code.

    Args:
        video_uuid(str): The uuid of the video.
        manager(VideoManager): The manager (domain) with the business logic.

    Returns:
        (image/jpeg): Video thumbnail image
    """

    thumbnail_content = manager.get_video_thumbnail(video_uuid=video_uuid)
    return StreamingResponse(
        io.BytesIO(thumbnail_content),
        media_type="image/jpeg",
        headers={"Content-Disposition": f"inline; filename=thumbnail_{video_uuid}.jpg"},
    )


@router.get(
    "/{video_uuid}/bytes",
    status_code=status.HTTP_200_OK,
)
async def get_video_bytes(
    video_uuid: str,
    manager: VideoManager = Depends(ManagerFactory.for_video),
) -> StreamingResponse:
    """
    Get video bytes by UUID should respond status OK and 200 HTTP Response Code.

    Args:
        video_uuid(str): The uuid of the video.
        manager(VideoManager): The manager (domain) with the business logic.

    Returns:
        (video/*): Video file bytes
    """

    video_content, content_type = manager.get_video_bytes(video_uuid=video_uuid)
    return StreamingResponse(
        io.BytesIO(video_content),
        media_type=content_type,
        headers={
            "Content-Disposition": f"inline; filename=video_{video_uuid}{manager.get_video_extension(video_uuid)}"
        },
    )


@router.delete(
    "/{video_uuid}",
    response_model=None,
    status_code=status.HTTP_200_OK,
)
async def delete_video(
    video_uuid: str,
    manager: VideoManager = Depends(ManagerFactory.for_video),
) -> None:
    """
    Delete video by id should respond status OK and 200 HTTP Response Code.

    Args:
        video_uuid(str): The uuid of the video.
        manager(VideoManager): The manager (domain) with the business logic.

    Returns:
        (json): None
    """

    return manager.delete_video_by_uuid(video_uuid=video_uuid)


@router.post(
    "",
    response_model=Video,
    status_code=status.HTTP_200_OK,
)
async def save_video(
    code: str = Form(...),
    file: UploadFile = File(...),
    manager: VideoManager = Depends(ManagerFactory.for_video),
) -> Video:
    """
    Create video with file upload should respond status OK and 200 HTTP Response Code.

    Args:
        code(str): The code/name of the video.
        file(UploadFile): The video file to upload.
        manager(VideoManager): The manager (domain) with the business logic.

    Returns:
        (json): Video
    """

    return manager.save_video_with_file(code, file)
