from unittest.mock import patch

import pytest
from fastapi import HTTPException, status
from fastapi.testclient import TestClient

from app.core.config import settings
from app.main import app
from app.schemas.entity_media_gallery import (
    EntityMediaGallery,
    EntityMediaGalleryCreate,
    EntityMediaGalleryUpdate,
)


@pytest.fixture
def client():
    return TestClient(app)


@pytest.fixture
def auth_headers():
    return {settings.AUTH_HEADER_KEY: settings.AUTH_SECRET_KEY}


# Sample data for testing
entity_media_gallery_data = [
    EntityMediaGallery(
        id=1,
        uuid="f50ec0b7-f960-400d-91f0-c42a6d44e3d0",
        entity_id=100,
        path="s3://bucket/images/real_madrid_logo.jpg",
        embedding=None,
        enabled=True,
        has_embedding=False,
        created_at="2024-01-01T00:00:00Z",
        created_by="test_user",
        updated_at="2024-01-01T00:00:00Z",
        updated_by="test_user",
    ),
    EntityMediaGallery(
        id=2,
        uuid="s50ec0b7-f960-400d-91f0-c42a6d44e3d1",
        entity_id=101,
        path="s3://bucket/images/barcelona_logo.jpg",
        embedding=None,
        enabled=True,
        has_embedding=False,
        created_at="2024-01-01T00:00:00Z",
        created_by="test_user",
        updated_at="2024-01-01T00:00:00Z",
        updated_by="test_user",
    ),
    EntityMediaGallery(
        id=3,
        uuid="t50ec0b7-f960-400d-91f0-c42a6d44e3d2",
        entity_id=102,
        path="s3://bucket/images/man_utd_logo.jpg",
        embedding=None,
        enabled=False,
        has_embedding=False,
        created_at="2024-01-01T00:00:00Z",
        created_by="test_user",
        updated_at="2024-01-01T00:00:00Z",
        updated_by="test_user",
    ),
]

entity_media_gallery_create_data = EntityMediaGalleryCreate(
    uuid="test-uuid-123",
    entity_id=100,
    path="s3://bucket/images/test_logo.jpg",
    embedding=None,
    enabled=True,
)

entity_media_gallery_update_data = EntityMediaGalleryUpdate(
    path="s3://bucket/images/updated_logo.jpg",
    enabled=False,
)


