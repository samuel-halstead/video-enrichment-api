from unittest.mock import patch

import pytest
from fastapi import HTTPException, status
from fastapi.testclient import TestClient
from video_enrichment_orm.schemas.taxonomy import (
    Taxonomy,
    TaxonomyCreate,
    TaxonomyUpdate,
)

from app.core.config import settings
from app.main import app


@pytest.fixture
def client():
    return TestClient(app)


@pytest.fixture
def auth_headers():
    return {settings.AUTH_HEADER_KEY: settings.AUTH_SECRET_KEY}


# Sample data for testing
taxonomy_data = [
    Taxonomy(
        id=1,
        uuid="f50ec0b7-f960-400d-91f0-c42a6d44e3d0",
        label="Sports",
        taxonomy_id=100,
        created_at="2024-01-01T00:00:00Z",
        created_by="test_user",
        updated_at="2024-01-01T00:00:00Z",
        updated_by="test_user",
    ),
    Taxonomy(
        id=2,
        uuid="s50ec0b7-f960-400d-91f0-c42a6d44e3d1",
        label="News",
        taxonomy_id=200,
        created_at="2024-01-01T00:00:00Z",
        created_by="test_user",
        updated_at="2024-01-01T00:00:00Z",
        updated_by="test_user",
    ),
]

taxonomy_create_data = TaxonomyCreate(
    uuid="test-uuid-123",
    label="Test Taxonomy",
    taxonomy_id=300,
)

taxonomy_update_data = TaxonomyUpdate(
    label="Updated Taxonomy Label",
)


