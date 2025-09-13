from fastapi import HTTPException, status
from video_enrichment_orm.managers.db_detection import db_detection_manager
from video_enrichment_orm.managers.db_segment_detection import (
    db_segment_detection_manager,
)
from video_enrichment_orm.managers.db_video import db_video_manager
from video_enrichment_orm.schemas.detection import Detection


class DetectionManager:
    def __init__(self) -> None:
        self._db_detection = db_detection_manager
        self._db_video = db_video_manager
        self._db_segment_detection = db_segment_detection_manager

    def get_detections_by_video_id(self, video_id: int) -> list[Detection]:
        """
        Get detections by video ID.
        Validates that the video exists before returning results.
        """
        try:
            video = self._db_video.get_video_by_id(video_id=video_id)
            if not video:
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Video {video_id} not found")
        except ValueError as e:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e)) from e

        return self._db_detection.get_detections_by_video_id(video_id=video_id)

    def get_detections_by_segment_detection_id(self, segment_detection_id: int) -> list[Detection]:
        """
        Get detections by segment detection ID.
        Validates that the segment detection exists before returning results.
        """
        try:
            segment_detection = self._db_segment_detection.get_segment_detection_by_id(
                segment_detection_id=segment_detection_id
            )
            if not segment_detection:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND, detail=f"Segment detection {segment_detection_id} not found"
                )
        except ValueError as e:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e)) from e

        return self._db_detection.get_detections_by_segment_detection_id(segment_detection_id=segment_detection_id)