class TestEntityMediaGalleryEndpoints:
    """Test cases for entity media gallery API endpoints."""

    def test_get_all_entity_media_galleries_success(self, client, auth_headers):
        """Test successful retrieval of all entity media galleries."""
        with patch(
            "app.business.entity_media_gallery.EntityMediaGalleryManager.get_all_entity_media_galleries"
        ) as mock_get_all:
            mock_get_all.return_value = entity_media_gallery_data

            response = client.get(f"{settings.API_V1_STR}/entity-media-gallery", headers=auth_headers)

            assert response.status_code == 200
            data = response.json()
            assert len(data) == 3
            assert data[0]["path"] == "s3://bucket/images/real_madrid_logo.jpg"
            assert data[1]["path"] == "s3://bucket/images/barcelona_logo.jpg"
            assert data[2]["path"] == "s3://bucket/images/man_utd_logo.jpg"
            mock_get_all.assert_called_once()

    def test_get_all_entity_media_galleries_unauthorized(self, client):
        """Test unauthorized access to get all entity media galleries."""
        response = client.get(f"{settings.API_V1_STR}/entity-media-gallery")
        assert response.status_code == 403

    def test_get_entity_media_gallery_by_uuid_success(self, client, auth_headers):
        """Test successful retrieval of entity media gallery by UUID."""
        with patch(
            "app.business.entity_media_gallery.EntityMediaGalleryManager.get_entity_media_gallery_by_uuid"
        ) as mock_get_gallery:
            mock_get_gallery.return_value = entity_media_gallery_data[0]

            response = client.get(
                f"{settings.API_V1_STR}/entity-media-gallery/f50ec0b7-f960-400d-91f0-c42a6d44e3d0", headers=auth_headers
            )

            assert response.status_code == 200
            data = response.json()
            assert data["uuid"] == "f50ec0b7-f960-400d-91f0-c42a6d44e3d0"
            assert data["path"] == "s3://bucket/images/real_madrid_logo.jpg"
            assert data["entity_id"] == 100
            assert data["enabled"] is True
            assert data["has_embedding"] is False
            mock_get_gallery.assert_called_once_with(media_gallery_uuid="f50ec0b7-f960-400d-91f0-c42a6d44e3d0")

    def test_get_entity_media_gallery_by_uuid_not_found(self, client, auth_headers):
        """Test entity media gallery not found by UUID."""
        with patch(
            "app.business.entity_media_gallery.EntityMediaGalleryManager.get_entity_media_gallery_by_uuid"
        ) as mock_get_gallery:
            mock_get_gallery.side_effect = HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Entity media gallery f50ec0b7-f960-400d-91f0-c42a6d44e3d1 not found",
            )

            response = client.get(
                f"{settings.API_V1_STR}/entity-media-gallery/f50ec0b7-f960-400d-91f0-c42a6d44e3d1", headers=auth_headers
            )

            assert response.status_code == 404
            data = response.json()
            assert data["detail"] == "Entity media gallery f50ec0b7-f960-400d-91f0-c42a6d44e3d1 not found"

    def test_get_entity_media_gallery_by_uuid_unauthorized(self, client):
        """Test unauthorized access to get entity media gallery by UUID."""
        response = client.get(f"{settings.API_V1_STR}/entity-media-gallery/f50ec0b7-f960-400d-91f0-c42a6d44e3d0")
        assert response.status_code == 403

    def test_get_entity_media_galleries_by_entity_id_success(self, client, auth_headers):
        """Test successful retrieval of entity media galleries by entity ID."""
        with patch(
            "app.business.entity_media_gallery.EntityMediaGalleryManager.get_entity_media_galleries_by_entity_id"
        ) as mock_get_by_entity:
            # Return only enabled galleries for entity_id 100
            mock_get_by_entity.return_value = [entity_media_gallery_data[0]]

            response = client.get(f"{settings.API_V1_STR}/entity-media-gallery/by-entity/100", headers=auth_headers)

            assert response.status_code == 200
            data = response.json()
            assert len(data) == 1
            assert data[0]["path"] == "s3://bucket/images/real_madrid_logo.jpg"
            assert data[0]["entity_id"] == 100
            mock_get_by_entity.assert_called_once_with(entity_id=100)

    def test_get_entity_media_galleries_by_entity_id_not_found(self, client, auth_headers):
        """Test entity media galleries by entity ID when entity doesn't exist."""
        with patch(
            "app.business.entity_media_gallery.EntityMediaGalleryManager.get_entity_media_galleries_by_entity_id"
        ) as mock_get_by_entity:
            mock_get_by_entity.side_effect = HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Entity 999 not found"
            )

            response = client.get(f"{settings.API_V1_STR}/entity-media-gallery/by-entity/999", headers=auth_headers)

            assert response.status_code == 404
            data = response.json()
            assert data["detail"] == "Entity 999 not found"

    def test_get_entity_media_galleries_by_entity_id_unauthorized(self, client):
        """Test unauthorized access to get entity media galleries by entity ID."""
        response = client.get(f"{settings.API_V1_STR}/entity-media-gallery/by-entity/100")
        assert response.status_code == 403

    def test_save_entity_media_gallery_success(self, client, auth_headers):
        """Test successful entity media gallery creation."""
        with patch(
            "app.business.entity_media_gallery.EntityMediaGalleryManager.save_entity_media_gallery"
        ) as mock_save:
            mock_save.return_value = entity_media_gallery_data[0]

            response = client.post(
                f"{settings.API_V1_STR}/entity-media-gallery",
                headers=auth_headers,
                json={
                    "uuid": "test-uuid-123",
                    "entity_id": 100,
                    "path": "s3://bucket/images/test_logo.jpg",
                    "embedding": None,
                    "enabled": True,
                },
            )

            assert response.status_code == 200
            data = response.json()
            assert data["path"] == "s3://bucket/images/real_madrid_logo.jpg"
            mock_save.assert_called_once()

    def test_save_entity_media_gallery_s3_not_exists(self, client, auth_headers):
        """Test entity media gallery creation with non-existent S3 path."""
        with patch(
            "app.business.entity_media_gallery.EntityMediaGalleryManager.save_entity_media_gallery"
        ) as mock_save:
            mock_save.side_effect = HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="media gallery s3://bucket/images/nonexistent.jpg not exists",
            )

            response = client.post(
                f"{settings.API_V1_STR}/entity-media-gallery",
                headers=auth_headers,
                json={
                    "uuid": "test-uuid-123",
                    "entity_id": 100,
                    "path": "s3://bucket/images/nonexistent.jpg",
                    "embedding": None,
                    "enabled": True,
                },
            )

            assert response.status_code == 400
            data = response.json()
            assert data["detail"] == "media gallery s3://bucket/images/nonexistent.jpg not exists"

    def test_save_entity_media_gallery_entity_not_found(self, client, auth_headers):
        """Test entity media gallery creation with non-existent entity_id."""
        with patch(
            "app.business.entity_media_gallery.EntityMediaGalleryManager.save_entity_media_gallery"
        ) as mock_save:
            mock_save.side_effect = HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Entity 999 not found")

            response = client.post(
                f"{settings.API_V1_STR}/entity-media-gallery",
                headers=auth_headers,
                json={
                    "uuid": "test-uuid-123",
                    "entity_id": 999,
                    "path": "s3://bucket/images/test_logo.jpg",
                    "embedding": None,
                    "enabled": True,
                },
            )

            assert response.status_code == 404
            data = response.json()
            assert data["detail"] == "Entity 999 not found"

    def test_save_entity_media_gallery_unauthorized(self, client):
        """Test unauthorized access to save entity media gallery."""
        response = client.post(
            f"{settings.API_V1_STR}/entity-media-gallery",
            json={
                "uuid": "test-uuid-123",
                "entity_id": 100,
                "path": "s3://bucket/images/test_logo.jpg",
                "embedding": None,
                "enabled": True,
            },
        )
        assert response.status_code == 403

    def test_save_entity_media_gallery_invalid_data(self, client, auth_headers):
        """Test entity media gallery creation with invalid data."""
        response = client.post(
            f"{settings.API_V1_STR}/entity-media-gallery",
            headers=auth_headers,
            json={
                "uuid": "test-uuid-123",
                # Missing required fields
            },
        )
        assert response.status_code == 422  # Validation error

    def test_update_entity_media_gallery_success(self, client, auth_headers):
        """Test successful entity media gallery update."""
        with patch(
            "app.business.entity_media_gallery.EntityMediaGalleryManager.update_entity_media_gallery_by_uuid"
        ) as mock_update:
            updated_gallery = EntityMediaGallery(
                id=1,
                uuid="f50ec0b7-f960-400d-91f0-c42a6d44e3d0",
                entity_id=100,
                path="s3://bucket/images/updated_real_madrid_logo.jpg",
                embedding=None,
                enabled=False,
                has_embedding=False,
                created_at="2024-01-01T00:00:00Z",
                created_by="test_user",
                updated_at="2024-01-01T00:00:00Z",
                updated_by="test_user",
            )
            mock_update.return_value = updated_gallery

            response = client.put(
                f"{settings.API_V1_STR}/entity-media-gallery/f50ec0b7-f960-400d-91f0-c42a6d44e3d0",
                headers=auth_headers,
                json={
                    "path": "s3://bucket/images/updated_real_madrid_logo.jpg",
                    "enabled": False,
                },
            )

            assert response.status_code == 200
            data = response.json()
            assert data["path"] == "s3://bucket/images/updated_real_madrid_logo.jpg"
            assert data["enabled"] is False
            mock_update.assert_called_once()

    def test_update_entity_media_gallery_not_found(self, client, auth_headers):
        """Test entity media gallery update with non-existent UUID."""
        with patch(
            "app.business.entity_media_gallery.EntityMediaGalleryManager.update_entity_media_gallery_by_uuid"
        ) as mock_update:
            mock_update.side_effect = HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Entity media gallery f50ec0b7-f960-400d-91f0-c42a6d44e3d1 not found",
            )

            response = client.put(
                f"{settings.API_V1_STR}/entity-media-gallery/f50ec0b7-f960-400d-91f0-c42a6d44e3d1",
                headers=auth_headers,
                json={
                    "path": "s3://bucket/images/updated_logo.jpg",
                    "enabled": True,
                },
            )

            assert response.status_code == 404
            data = response.json()
            assert data["detail"] == "Entity media gallery f50ec0b7-f960-400d-91f0-c42a6d44e3d1 not found"

    def test_update_entity_media_gallery_unauthorized(self, client):
        """Test unauthorized access to update entity media gallery."""
        response = client.put(
            f"{settings.API_V1_STR}/entity-media-gallery/f50ec0b7-f960-400d-91f0-c42a6d44e3d0",
            json={
                "path": "s3://bucket/images/updated_logo.jpg",
                "enabled": True,
            },
        )
        assert response.status_code == 403

    def test_update_entity_media_gallery_partial_data(self, client, auth_headers):
        """Test entity media gallery update with partial data."""
        with patch(
            "app.business.entity_media_gallery.EntityMediaGalleryManager.update_entity_media_gallery_by_uuid"
        ) as mock_update:
            updated_gallery = EntityMediaGallery(
                id=1,
                uuid="f50ec0b7-f960-400d-91f0-c42a6d44e3d0",
                entity_id=100,
                path="s3://bucket/images/real_madrid_logo.jpg",
                embedding=None,
                enabled=False,  # Only this field updated
                has_embedding=False,
                created_at="2024-01-01T00:00:00Z",
                created_by="test_user",
                updated_at="2024-01-01T00:00:00Z",
                updated_by="test_user",
            )
            mock_update.return_value = updated_gallery

            response = client.put(
                f"{settings.API_V1_STR}/entity-media-gallery/f50ec0b7-f960-400d-91f0-c42a6d44e3d0",
                headers=auth_headers,
                json={
                    "enabled": False,  # Only update enabled field
                },
            )

            assert response.status_code == 200
            data = response.json()
            assert data["enabled"] is False
            assert data["path"] == "s3://bucket/images/real_madrid_logo.jpg"  # Unchanged
            mock_update.assert_called_once()

    def test_delete_entity_media_gallery_success(self, client, auth_headers):
        """Test successful entity media gallery deletion."""
        with patch(
            "app.business.entity_media_gallery.EntityMediaGalleryManager.delete_entity_media_gallery_by_uuid"
        ) as mock_delete:
            mock_delete.return_value = None

            response = client.delete(
                f"{settings.API_V1_STR}/entity-media-gallery/f50ec0b7-f960-400d-91f0-c42a6d44e3d0", headers=auth_headers
            )

            assert response.status_code == 200
            mock_delete.assert_called_once_with(media_gallery_uuid="f50ec0b7-f960-400d-91f0-c42a6d44e3d0")

    def test_delete_entity_media_gallery_unauthorized(self, client):
        """Test unauthorized access to delete entity media gallery."""
        response = client.delete(f"{settings.API_V1_STR}/entity-media-gallery/f50ec0b7-f960-400d-91f0-c42a6d44e3d0")
        assert response.status_code == 403

    def test_entity_media_gallery_endpoints_without_auth_header(self, client):
        """Test all entity media gallery endpoints without authentication header."""
        endpoints = [
            ("GET", f"{settings.API_V1_STR}/entity-media-gallery"),
            ("GET", f"{settings.API_V1_STR}/entity-media-gallery/f50ec0b7-f960-400d-91f0-c42a6d44e3d0"),
            ("GET", f"{settings.API_V1_STR}/entity-media-gallery/by-entity/100"),
            ("POST", f"{settings.API_V1_STR}/entity-media-gallery"),
            ("PUT", f"{settings.API_V1_STR}/entity-media-gallery/f50ec0b7-f960-400d-91f0-c42a6d44e3d0"),
            ("DELETE", f"{settings.API_V1_STR}/entity-media-gallery/f50ec0b7-f960-400d-91f0-c42a6d44e3d0"),
        ]

        for method, url in endpoints:
            if method == "GET":
                response = client.get(url)
            elif method == "POST":
                response = client.post(url, json={"entity_id": 100, "path": "s3://bucket/test.jpg"})
            elif method == "PUT":
                response = client.put(url, json={"path": "s3://bucket/test.jpg"})
            elif method == "DELETE":
                response = client.delete(url)

            assert response.status_code == 403

    def test_entity_media_gallery_endpoints_with_invalid_auth(self, client):
        """Test all entity media gallery endpoints with invalid authentication."""
        invalid_headers = {settings.AUTH_HEADER_KEY: "invalid_token"}

        endpoints = [
            ("GET", f"{settings.API_V1_STR}/entity-media-gallery"),
            ("GET", f"{settings.API_V1_STR}/entity-media-gallery/f50ec0b7-f960-400d-91f0-c42a6d44e3d0"),
            ("GET", f"{settings.API_V1_STR}/entity-media-gallery/by-entity/100"),
            ("POST", f"{settings.API_V1_STR}/entity-media-gallery"),
            ("PUT", f"{settings.API_V1_STR}/entity-media-gallery/f50ec0b7-f960-400d-91f0-c42a6d44e3d0"),
            ("DELETE", f"{settings.API_V1_STR}/entity-media-gallery/f50ec0b7-f960-400d-91f0-c42a6d44e3d0"),
        ]

        for method, url in endpoints:
            if method == "GET":
                response = client.get(url, headers=invalid_headers)
            elif method == "POST":
                response = client.post(
                    url, headers=invalid_headers, json={"entity_id": 100, "path": "s3://bucket/test.jpg"}
                )
            elif method == "PUT":
                response = client.put(url, headers=invalid_headers, json={"path": "s3://bucket/test.jpg"})
            elif method == "DELETE":
                response = client.delete(url, headers=invalid_headers)

            assert response.status_code == 403

    def test_save_entity_media_gallery_with_file_upload(self, client, auth_headers, tmp_path):
        """Test successful entity media gallery creation with file upload."""
        test_file = tmp_path / "test_image.jpg"
        test_file.write_bytes(b"fake image data")
        with patch(
            "app.business.entity_media_gallery.EntityMediaGalleryManager.save_entity_media_gallery_with_file"
        ) as mock_save:
            mock_save.return_value = entity_media_gallery_data[0]
            with open(test_file, "rb") as f:
                response = client.post(
                    f"{settings.API_V1_STR}/entity-media-gallery",
                    headers=auth_headers,
                    files={"file": ("test_image.jpg", f, "image/jpeg")},
                    data={"entity_id": 100, "uuid": "test-uuid-123", "enabled": True},
                )
            assert response.status_code == 200
            data = response.json()
            assert data["uuid"] == "f50ec0b7-f960-400d-91f0-c42a6d44e3d0"
            assert data["entity_id"] == 100
            assert "test_image.jpg" in data["path"]
            mock_save.assert_called_once()
