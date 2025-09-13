from unittest.mock import patch

import pytest
from fastapi import HTTPException, status
from fastapi.testclient import TestClient
from video_enrichment_orm.schemas.video import Video, VideoCreate

from app.core.config import settings
from app.main import app


@pytest.fixture
def client():
    return TestClient(app)


@pytest.fixture
def auth_headers():
    return {settings.AUTH_HEADER_KEY: settings.AUTH_SECRET_KEY}


# Sample data for testing
video_data = [
    Video(
        id=1,
        code="20_11_2024_13_24_23_rtve",
        uuid="f50ec0b7-f960-400d-91f0-c42a6d44e3d0",
        path="bucket/video-enrichment/20_11_2024_13_24_23_rtve.mp4",
        extension=".mp4",
        frames=7260,
        length=121,
        frame_rate=60,
    ),
    Video(
        id=2,
        code="20_11_2024_13_34_23_lsxt",
        uuid="s50ec0b7-f960-400d-91f0-c42a6d44e3d1",
        path="bucket/video-enrichment/20_11_2024_13_34_23_lsxt.avi",
        extension=".avi",
        frames=3600,
        length=60,
        frame_rate=60,
    ),
]

video_create_data = VideoCreate(
    uuid="test-uuid-123",
    code="test_video",
    path="test/path/video.mp4",
    extension=".mp4",
    frames=1000,
    length=30,
    frame_rate=30,
)


