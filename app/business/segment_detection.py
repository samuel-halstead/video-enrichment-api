from fastapi import HTTPException, status
from video_enrichment_orm.managers.db_segment_detection import (
    db_segment_detection_manager,
)
from video_enrichment_orm.managers.db_taxonomy import db_taxonomy_manager
from video_enrichment_orm.managers.db_video import db_video_manager
from video_enrichment_orm.schemas.segment_detection import SegmentDetection


class SegmentDetectionManager:
    def __init__(self) -> None:
        self._db_segment_detection = db_segment_detection_manager
        self._db_video = db_video_manager
        self._db_taxonomy = db_taxonomy_manager

    def get_segment_detections_by_video_id(self, video_id: int) -> list[SegmentDetection]:
        """
        Get segment detections by video ID.
        Validates that the video exists before returning results.
        """
        try:
            video = self._db_video.get_video_by_id(video_id=video_id)
            if not video:
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Video {video_id} not found")
        except ValueError as e:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e)) from e

        return self._db_segment_detection.get_segment_detections_by_video_id(video_id=video_id)

    def get_segment_detections_by_video_and_taxonomy(self, video_id: int, taxonomy_id: int) -> list[SegmentDetection]:
        """
        Get segment detections by video ID and taxonomy ID.
        Validates that both the video and taxonomy exist before returning results.
        """
        # Check if video exists
        try:
            video = self._db_video.get_video_by_id(video_id=video_id)
            if not video:
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Video {video_id} not found")
        except ValueError as e:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e)) from e

        # Check if taxonomy exists
        try:
            taxonomy = self._db_taxonomy.get_taxonomy_by_id(taxonomy_id=taxonomy_id)
            if not taxonomy:
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Taxonomy {taxonomy_id} not found")
        except ValueError as e:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e)) from e

        return self._db_segment_detection.get_segment_detections_by_video_and_taxonomy(
            video_id=video_id, taxonomy_id=taxonomy_id
        )
