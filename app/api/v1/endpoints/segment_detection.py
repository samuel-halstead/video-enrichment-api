from fastapi import APIRouter, Depends, status
from video_enrichment_orm.schemas.segment_detection import SegmentDetection

from app.api.dependencies import ManagerFactory
from app.business.segment_detection import SegmentDetectionManager

router = APIRouter(prefix="/segment-detection", tags=["Segment Detection"])


@router.get(
    "/by-video/{video_id}",
    response_model=list[SegmentDetection],
    status_code=status.HTTP_200_OK,
)
async def get_segment_detections_by_video_id(
    video_id: int,
    manager: SegmentDetectionManager = Depends(ManagerFactory.for_segment_detection),
) -> list[SegmentDetection]:
    """
    Get segment detections by video ID should respond status OK and 200 HTTP Response Code.

    Args:
        video_id(int): The video ID to filter segment detections.
        manager(SegmentDetectionManager): The manager (domain) with the business logic.

    Returns:
        (json): list of segment detections for the video
    """

    return manager.get_segment_detections_by_video_id(video_id=video_id)


@router.get(
    "/by-video/{video_id}/taxonomy/{taxonomy_id}",
    response_model=list[SegmentDetection],
    status_code=status.HTTP_200_OK,
)
async def get_segment_detections_by_video_and_taxonomy(
    video_id: int,
    taxonomy_id: int,
    manager: SegmentDetectionManager = Depends(ManagerFactory.for_segment_detection),
) -> list[SegmentDetection]:
    """
    Get segment detections by video ID and taxonomy ID should respond status OK and 200 HTTP Response Code.

    Args:
        video_id(int): The video ID to filter segment detections.
        taxonomy_id(int): The taxonomy ID to filter segment detections.
        manager(SegmentDetectionManager): The manager (domain) with the business logic.

    Returns:
        (json): list of segment detections for the video and taxonomy
    """

    return manager.get_segment_detections_by_video_and_taxonomy(video_id=video_id, taxonomy_id=taxonomy_id)
