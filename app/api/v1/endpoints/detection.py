from fastapi import APIRouter, Depends, status
from video_enrichment_orm.schemas.detection import Detection

from app.api.dependencies import ManagerFactory
from app.business.detection import DetectionManager

router = APIRouter(prefix="/detection", tags=["Detection"])


@router.get(
    "/by-video/{video_id}",
    response_model=list[Detection],
    status_code=status.HTTP_200_OK,
)
async def get_detections_by_video_id(
    video_id: int,
    manager: DetectionManager = Depends(ManagerFactory.for_detection),
) -> list[Detection]:
    """
    Get detections by video ID should respond status OK and 200 HTTP Response Code.

    Args:
        video_id(int): The video ID to filter detections.
        manager(DetectionManager): The manager (domain) with the business logic.

    Returns:
        (json): list of detections for the video
    """

    return manager.get_detections_by_video_id(video_id=video_id)


@router.get(
    "/by-segment-detection/{segment_detection_id}",
    response_model=list[Detection],
    status_code=status.HTTP_200_OK,
)
async def get_detections_by_segment_detection_id(
    segment_detection_id: int,
    manager: DetectionManager = Depends(ManagerFactory.for_detection),
) -> list[Detection]:
    """
    Get detections by segment detection ID should respond status OK and 200 HTTP Response Code.

    Args:
        segment_detection_id(int): The segment detection ID to filter detections.
        manager(DetectionManager): The manager (domain) with the business logic.

    Returns:
        (json): list of detections for the segment detection
    """

    return manager.get_detections_by_segment_detection_id(segment_detection_id=segment_detection_id)