class TestTaxonomyEndpoints:
    """Test cases for taxonomy API endpoints."""

    def test_get_all_taxonomies_success(self, client, auth_headers):
        """Test successful retrieval of all taxonomies."""
        with patch("app.business.taxonomy.TaxonomyManager.get_all_taxonomies") as mock_get_all:
            mock_get_all.return_value = taxonomy_data

            response = client.get(f"{settings.API_V1_STR}/taxonomy", headers=auth_headers)

            assert response.status_code == 200
            data = response.json()
            assert len(data) == 2
            assert data[0]["label"] == "Sports"
            assert data[1]["label"] == "News"
            mock_get_all.assert_called_once()

    def test_get_all_taxonomies_unauthorized(self, client):
        """Test unauthorized access to get all taxonomies."""
        response = client.get(f"{settings.API_V1_STR}/taxonomy")
        assert response.status_code == 403

    def test_get_taxonomy_by_uuid_success(self, client, auth_headers):
        """Test successful retrieval of taxonomy by UUID."""
        with patch("app.business.taxonomy.TaxonomyManager.get_taxonomy_by_uuid") as mock_get_taxonomy:
            mock_get_taxonomy.return_value = taxonomy_data[0]

            response = client.get(
                f"{settings.API_V1_STR}/taxonomy/f50ec0b7-f960-400d-91f0-c42a6d44e3d0", headers=auth_headers
            )

            assert response.status_code == 200
            data = response.json()
            assert data["uuid"] == "f50ec0b7-f960-400d-91f0-c42a6d44e3d0"
            assert data["label"] == "Sports"
            assert data["taxonomy_id"] == 100
            mock_get_taxonomy.assert_called_once_with(taxonomy_uuid="f50ec0b7-f960-400d-91f0-c42a6d44e3d0")

    def test_get_taxonomy_by_uuid_not_found(self, client, auth_headers):
        """Test taxonomy not found by UUID."""
        with patch("app.business.taxonomy.TaxonomyManager.get_taxonomy_by_uuid") as mock_get_taxonomy:
            mock_get_taxonomy.side_effect = HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Taxonomy f50ec0b7-f960-400d-91f0-c42a6d44e3d1 not found"
            )

            response = client.get(
                f"{settings.API_V1_STR}/taxonomy/f50ec0b7-f960-400d-91f0-c42a6d44e3d1", headers=auth_headers
            )

            assert response.status_code == 404
            data = response.json()
            assert data["detail"] == "Taxonomy f50ec0b7-f960-400d-91f0-c42a6d44e3d1 not found"

    def test_get_taxonomy_by_uuid_unauthorized(self, client):
        """Test unauthorized access to get taxonomy by UUID."""
        response = client.get(f"{settings.API_V1_STR}/taxonomy/f50ec0b7-f960-400d-91f0-c42a6d44e3d0")
        assert response.status_code == 403

    def test_save_taxonomy_success(self, client, auth_headers):
        """Test successful taxonomy creation."""
        with patch("app.business.taxonomy.TaxonomyManager.save_taxonomy") as mock_save:
            mock_save.return_value = taxonomy_data[0]

            response = client.post(
                f"{settings.API_V1_STR}/taxonomy",
                headers=auth_headers,
                json={
                    "uuid": "test-uuid-123",
                    "label": "Test Taxonomy",
                    "taxonomy_id": 300,
                },
            )

            assert response.status_code == 200
            data = response.json()
            assert data["label"] == "Sports"
            mock_save.assert_called_once()

    def test_save_taxonomy_not_found(self, client, auth_headers):
        """Test taxonomy creation with non-existent taxonomy_id."""
        with patch("app.business.taxonomy.TaxonomyManager.save_taxonomy") as mock_save:
            mock_save.side_effect = HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Taxonomy with id 999 not found"
            )

            response = client.post(
                f"{settings.API_V1_STR}/taxonomy",
                headers=auth_headers,
                json={
                    "uuid": "test-uuid-123",
                    "label": "Test Taxonomy",
                    "taxonomy_id": 999,
                },
            )

            assert response.status_code == 404
            data = response.json()
            assert data["detail"] == "Taxonomy with id 999 not found"

    def test_save_taxonomy_unauthorized(self, client):
        """Test unauthorized access to save taxonomy."""
        response = client.post(
            f"{settings.API_V1_STR}/taxonomy",
            json={
                "uuid": "test-uuid-123",
                "label": "Test Taxonomy",
                "taxonomy_id": 300,
            },
        )
        assert response.status_code == 403

    def test_save_taxonomy_invalid_data(self, client, auth_headers):
        """Test taxonomy creation with invalid data."""
        response = client.post(
            f"{settings.API_V1_STR}/taxonomy",
            headers=auth_headers,
            json={
                "uuid": "test-uuid-123",
                # Missing required fields
            },
        )
        assert response.status_code == 422  # Validation error

    def test_update_taxonomy_success(self, client, auth_headers):
        """Test successful taxonomy update."""
        with patch("app.business.taxonomy.TaxonomyManager.update_taxonomy_by_uuid") as mock_update:
            updated_taxonomy = Taxonomy(
                id=1,
                uuid="f50ec0b7-f960-400d-91f0-c42a6d44e3d0",
                label="Updated Sports",
                taxonomy_id=100,
                created_at="2024-01-01T00:00:00Z",
                created_by="test_user",
                updated_at="2024-01-01T00:00:00Z",
                updated_by="test_user",
            )
            mock_update.return_value = updated_taxonomy

            response = client.put(
                f"{settings.API_V1_STR}/taxonomy/f50ec0b7-f960-400d-91f0-c42a6d44e3d0",
                headers=auth_headers,
                json={
                    "label": "Updated Sports",
                },
            )

            assert response.status_code == 200
            data = response.json()
            assert data["label"] == "Updated Sports"
            mock_update.assert_called_once()

    def test_update_taxonomy_not_found(self, client, auth_headers):
        """Test taxonomy update with non-existent UUID."""
        with patch("app.business.taxonomy.TaxonomyManager.update_taxonomy_by_uuid") as mock_update:
            mock_update.side_effect = HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Taxonomy f50ec0b7-f960-400d-91f0-c42a6d44e3d1 not found"
            )

            response = client.put(
                f"{settings.API_V1_STR}/taxonomy/f50ec0b7-f960-400d-91f0-c42a6d44e3d1",
                headers=auth_headers,
                json={
                    "label": "Updated Label",
                },
            )

            assert response.status_code == 404
            data = response.json()
            assert data["detail"] == "Taxonomy f50ec0b7-f960-400d-91f0-c42a6d44e3d1 not found"

    def test_update_taxonomy_unauthorized(self, client):
        """Test unauthorized access to update taxonomy."""
        response = client.put(
            f"{settings.API_V1_STR}/taxonomy/f50ec0b7-f960-400d-91f0-c42a6d44e3d0",
            json={
                "label": "Updated Label",
            },
        )
        assert response.status_code == 403

    def test_delete_taxonomy_success(self, client, auth_headers):
        """Test successful taxonomy deletion."""
        with patch("app.business.taxonomy.TaxonomyManager.delete_taxonomy_by_uuid") as mock_delete:
            mock_delete.return_value = None

            response = client.delete(
                f"{settings.API_V1_STR}/taxonomy/f50ec0b7-f960-400d-91f0-c42a6d44e3d0", headers=auth_headers
            )

            assert response.status_code == 200
            mock_delete.assert_called_once_with(taxonomy_uuid="f50ec0b7-f960-400d-91f0-c42a6d44e3d0")

    def test_delete_taxonomy_unauthorized(self, client):
        """Test unauthorized access to delete taxonomy."""
        response = client.delete(f"{settings.API_V1_STR}/taxonomy/f50ec0b7-f960-400d-91f0-c42a6d44e3d0")
        assert response.status_code == 403

    def test_taxonomy_endpoints_without_auth_header(self, client):
        """Test all taxonomy endpoints without authentication header."""
        endpoints = [
            ("GET", f"{settings.API_V1_STR}/taxonomy"),
            ("GET", f"{settings.API_V1_STR}/taxonomy/f50ec0b7-f960-400d-91f0-c42a6d44e3d0"),
            ("POST", f"{settings.API_V1_STR}/taxonomy"),
            ("PUT", f"{settings.API_V1_STR}/taxonomy/f50ec0b7-f960-400d-91f0-c42a6d44e3d0"),
            ("DELETE", f"{settings.API_V1_STR}/taxonomy/f50ec0b7-f960-400d-91f0-c42a6d44e3d0"),
        ]

        for method, url in endpoints:
            if method == "GET":
                response = client.get(url)
            elif method == "POST":
                response = client.post(url, json={"label": "test"})
            elif method == "PUT":
                response = client.put(url, json={"label": "test"})
            elif method == "DELETE":
                response = client.delete(url)

            assert response.status_code == 403

    def test_taxonomy_endpoints_with_invalid_auth(self, client):
        """Test all taxonomy endpoints with invalid authentication."""
        invalid_headers = {settings.AUTH_HEADER_KEY: "invalid_token"}

        endpoints = [
            ("GET", f"{settings.API_V1_STR}/taxonomy"),
            ("GET", f"{settings.API_V1_STR}/taxonomy/f50ec0b7-f960-400d-91f0-c42a6d44e3d0"),
            ("POST", f"{settings.API_V1_STR}/taxonomy"),
            ("PUT", f"{settings.API_V1_STR}/taxonomy/f50ec0b7-f960-400d-91f0-c42a6d44e3d0"),
            ("DELETE", f"{settings.API_V1_STR}/taxonomy/f50ec0b7-f960-400d-91f0-c42a6d44e3d0"),
        ]

        for method, url in endpoints:
            if method == "GET":
                response = client.get(url, headers=invalid_headers)
            elif method == "POST":
                response = client.post(url, headers=invalid_headers, json={"label": "test"})
            elif method == "PUT":
                response = client.put(url, headers=invalid_headers, json={"label": "test"})
            elif method == "DELETE":
                response = client.delete(url, headers=invalid_headers)

            assert response.status_code == 403
