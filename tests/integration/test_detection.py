from unittest.mock import patch

import pytest
from fastapi import HTTPException, status
from fastapi.testclient import TestClient
from video_enrichment_orm.schemas.detection import Detection

from app.core.config import settings
from app.main import app


@pytest.fixture
def client():
    return TestClient(app)


@pytest.fixture
def auth_headers():
    return {settings.AUTH_HEADER_KEY: settings.AUTH_SECRET_KEY}


# Sample data for testing
detection_data = [
    Detection(
        id=1,
        uuid="f50ec0b7-f960-400d-91f0-c42a6d44e3d0",
        video_id=100,
        frame=150,
        segment_detection_id=200,
        detection_score=0.95,
        entity_score=0.88,
        bbox_x_min=0.1,
        bbox_y_min=0.2,
        bbox_x_max=0.8,
        bbox_y_max=0.9,
        created_at="2024-01-01T00:00:00Z",
        created_by="test_user",
        updated_at="2024-01-01T00:00:00Z",
        updated_by="test_user",
    ),
    Detection(
        id=2,
        uuid="s50ec0b7-f960-400d-91f0-c42a6d44e3d1",
        video_id=100,
        frame=160,
        segment_detection_id=200,
        detection_score=0.92,
        entity_score=0.85,
        bbox_x_min=0.15,
        bbox_y_min=0.25,
        bbox_x_max=0.85,
        bbox_y_max=0.95,
        created_at="2024-01-01T00:00:00Z",
        created_by="test_user",
        updated_at="2024-01-01T00:00:00Z",
        updated_by="test_user",
    ),
    Detection(
        id=3,
        uuid="t50ec0b7-f960-400d-91f0-c42a6d44e3d2",
        video_id=100,
        frame=170,
        segment_detection_id=201,
        detection_score=0.87,
        entity_score=0.79,
        bbox_x_min=0.2,
        bbox_y_min=0.3,
        bbox_x_max=0.9,
        bbox_y_max=1.0,
        created_at="2024-01-01T00:00:00Z",
        created_by="test_user",
        updated_at="2024-01-01T00:00:00Z",
        updated_by="test_user",
    ),
]