class TestVideoEndpoints:
    """Test cases for video API endpoints."""

    def test_get_all_videos_success(self, client, auth_headers):
        """Test successful retrieval of all videos."""
        with patch("app.business.video.VideoManager.get_all_videos") as mock_get_all:
            mock_get_all.return_value = video_data

            response = client.get(f"{settings.API_V1_STR}/video", headers=auth_headers)

            assert response.status_code == 200
            data = response.json()
            assert len(data) == 2
            assert data[0]["code"] == "20_11_2024_13_24_23_rtve"
            assert data[1]["code"] == "20_11_2024_13_34_23_lsxt"
            mock_get_all.assert_called_once()

    def test_get_all_videos_unauthorized(self, client):
        """Test unauthorized access to get all videos."""
        response = client.get(f"{settings.API_V1_STR}/video")
        assert response.status_code == 403

    def test_get_video_by_uuid_success(self, client, auth_headers):
        """Test successful retrieval of video by UUID."""
        with patch("app.business.video.VideoManager.get_video_by_uuid") as mock_get_video:
            mock_get_video.return_value = video_data[0]

            response = client.get(
                f"{settings.API_V1_STR}/video/f50ec0b7-f960-400d-91f0-c42a6d44e3d0", headers=auth_headers
            )

            assert response.status_code == 200
            data = response.json()
            assert data["uuid"] == "f50ec0b7-f960-400d-91f0-c42a6d44e3d0"
            assert data["code"] == "20_11_2024_13_24_23_rtve"
            mock_get_video.assert_called_once_with(video_uuid="f50ec0b7-f960-400d-91f0-c42a6d44e3d0")

    def test_get_video_by_uuid_not_found(self, client, auth_headers):
        """Test video not found by UUID."""
        with patch("app.business.video.VideoManager.get_video_by_uuid") as mock_get_video:
            mock_get_video.side_effect = HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Video f50ec0b7-f960-400d-91f0-c42a6d44e3d1 not found"
            )

            response = client.get(
                f"{settings.API_V1_STR}/video/f50ec0b7-f960-400d-91f0-c42a6d44e3d1", headers=auth_headers
            )

            assert response.status_code == 404
            data = response.json()
            assert data["detail"] == "Video f50ec0b7-f960-400d-91f0-c42a6d44e3d1 not found"

    def test_get_video_by_uuid_unauthorized(self, client):
        """Test unauthorized access to get video by UUID."""
        response = client.get(f"{settings.API_V1_STR}/video/f50ec0b7-f960-400d-91f0-c42a6d44e3d0")
        assert response.status_code == 403

    def test_delete_video_success(self, client, auth_headers):
        """Test successful deletion of video."""
        with patch("app.business.video.VideoManager.delete_video_by_uuid") as mock_delete:
            mock_delete.return_value = None

            response = client.delete(
                f"{settings.API_V1_STR}/video/f50ec0b7-f960-400d-91f0-c42a6d44e3d0", headers=auth_headers
            )

            assert response.status_code == 200
            mock_delete.assert_called_once_with(video_uuid="f50ec0b7-f960-400d-91f0-c42a6d44e3d0")

    def test_delete_video_unauthorized(self, client):
        """Test unauthorized access to delete video."""
        response = client.delete(f"{settings.API_V1_STR}/video/f50ec0b7-f960-400d-91f0-c42a6d44e3d0")
        assert response.status_code == 403

    def test_save_video_success(self, client, auth_headers):
        """Test successful video creation with file upload."""
        # Create a mock video file
        video_content = b"fake video content"

        with patch("app.business.video.VideoManager.save_video_with_file") as mock_save:
            mock_save.return_value = video_data[0]

            response = client.post(
                f"{settings.API_V1_STR}/video",
                headers=auth_headers,
                files={"file": ("test_video.mp4", video_content, "video/mp4")},
                data={"code": "test_video"},
            )

            assert response.status_code == 200
            data = response.json()
            assert data["code"] == "20_11_2024_13_24_23_rtve"
            mock_save.assert_called_once()

    def test_save_video_bad_request(self, client, auth_headers):
        """Test video creation with bad request."""
        with patch("app.business.video.VideoManager.save_video_with_file") as mock_save:
            mock_save.side_effect = HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid video file")

            video_content = b"fake video content"
            response = client.post(
                f"{settings.API_V1_STR}/video",
                headers=auth_headers,
                files={"file": ("test_video.mp4", video_content, "video/mp4")},
                data={"code": "test_video"},
            )

            assert response.status_code == 400
            data = response.json()
            assert data["detail"] == "Invalid video file"

    def test_save_video_unauthorized(self, client):
        """Test unauthorized access to save video."""
        video_content = b"fake video content"
        response = client.post(
            f"{settings.API_V1_STR}/video",
            files={"file": ("test_video.mp4", video_content, "video/mp4")},
            data={"code": "test_video"},
        )
        assert response.status_code == 403

    def test_save_video_invalid_file_type(self, client, auth_headers):
        """Test video creation with invalid file type."""
        # Create a mock text file instead of video
        text_content = b"this is not a video"

        response = client.post(
            f"{settings.API_V1_STR}/video",
            headers=auth_headers,
            files={"file": ("test.txt", text_content, "text/plain")},
            data={"code": "test_video"},
        )

        assert response.status_code == 400
        data = response.json()
        assert "File must be a video" in data["detail"]

    def test_save_video_missing_file(self, client, auth_headers):
        """Test video creation with missing file."""
        response = client.post(
            f"{settings.API_V1_STR}/video",
            headers=auth_headers,
            data={"code": "test_video"},
        )
        assert response.status_code == 422  # Validation error

    def test_save_video_missing_code(self, client, auth_headers):
        """Test video creation with missing code."""
        video_content = b"fake video content"
        response = client.post(
            f"{settings.API_V1_STR}/video",
            headers=auth_headers,
            files={"file": ("test_video.mp4", video_content, "video/mp4")},
        )
        assert response.status_code == 422  # Validation error

    def test_get_video_thumbnail_success(self, client, auth_headers):
        """Test successful retrieval of video thumbnail."""
        with patch("app.business.video.VideoManager.get_video_thumbnail") as mock_get_thumbnail:
            mock_get_thumbnail.return_value = b"fake thumbnail data"

            response = client.get(
                f"{settings.API_V1_STR}/video/f50ec0b7-f960-400d-91f0-c42a6d44e3d0/thumbnail",
                headers=auth_headers,
            )

            assert response.status_code == 200
            assert response.content == b"fake thumbnail data"
            assert response.headers["content-type"] == "image/jpeg"
            assert (
                "inline; filename=thumbnail_f50ec0b7-f960-400d-91f0-c42a6d44e3d0.jpg"
                in response.headers["content-disposition"]
            )

    def test_get_video_thumbnail_not_found(self, client, auth_headers):
        """Test video thumbnail not found."""
        with patch("app.business.video.VideoManager.get_video_thumbnail") as mock_get_thumbnail:
            mock_get_thumbnail.side_effect = HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Thumbnail not found in S3"
            )

            response = client.get(
                f"{settings.API_V1_STR}/video/f50ec0b7-f960-400d-91f0-c42a6d44e3d0/thumbnail",
                headers=auth_headers,
            )

            assert response.status_code == 404
            data = response.json()
            assert data["detail"] == "Thumbnail not found in S3"

    def test_get_video_thumbnail_video_not_found(self, client, auth_headers):
        """Test video thumbnail when video not found."""
        with patch("app.business.video.VideoManager.get_video_thumbnail") as mock_get_thumbnail:
            mock_get_thumbnail.side_effect = HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Video f50ec0b7-f960-400d-91f0-c42a6d44e3d0 not found"
            )

            response = client.get(
                f"{settings.API_V1_STR}/video/f50ec0b7-f960-400d-91f0-c42a6d44e3d0/thumbnail",
                headers=auth_headers,
            )

            assert response.status_code == 404
            data = response.json()
            assert data["detail"] == "Video f50ec0b7-f960-400d-91f0-c42a6d44e3d0 not found"

    def test_get_video_thumbnail_unauthorized(self, client):
        """Test unauthorized access to get video thumbnail."""
        response = client.get(f"{settings.API_V1_STR}/video/f50ec0b7-f960-400d-91f0-c42a6d44e3d0/thumbnail")
        assert response.status_code == 403

    def test_get_video_bytes_success(self, client, auth_headers):
        """Test successful retrieval of video bytes."""
        with patch("app.business.video.VideoManager.get_video_bytes") as mock_get_bytes:
            mock_get_bytes.return_value = (b"fake video content", "video/mp4")

            response = client.get(
                f"{settings.API_V1_STR}/video/f50ec0b7-f960-400d-91f0-c42a6d44e3d0/bytes",
                headers=auth_headers,
            )

            assert response.status_code == 200
            assert response.content == b"fake video content"
            assert response.headers["content-type"] == "video/mp4"
            assert (
                "inline; filename=video_f50ec0b7-f960-400d-91f0-c42a6d44e3d0.mp4"
                in response.headers["content-disposition"]
            )

    def test_get_video_bytes_not_found(self, client, auth_headers):
        """Test video bytes not found."""
        with patch("app.business.video.VideoManager.get_video_bytes") as mock_get_bytes:
            mock_get_bytes.side_effect = HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Video not found in S3"
            )

            response = client.get(
                f"{settings.API_V1_STR}/video/f50ec0b7-f960-400d-91f0-c42a6d44e3d0/bytes",
                headers=auth_headers,
            )

            assert response.status_code == 404
            data = response.json()
            assert data["detail"] == "Video not found in S3"

    def test_get_video_bytes_video_not_found(self, client, auth_headers):
        """Test video bytes when video not found."""
        with patch("app.business.video.VideoManager.get_video_bytes") as mock_get_bytes:
            mock_get_bytes.side_effect = HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Video f50ec0b7-f960-400d-91f0-c42a6d44e3d0 not found"
            )

            response = client.get(
                f"{settings.API_V1_STR}/video/f50ec0b7-f960-400d-91f0-c42a6d44e3d0/bytes",
                headers=auth_headers,
            )

            assert response.status_code == 404
            data = response.json()
            assert data["detail"] == "Video f50ec0b7-f960-400d-91f0-c42a6d44e3d0 not found"

    def test_get_video_bytes_unauthorized(self, client):
        """Test unauthorized access to get video bytes."""
        response = client.get(f"{settings.API_V1_STR}/video/f50ec0b7-f960-400d-91f0-c42a6d44e3d0/bytes")
        assert response.status_code == 403
