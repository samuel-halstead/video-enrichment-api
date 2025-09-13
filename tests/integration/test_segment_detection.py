from unittest.mock import patch

import pytest
from fastapi import HTTPException, status
from fastapi.testclient import TestClient
from video_enrichment_orm.schemas.segment_detection import SegmentDetection

from app.core.config import settings
from app.main import app


@pytest.fixture
def client():
    return TestClient(app)


@pytest.fixture
def auth_headers():
    return {settings.AUTH_HEADER_KEY: settings.AUTH_SECRET_KEY}


# Sample data for testing
segment_detection_data = [
    SegmentDetection(
        id=1,
        uuid="f50ec0b7-f960-400d-91f0-c42a6d44e3d0",
        video_id=100,
        start_frame=100,
        end_frame=150,
        taxonomy_id=200,
        entity_id=300,
        created_at="2024-01-01T00:00:00Z",
        created_by="test_user",
        updated_at="2024-01-01T00:00:00Z",
        updated_by="test_user",
    ),
    SegmentDetection(
        id=2,
        uuid="s50ec0b7-f960-400d-91f0-c42a6d44e3d1",
        video_id=100,
        start_frame=200,
        end_frame=250,
        taxonomy_id=200,
        entity_id=301,
        created_at="2024-01-01T00:00:00Z",
        created_by="test_user",
        updated_at="2024-01-01T00:00:00Z",
        updated_by="test_user",
    ),
    SegmentDetection(
        id=3,
        uuid="t50ec0b7-f960-400d-91f0-c42a6d44e3d2",
        video_id=100,
        start_frame=300,
        end_frame=350,
        taxonomy_id=201,
        entity_id=302,
        created_at="2024-01-01T00:00:00Z",
        created_by="test_user",
        updated_at="2024-01-01T00:00:00Z",
        updated_by="test_user",
    ),
]