class TestDetectionEndpoints:
    """Test cases for detection API endpoints."""

    def test_get_detections_by_video_id_success(self, client, auth_headers):
        """Test successful retrieval of detections by video ID."""
        with patch("app.business.detection.DetectionManager.get_detections_by_video_id") as mock_get_by_video:
            mock_get_by_video.return_value = detection_data

            response = client.get(f"{settings.API_V1_STR}/detection/by-video/100", headers=auth_headers)

            assert response.status_code == 200
            data = response.json()
            assert len(data) == 3
            assert data[0]["video_id"] == 100
            assert data[0]["frame"] == 150
            assert data[0]["detection_score"] == 0.95
            assert data[0]["entity_score"] == 0.88
            assert data[0]["bbox_x_min"] == 0.1
            assert data[0]["bbox_y_min"] == 0.2
            assert data[0]["bbox_x_max"] == 0.8
            assert data[0]["bbox_y_max"] == 0.9
            mock_get_by_video.assert_called_once_with(video_id=100)

    def test_get_detections_by_video_id_video_not_found(self, client, auth_headers):
        """Test detections by video ID when video doesn't exist."""
        with patch("app.business.detection.DetectionManager.get_detections_by_video_id") as mock_get_by_video:
            mock_get_by_video.side_effect = HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Video 999 not found"
            )

            response = client.get(f"{settings.API_V1_STR}/detection/by-video/999", headers=auth_headers)

            assert response.status_code == 404
            data = response.json()
            assert data["detail"] == "Video 999 not found"

    def test_get_detections_by_video_id_unauthorized(self, client):
        """Test unauthorized access to get detections by video ID."""
        response = client.get(f"{settings.API_V1_STR}/detection/by-video/100")
        assert response.status_code == 403

    def test_get_detections_by_segment_detection_id_success(self, client, auth_headers):
        """Test successful retrieval of detections by segment detection ID."""
        with patch(
            "app.business.detection.DetectionManager.get_detections_by_segment_detection_id"
        ) as mock_get_by_segment:
            # Return only detections for segment_detection_id 200
            mock_get_by_segment.return_value = [detection_data[0], detection_data[1]]

            response = client.get(f"{settings.API_V1_STR}/detection/by-segment-detection/200", headers=auth_headers)

            assert response.status_code == 200
            data = response.json()
            assert len(data) == 2
            assert data[0]["segment_detection_id"] == 200
            assert data[1]["segment_detection_id"] == 200
            assert data[0]["frame"] == 150
            assert data[1]["frame"] == 160
            mock_get_by_segment.assert_called_once_with(segment_detection_id=200)

    def test_get_detections_by_segment_detection_id_not_found(self, client, auth_headers):
        """Test detections by segment detection ID when segment detection doesn't exist."""
        with patch(
            "app.business.detection.DetectionManager.get_detections_by_segment_detection_id"
        ) as mock_get_by_segment:
            mock_get_by_segment.side_effect = HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Segment detection 999 not found"
            )

            response = client.get(f"{settings.API_V1_STR}/detection/by-segment-detection/999", headers=auth_headers)

            assert response.status_code == 404
            data = response.json()
            assert data["detail"] == "Segment detection 999 not found"

    def test_get_detections_by_segment_detection_id_unauthorized(self, client):
        """Test unauthorized access to get detections by segment detection ID."""
        response = client.get(f"{settings.API_V1_STR}/detection/by-segment-detection/200")
        assert response.status_code == 403

    def test_get_detections_by_video_id_empty_result(self, client, auth_headers):
        """Test detections by video ID when no detections exist."""
        with patch("app.business.detection.DetectionManager.get_detections_by_video_id") as mock_get_by_video:
            mock_get_by_video.return_value = []

            response = client.get(f"{settings.API_V1_STR}/detection/by-video/100", headers=auth_headers)

            assert response.status_code == 200
            data = response.json()
            assert len(data) == 0
            mock_get_by_video.assert_called_once_with(video_id=100)

    def test_get_detections_by_segment_detection_id_empty_result(self, client, auth_headers):
        """Test detections by segment detection ID when no detections exist."""
        with patch(
            "app.business.detection.DetectionManager.get_detections_by_segment_detection_id"
        ) as mock_get_by_segment:
            mock_get_by_segment.return_value = []

            response = client.get(f"{settings.API_V1_STR}/detection/by-segment-detection/200", headers=auth_headers)

            assert response.status_code == 200
            data = response.json()
            assert len(data) == 0
            mock_get_by_segment.assert_called_once_with(segment_detection_id=200)

    def test_detection_endpoints_without_auth_header(self, client):
        """Test all detection endpoints without authentication header."""
        endpoints = [
            ("GET", f"{settings.API_V1_STR}/detection/by-video/100"),
            ("GET", f"{settings.API_V1_STR}/detection/by-segment-detection/200"),
        ]

        for method, url in endpoints:
            if method == "GET":
                response = client.get(url)

            assert response.status_code == 403

    def test_detection_endpoints_with_invalid_auth(self, client):
        """Test all detection endpoints with invalid authentication."""
        invalid_headers = {settings.AUTH_HEADER_KEY: "invalid_token"}

        endpoints = [
            ("GET", f"{settings.API_V1_STR}/detection/by-video/100"),
            ("GET", f"{settings.API_V1_STR}/detection/by-segment-detection/200"),
        ]

        for method, url in endpoints:
            if method == "GET":
                response = client.get(url, headers=invalid_headers)

            assert response.status_code == 403

    def test_detection_endpoints_with_invalid_video_id(self, client, auth_headers):
        """Test detection endpoints with invalid video ID format."""
        response = client.get(f"{settings.API_V1_STR}/detection/by-video/invalid", headers=auth_headers)
        assert response.status_code == 422  # Validation error for invalid integer

    def test_detection_endpoints_with_invalid_segment_detection_id(self, client, auth_headers):
        """Test detection endpoints with invalid segment detection ID format."""
        response = client.get(f"{settings.API_V1_STR}/detection/by-segment-detection/invalid", headers=auth_headers)
        assert response.status_code == 422  # Validation error for invalid integer

    def test_detection_endpoints_with_negative_video_id(self, client, auth_headers):
        """Test detection endpoints with negative video ID."""
        with patch("app.business.detection.DetectionManager.get_detections_by_video_id") as mock_get_by_video:
            mock_get_by_video.side_effect = HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Video -1 not found"
            )

            response = client.get(f"{settings.API_V1_STR}/detection/by-video/-1", headers=auth_headers)

            assert response.status_code == 404

    def test_detection_endpoints_with_zero_video_id(self, client, auth_headers):
        """Test detection endpoints with zero video ID."""
        with patch("app.business.detection.DetectionManager.get_detections_by_video_id") as mock_get_by_video:
            mock_get_by_video.side_effect = HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Video 0 not found"
            )

            response = client.get(f"{settings.API_V1_STR}/detection/by-video/0", headers=auth_headers)

            assert response.status_code == 404

    def test_detection_endpoints_with_negative_segment_detection_id(self, client, auth_headers):
        """Test detection endpoints with negative segment detection ID."""
        with patch(
            "app.business.detection.DetectionManager.get_detections_by_segment_detection_id"
        ) as mock_get_by_segment:
            mock_get_by_segment.side_effect = HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Segment detection -1 not found"
            )

            response = client.get(f"{settings.API_V1_STR}/detection/by-segment-detection/-1", headers=auth_headers)

            assert response.status_code == 404

    def test_detection_endpoints_with_zero_segment_detection_id(self, client, auth_headers):
        """Test detection endpoints with zero segment detection ID."""
        with patch(
            "app.business.detection.DetectionManager.get_detections_by_segment_detection_id"
        ) as mock_get_by_segment:
            mock_get_by_segment.side_effect = HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Segment detection 0 not found"
            )

            response = client.get(f"{settings.API_V1_STR}/detection/by-segment-detection/0", headers=auth_headers)

            assert response.status_code == 404

    def test_detection_data_structure(self, client, auth_headers):
        """Test that detection response has the correct data structure."""
        with patch("app.business.detection.DetectionManager.get_detections_by_video_id") as mock_get_by_video:
            mock_get_by_video.return_value = [detection_data[0]]

            response = client.get(f"{settings.API_V1_STR}/detection/by-video/100", headers=auth_headers)

            assert response.status_code == 200
            data = response.json()
            assert len(data) == 1

            detection = data[0]
            required_fields = [
                "id",
                "uuid",
                "video_id",
                "frame",
                "segment_detection_id",
                "detection_score",
                "entity_score",
                "bbox_x_min",
                "bbox_y_min",
                "bbox_x_max",
                "bbox_y_max",
            ]
            for field in required_fields:
                assert field in detection

            assert detection["id"] == 1
            assert detection["uuid"] == "f50ec0b7-f960-400d-91f0-c42a6d44e3d0"
            assert detection["video_id"] == 100
            assert detection["frame"] == 150
            assert detection["segment_detection_id"] == 200
            assert detection["detection_score"] == 0.95
            assert detection["entity_score"] == 0.88
            assert detection["bbox_x_min"] == 0.1
            assert detection["bbox_y_min"] == 0.2
            assert detection["bbox_x_max"] == 0.8
            assert detection["bbox_y_max"] == 0.9

    def test_detection_score_validation(self, client, auth_headers):
        """Test that detection scores are properly validated in response."""
        with patch("app.business.detection.DetectionManager.get_detections_by_video_id") as mock_get_by_video:
            mock_get_by_video.return_value = detection_data

            response = client.get(f"{settings.API_V1_STR}/detection/by-video/100", headers=auth_headers)

            assert response.status_code == 200
            data = response.json()

            # Check that scores are within valid range (0.0 to 1.0)
            for detection in data:
                assert 0.0 <= detection["detection_score"] <= 1.0
                assert 0.0 <= detection["entity_score"] <= 1.0

    def test_detection_bbox_validation(self, client, auth_headers):
        """Test that bounding box coordinates are properly validated in response."""
        with patch("app.business.detection.DetectionManager.get_detections_by_video_id") as mock_get_by_video:
            mock_get_by_video.return_value = detection_data

            response = client.get(f"{settings.API_V1_STR}/detection/by-video/100", headers=auth_headers)

            assert response.status_code == 200
            data = response.json()

            # Check that bounding box coordinates are valid
            for detection in data:
                assert detection["bbox_x_min"] < detection["bbox_x_max"]
                assert detection["bbox_y_min"] < detection["bbox_y_max"]
                assert 0.0 <= detection["bbox_x_min"] <= 1.0
                assert 0.0 <= detection["bbox_y_min"] <= 1.0
                assert 0.0 <= detection["bbox_x_max"] <= 1.0
                assert 0.0 <= detection["bbox_y_max"] <= 1.0
