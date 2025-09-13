import os
import tempfile
import uuid

import cv2
from fastapi import HTTPException, UploadFile, status
from video_enrichment_orm.managers.db_segment_detection import (
    db_segment_detection_manager,
)
from video_enrichment_orm.managers.db_video import db_video_manager
from video_enrichment_orm.schemas.video import Video, VideoCreate

from app.core.config import settings
from app.managers.aws.s3 import s3_manager


class VideoManager:
    def __init__(self) -> None:
        self._db_video = db_video_manager
        self._db_segment_detection = db_segment_detection_manager

    def get_all_videos(self) -> list[Video]:
        return self._db_video.get_videos()

    def get_video_by_id(self, video_id: int) -> Video:
        video = self._db_video.get_video_by_id(video_id=video_id)
        if not video:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Video {video_id} not found")

        return video

    def get_video_by_uuid(self, video_uuid: str) -> Video:
        video = self._db_video.get_video_by_uuid(video_uuid=video_uuid)
        if not video:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Video {video_uuid} not found")

        return video

    def get_videos_by_entity_ids(self, entity_ids: list[int]) -> list[Video]:
        """
        Get videos that contain detections of the specified entities.

        Args:
            entity_ids: List of entity IDs to filter by

        Returns:
            List of videos that contain detections of the specified entities
        """

        if not entity_ids:
            return []

        # Get all segment detections for the specified entities
        segment_detections = self._db_segment_detection.get_segment_detections_by_entity_ids(entity_ids=entity_ids)

        # Extract unique video IDs from segment detections
        video_ids = list({detection.video_id for detection in segment_detections})

        if not video_ids:
            return []

        # Get videos by IDs
        videos = self._db_video.get_videos_by_ids(video_ids)

        return videos

    def get_video_thumbnail(self, video_uuid: str) -> bytes:
        """Get video thumbnail from S3 by video UUID."""
        # Get video from database to verify it exists
        video = self.get_video_by_uuid(video_uuid=video_uuid)

        # Construct thumbnail path based on video path
        video_dir = os.path.dirname(video.path)
        thumbnail_s3_path = f"{video_dir}/thumbnail.jpg"

        # Download thumbnail from S3
        bucket, key = s3_manager.decode_path(thumbnail_s3_path)
        thumbnail_content = s3_manager.download_object(bucket, key)

        if not thumbnail_content:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Thumbnail not found in S3")

        return thumbnail_content

    def get_video_bytes(self, video_uuid: str) -> tuple[bytes, str]:
        """Get video bytes from S3 by video UUID."""
        # Get video from database to verify it exists
        video = self.get_video_by_uuid(video_uuid=video_uuid)

        # Download video from S3
        bucket, key = s3_manager.decode_path(video.path)
        video_content = s3_manager.download_object(bucket, key)

        if not video_content:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Video not found in S3")

        # Determine content type based on file extension
        content_type = self._get_content_type_from_extension(video.extension)

        return video_content, content_type

    def get_video_extension(self, video_uuid: str) -> str:
        """Get video file extension by video UUID."""
        video = self.get_video_by_uuid(video_uuid=video_uuid)
        return video.extension

    def _get_content_type_from_extension(self, extension: str) -> str:
        """Get MIME content type from file extension."""
        extension_lower = extension.lower()
        content_type_map = {
            ".mp4": "video/mp4",
            ".avi": "video/x-msvideo",
            ".mov": "video/quicktime",
            ".wmv": "video/x-ms-wmv",
            ".flv": "video/x-flv",
            ".webm": "video/webm",
            ".mkv": "video/x-matroska",
            ".m4v": "video/x-m4v",
            ".3gp": "video/3gpp",
            ".ogv": "video/ogg",
        }
        return content_type_map.get(extension_lower, "application/octet-stream")

    def save_video(self, video: VideoCreate) -> Video:
        bucket, key = s3_manager.decode_path(video.path)
        if not s3_manager.exists(bucket, key):
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Video {video.path} not exists")

        video_extension = video.path.split(".")[-1]

        video_request = VideoCreate(
            uuid=video.uuid,
            code=video.code,
            path=video.path,
            extension=video_extension,
            frames=video.frame_rate,
            length=video.length,
            frame_rate=video.frame_rate,
        )

        video = self._db_video.save_video(video=video_request)

        return video

    def save_video_with_file(self, code: str, file: UploadFile) -> Video:
        # Validate file type
        if not file.content_type or not file.content_type.startswith("video/"):
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="File must be a video")

        # Create temporary file to process video
        with tempfile.NamedTemporaryFile(delete=False, suffix=os.path.splitext(file.filename)[1]) as temp_file:
            # Write uploaded file to temporary file
            file_content = file.file.read()
            temp_file.write(file_content)
            temp_file.flush()

            # Extract video metadata using OpenCV
            cap = cv2.VideoCapture(temp_file.name)
            if not cap.isOpened():
                raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid video file")

            # Get video properties
            frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
            fps = cap.get(cv2.CAP_PROP_FPS)
            duration = frame_count / fps if fps > 0 else 0

            # Extract first frame as thumbnail
            ret, frame = cap.read()
            if not ret:
                raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Could not read video frames")

            cap.release()

            # Clean up temporary file
            os.unlink(temp_file.name)

        # Generate UUID for the video
        video_uuid = str(uuid.uuid4())

        # Determine file extension
        file_extension = os.path.splitext(file.filename)[1] if file.filename else ".mp4"

        # S3 paths: S3_VIDEO_PATH/video_uuid/video_file and S3_VIDEO_PATH/video_uuid/thumbnail.jpg
        video_s3_path = f"{settings.S3_VIDEO_PATH}/{video_uuid}/{file.filename or 'video' + file_extension}"
        thumbnail_s3_path = f"{settings.S3_VIDEO_PATH}/{video_uuid}/thumbnail.jpg"

        # Upload video to S3
        bucket, key = s3_manager.decode_path(video_s3_path)
        if not s3_manager.upload_object(bucket, key, file_content):
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to upload video to S3"
            )

        # Save thumbnail as JPEG and upload to S3
        _, thumbnail_buffer = cv2.imencode(".jpg", frame)
        thumbnail_content = thumbnail_buffer.tobytes()

        bucket, key = s3_manager.decode_path(thumbnail_s3_path)
        if not s3_manager.upload_object(bucket, key, thumbnail_content):
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to upload thumbnail to S3"
            )

        # Save video record to database
        video_request = VideoCreate(
            uuid=video_uuid,
            code=code,
            path=video_s3_path,
            extension=file_extension,
            frames=frame_count,
            length=int(duration),
            frame_rate=fps,
        )

        video = self._db_video.save_video(video=video_request)
        return video

    def delete_video_by_id(self, video_id: int) -> None:
        self.delete_video_from_s3(video_id=video_id)
        return self._db_video.delete_video_by_id(video_id=video_id)

    def delete_video_by_uuid(self, video_uuid: str) -> None:
        self.delete_video_from_s3(video_uuid=video_uuid)
        return self._db_video.delete_video_by_uuid(video_uuid=video_uuid)

    def delete_video_from_s3(self, video_id: int = None, video_uuid: str = None) -> None:
        if video_id:
            video = self.get_video_by_id(video_id=video_id)
            if not video:
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Video {video_id} not found")
            video_path = video.path
        elif video_uuid:
            video = self.get_video_by_uuid(video_uuid=video_uuid)
            if not video:
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Video {video_uuid} not found")
            video_path = video.path
        else:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Video ID or UUID is required")

        bucket, key = s3_manager.decode_path(video_path)
        s3_manager.delete_object(bucket, key)