class TestSegmentDetectionEndpoints:
    """Test cases for segment detection API endpoints."""

    def test_get_segment_detections_by_video_id_success(self, client, auth_headers):
        """Test successful retrieval of segment detections by video ID."""
        with patch(
            "app.business.segment_detection.SegmentDetectionManager.get_segment_detections_by_video_id"
        ) as mock_get_by_video:
            mock_get_by_video.return_value = segment_detection_data

            response = client.get(f"{settings.API_V1_STR}/segment-detection/by-video/100", headers=auth_headers)

            assert response.status_code == 200
            data = response.json()
            assert len(data) == 3
            assert data[0]["video_id"] == 100
            assert data[0]["start_frame"] == 100
            assert data[0]["end_frame"] == 150
            assert data[0]["taxonomy_id"] == 200
            assert data[0]["entity_id"] == 300
            mock_get_by_video.assert_called_once_with(video_id=100)

    def test_get_segment_detections_by_video_id_video_not_found(self, client, auth_headers):
        """Test segment detections by video ID when video doesn't exist."""
        with patch(
            "app.business.segment_detection.SegmentDetectionManager.get_segment_detections_by_video_id"
        ) as mock_get_by_video:
            mock_get_by_video.side_effect = HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Video 999 not found"
            )

            response = client.get(f"{settings.API_V1_STR}/segment-detection/by-video/999", headers=auth_headers)

            assert response.status_code == 404
            data = response.json()
            assert data["detail"] == "Video 999 not found"

    def test_get_segment_detections_by_video_id_unauthorized(self, client):
        """Test unauthorized access to get segment detections by video ID."""
        response = client.get(f"{settings.API_V1_STR}/segment-detection/by-video/100")
        assert response.status_code == 403

    def test_get_segment_detections_by_video_and_taxonomy_success(self, client, auth_headers):
        """Test successful retrieval of segment detections by video and taxonomy."""
        with patch(
            "app.business.segment_detection.SegmentDetectionManager.get_segment_detections_by_video_and_taxonomy"
        ) as mock_get_by_video_taxonomy:
            # Return only detections for video_id 100 and taxonomy_id 200
            mock_get_by_video_taxonomy.return_value = [segment_detection_data[0], segment_detection_data[1]]

            response = client.get(
                f"{settings.API_V1_STR}/segment-detection/by-video/100/taxonomy/200", headers=auth_headers
            )

            assert response.status_code == 200
            data = response.json()
            assert len(data) == 2
            assert data[0]["video_id"] == 100
            assert data[0]["taxonomy_id"] == 200
            assert data[1]["video_id"] == 100
            assert data[1]["taxonomy_id"] == 200
            mock_get_by_video_taxonomy.assert_called_once_with(video_id=100, taxonomy_id=200)

    def test_get_segment_detections_by_video_and_taxonomy_video_not_found(self, client, auth_headers):
        """Test segment detections by video and taxonomy when video doesn't exist."""
        with patch(
            "app.business.segment_detection.SegmentDetectionManager.get_segment_detections_by_video_and_taxonomy"
        ) as mock_get_by_video_taxonomy:
            mock_get_by_video_taxonomy.side_effect = HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Video 999 not found"
            )

            response = client.get(
                f"{settings.API_V1_STR}/segment-detection/by-video/999/taxonomy/200", headers=auth_headers
            )

            assert response.status_code == 404
            data = response.json()
            assert data["detail"] == "Video 999 not found"

    def test_get_segment_detections_by_video_and_taxonomy_taxonomy_not_found(self, client, auth_headers):
        """Test segment detections by video and taxonomy when taxonomy doesn't exist."""
        with patch(
            "app.business.segment_detection.SegmentDetectionManager.get_segment_detections_by_video_and_taxonomy"
        ) as mock_get_by_video_taxonomy:
            mock_get_by_video_taxonomy.side_effect = HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Taxonomy 999 not found"
            )

            response = client.get(
                f"{settings.API_V1_STR}/segment-detection/by-video/100/taxonomy/999", headers=auth_headers
            )

            assert response.status_code == 404
            data = response.json()
            assert data["detail"] == "Taxonomy 999 not found"

    def test_get_segment_detections_by_video_and_taxonomy_unauthorized(self, client):
        """Test unauthorized access to get segment detections by video and taxonomy."""
        response = client.get(f"{settings.API_V1_STR}/segment-detection/by-video/100/taxonomy/200")
        assert response.status_code == 403

    def test_get_segment_detections_by_video_id_empty_result(self, client, auth_headers):
        """Test segment detections by video ID when no detections exist."""
        with patch(
            "app.business.segment_detection.SegmentDetectionManager.get_segment_detections_by_video_id"
        ) as mock_get_by_video:
            mock_get_by_video.return_value = []

            response = client.get(f"{settings.API_V1_STR}/segment-detection/by-video/100", headers=auth_headers)

            assert response.status_code == 200
            data = response.json()
            assert len(data) == 0
            mock_get_by_video.assert_called_once_with(video_id=100)

    def test_get_segment_detections_by_video_and_taxonomy_empty_result(self, client, auth_headers):
        """Test segment detections by video and taxonomy when no detections exist."""
        with patch(
            "app.business.segment_detection.SegmentDetectionManager.get_segment_detections_by_video_and_taxonomy"
        ) as mock_get_by_video_taxonomy:
            mock_get_by_video_taxonomy.return_value = []

            response = client.get(
                f"{settings.API_V1_STR}/segment-detection/by-video/100/taxonomy/999", headers=auth_headers
            )

            assert response.status_code == 200
            data = response.json()
            assert len(data) == 0
            mock_get_by_video_taxonomy.assert_called_once_with(video_id=100, taxonomy_id=999)

    def test_segment_detection_endpoints_without_auth_header(self, client):
        """Test all segment detection endpoints without authentication header."""
        endpoints = [
            ("GET", f"{settings.API_V1_STR}/segment-detection/by-video/100"),
            ("GET", f"{settings.API_V1_STR}/segment-detection/by-video/100/taxonomy/200"),
        ]

        for method, url in endpoints:
            if method == "GET":
                response = client.get(url)

            assert response.status_code == 403

    def test_segment_detection_endpoints_with_invalid_auth(self, client):
        """Test all segment detection endpoints with invalid authentication."""
        invalid_headers = {settings.AUTH_HEADER_KEY: "invalid_token"}

        endpoints = [
            ("GET", f"{settings.API_V1_STR}/segment-detection/by-video/100"),
            ("GET", f"{settings.API_V1_STR}/segment-detection/by-video/100/taxonomy/200"),
        ]

        for method, url in endpoints:
            if method == "GET":
                response = client.get(url, headers=invalid_headers)

            assert response.status_code == 403

    def test_segment_detection_endpoints_with_invalid_video_id(self, client, auth_headers):
        """Test segment detection endpoints with invalid video ID format."""
        response = client.get(f"{settings.API_V1_STR}/segment-detection/by-video/invalid", headers=auth_headers)
        assert response.status_code == 422  # Validation error for invalid integer

    def test_segment_detection_endpoints_with_invalid_taxonomy_id(self, client, auth_headers):
        """Test segment detection endpoints with invalid taxonomy ID format."""
        response = client.get(
            f"{settings.API_V1_STR}/segment-detection/by-video/100/taxonomy/invalid", headers=auth_headers
        )
        assert response.status_code == 422  # Validation error for invalid integer

    def test_segment_detection_endpoints_with_negative_video_id(self, client, auth_headers):
        """Test segment detection endpoints with negative video ID."""
        with patch(
            "app.business.segment_detection.SegmentDetectionManager.get_segment_detections_by_video_id"
        ) as mock_get_by_video:
            mock_get_by_video.side_effect = HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Video -1 not found"
            )

            response = client.get(f"{settings.API_V1_STR}/segment-detection/by-video/-1", headers=auth_headers)

            assert response.status_code == 404

    def test_segment_detection_endpoints_with_zero_video_id(self, client, auth_headers):
        """Test segment detection endpoints with zero video ID."""
        with patch(
            "app.business.segment_detection.SegmentDetectionManager.get_segment_detections_by_video_id"
        ) as mock_get_by_video:
            mock_get_by_video.side_effect = HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Video 0 not found"
            )

            response = client.get(f"{settings.API_V1_STR}/segment-detection/by-video/0", headers=auth_headers)

            assert response.status_code == 404

    def test_segment_detection_data_structure(self, client, auth_headers):
        """Test that segment detection response has the correct data structure."""
        with patch(
            "app.business.segment_detection.SegmentDetectionManager.get_segment_detections_by_video_id"
        ) as mock_get_by_video:
            mock_get_by_video.return_value = [segment_detection_data[0]]

            response = client.get(f"{settings.API_V1_STR}/segment-detection/by-video/100", headers=auth_headers)

            assert response.status_code == 200
            data = response.json()
            assert len(data) == 1

            detection = data[0]
            required_fields = ["id", "uuid", "video_id", "start_frame", "end_frame", "taxonomy_id", "entity_id"]
            for field in required_fields:
                assert field in detection

            assert detection["id"] == 1
            assert detection["uuid"] == "f50ec0b7-f960-400d-91f0-c42a6d44e3d0"
            assert detection["video_id"] == 100
            assert detection["start_frame"] == 100
            assert detection["end_frame"] == 150
            assert detection["taxonomy_id"] == 200
            assert detection["entity_id"] == 300
