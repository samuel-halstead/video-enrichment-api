from unittest.mock import patch

import pytest
from fastapi import HTTPException, status
from fastapi.testclient import TestClient
from video_enrichment_orm.schemas.entity import Entity, EntityCreate, EntityUpdate

from app.core.config import settings
from app.main import app


@pytest.fixture
def client():
    return TestClient(app)


@pytest.fixture
def auth_headers():
    return {settings.AUTH_HEADER_KEY: settings.AUTH_SECRET_KEY}


# Sample data for testing
entity_data = [
    Entity(
        id=1,
        uuid="f50ec0b7-f960-400d-91f0-c42a6d44e3d0",
        alias=["Real Madrid", "Madrid"],
        enabled=True,
        taxonomy_id=100,
        created_at="2024-01-01T00:00:00Z",
        created_by="test_user",
        updated_at="2024-01-01T00:00:00Z",
        updated_by="test_user",
    ),
    Entity(
        id=2,
        uuid="s50ec0b7-f960-400d-91f0-c42a6d44e3d1",
        alias=["Barcelona", "Barça"],
        enabled=True,
        taxonomy_id=100,
        created_at="2024-01-01T00:00:00Z",
        created_by="test_user",
        updated_at="2024-01-01T00:00:00Z",
        updated_by="test_user",
    ),
    Entity(
        id=3,
        uuid="t50ec0b7-f960-400d-91f0-c42a6d44e3d2",
        alias=["Manchester United", "Man Utd"],
        enabled=False,
        taxonomy_id=200,
        created_at="2024-01-01T00:00:00Z",
        created_by="test_user",
        updated_at="2024-01-01T00:00:00Z",
        updated_by="test_user",
    ),
]

entity_create_data = EntityCreate(
    uuid="test-uuid-123",
    alias=["Test Entity", "Test"],
    enabled=True,
    taxonomy_id=100,
)

entity_update_data = EntityUpdate(
    alias=["Updated Entity", "Updated"],
    enabled=False,
)


class TestEntityEndpoints:
    """Test cases for entity API endpoints."""

    def test_get_all_entities_success(self, client, auth_headers):
        """Test successful retrieval of all entities."""
        with patch("app.business.entity.EntityManager.get_all_entities") as mock_get_all:
            mock_get_all.return_value = entity_data

            response = client.get(f"{settings.API_V1_STR}/entity", headers=auth_headers)

            assert response.status_code == 200
            data = response.json()
            assert len(data) == 3
            assert data[0]["alias"] == ["Real Madrid", "Madrid"]
            assert data[1]["alias"] == ["Barcelona", "Barça"]
            assert data[2]["alias"] == ["Manchester United", "Man Utd"]
            mock_get_all.assert_called_once()

    def test_get_all_entities_unauthorized(self, client):
        """Test unauthorized access to get all entities."""
        response = client.get(f"{settings.API_V1_STR}/entity")
        assert response.status_code == 403

    def test_get_entity_by_uuid_success(self, client, auth_headers):
        """Test successful retrieval of entity by UUID."""
        with patch("app.business.entity.EntityManager.get_entity_by_uuid") as mock_get_entity:
            mock_get_entity.return_value = entity_data[0]

            response = client.get(
                f"{settings.API_V1_STR}/entity/f50ec0b7-f960-400d-91f0-c42a6d44e3d0", headers=auth_headers
            )

            assert response.status_code == 200
            data = response.json()
            assert data["uuid"] == "f50ec0b7-f960-400d-91f0-c42a6d44e3d0"
            assert data["alias"] == ["Real Madrid", "Madrid"]
            assert data["enabled"] is True
            assert data["taxonomy_id"] == 100
            mock_get_entity.assert_called_once_with(entity_uuid="f50ec0b7-f960-400d-91f0-c42a6d44e3d0")

    def test_get_entity_by_uuid_not_found(self, client, auth_headers):
        """Test entity not found by UUID."""
        with patch("app.business.entity.EntityManager.get_entity_by_uuid") as mock_get_entity:
            mock_get_entity.side_effect = HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Entity f50ec0b7-f960-400d-91f0-c42a6d44e3d1 not found"
            )

            response = client.get(
                f"{settings.API_V1_STR}/entity/f50ec0b7-f960-400d-91f0-c42a6d44e3d1", headers=auth_headers
            )

            assert response.status_code == 404
            data = response.json()
            assert data["detail"] == "Entity f50ec0b7-f960-400d-91f0-c42a6d44e3d1 not found"

    def test_get_entity_by_uuid_unauthorized(self, client):
        """Test unauthorized access to get entity by UUID."""
        response = client.get(f"{settings.API_V1_STR}/entity/f50ec0b7-f960-400d-91f0-c42a6d44e3d0")
        assert response.status_code == 403

    def test_get_entities_by_taxonomy_id_success(self, client, auth_headers):
        """Test successful retrieval of entities by taxonomy ID."""
        with patch("app.business.entity.EntityManager.get_entities_by_taxonomy_id") as mock_get_by_taxonomy:
            # Return only enabled entities for taxonomy_id 100
            mock_get_by_taxonomy.return_value = [entity_data[0], entity_data[1]]

            response = client.get(f"{settings.API_V1_STR}/entity/by-taxonomy/100", headers=auth_headers)

            assert response.status_code == 200
            data = response.json()
            assert len(data) == 2
            assert data[0]["alias"] == ["Real Madrid", "Madrid"]
            assert data[1]["alias"] == ["Barcelona", "Barça"]
            mock_get_by_taxonomy.assert_called_once_with(taxonomy_id=100)

    def test_get_entities_by_taxonomy_id_not_found(self, client, auth_headers):
        """Test entities by taxonomy ID when taxonomy doesn't exist."""
        with patch("app.business.entity.EntityManager.get_entities_by_taxonomy_id") as mock_get_by_taxonomy:
            mock_get_by_taxonomy.side_effect = HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Taxonomy with id 999 not found"
            )

            response = client.get(f"{settings.API_V1_STR}/entity/by-taxonomy/999", headers=auth_headers)

            assert response.status_code == 404
            data = response.json()
            assert data["detail"] == "Taxonomy with id 999 not found"

    def test_get_entities_by_taxonomy_id_unauthorized(self, client):
        """Test unauthorized access to get entities by taxonomy ID."""
        response = client.get(f"{settings.API_V1_STR}/entity/by-taxonomy/100")
        assert response.status_code == 403

    def test_save_entity_success(self, client, auth_headers):
        """Test successful entity creation."""
        with patch("app.business.entity.EntityManager.save_entity") as mock_save:
            mock_save.return_value = entity_data[0]

            response = client.post(
                f"{settings.API_V1_STR}/entity",
                headers=auth_headers,
                json={
                    "uuid": "test-uuid-123",
                    "alias": ["Test Entity", "Test"],
                    "enabled": True,
                    "taxonomy_id": 100,
                },
            )

            assert response.status_code == 200
            data = response.json()
            assert data["alias"] == ["Real Madrid", "Madrid"]
            mock_save.assert_called_once()

    def test_save_entity_taxonomy_not_found(self, client, auth_headers):
        """Test entity creation with non-existent taxonomy_id."""
        with patch("app.business.entity.EntityManager.save_entity") as mock_save:
            mock_save.side_effect = HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Taxonomy with id 999 not found"
            )

            response = client.post(
                f"{settings.API_V1_STR}/entity",
                headers=auth_headers,
                json={
                    "uuid": "test-uuid-123",
                    "alias": ["Test Entity", "Test"],
                    "enabled": True,
                    "taxonomy_id": 999,
                },
            )

            assert response.status_code == 404
            data = response.json()
            assert data["detail"] == "Taxonomy with id 999 not found"

    def test_save_entity_unauthorized(self, client):
        """Test unauthorized access to save entity."""
        response = client.post(
            f"{settings.API_V1_STR}/entity",
            json={
                "uuid": "test-uuid-123",
                "alias": ["Test Entity", "Test"],
                "enabled": True,
                "taxonomy_id": 100,
            },
        )
        assert response.status_code == 403

    def test_save_entity_invalid_data(self, client, auth_headers):
        """Test entity creation with invalid data."""
        response = client.post(
            f"{settings.API_V1_STR}/entity",
            headers=auth_headers,
            json={
                "uuid": "test-uuid-123",
                # Missing required fields
            },
        )
        assert response.status_code == 422  # Validation error

    def test_update_entity_success(self, client, auth_headers):
        """Test successful entity update."""
        with patch("app.business.entity.EntityManager.update_entity_by_uuid") as mock_update:
            updated_entity = Entity(
                id=1,
                uuid="f50ec0b7-f960-400d-91f0-c42a6d44e3d0",
                alias=["Updated Real Madrid", "Updated Madrid"],
                enabled=False,
                taxonomy_id=100,
                created_at="2024-01-01T00:00:00Z",
                created_by="test_user",
                updated_at="2024-01-01T00:00:00Z",
                updated_by="test_user",
            )
            mock_update.return_value = updated_entity

            response = client.put(
                f"{settings.API_V1_STR}/entity/f50ec0b7-f960-400d-91f0-c42a6d44e3d0",
                headers=auth_headers,
                json={
                    "alias": ["Updated Real Madrid", "Updated Madrid"],
                    "enabled": False,
                },
            )

            assert response.status_code == 200
            data = response.json()
            assert data["alias"] == ["Updated Real Madrid", "Updated Madrid"]
            assert data["enabled"] is False
            mock_update.assert_called_once()

    def test_update_entity_not_found(self, client, auth_headers):
        """Test entity update with non-existent UUID."""
        with patch("app.business.entity.EntityManager.update_entity_by_uuid") as mock_update:
            mock_update.side_effect = HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Entity f50ec0b7-f960-400d-91f0-c42a6d44e3d1 not found"
            )

            response = client.put(
                f"{settings.API_V1_STR}/entity/f50ec0b7-f960-400d-91f0-c42a6d44e3d1",
                headers=auth_headers,
                json={
                    "alias": ["Updated Entity"],
                    "enabled": True,
                },
            )

            assert response.status_code == 404
            data = response.json()
            assert data["detail"] == "Entity f50ec0b7-f960-400d-91f0-c42a6d44e3d1 not found"

    def test_update_entity_unauthorized(self, client):
        """Test unauthorized access to update entity."""
        response = client.put(
            f"{settings.API_V1_STR}/entity/f50ec0b7-f960-400d-91f0-c42a6d44e3d0",
            json={
                "alias": ["Updated Entity"],
                "enabled": True,
            },
        )
        assert response.status_code == 403

    def test_update_entity_partial_data(self, client, auth_headers):
        """Test entity update with partial data."""
        with patch("app.business.entity.EntityManager.update_entity_by_uuid") as mock_update:
            updated_entity = Entity(
                id=1,
                uuid="f50ec0b7-f960-400d-91f0-c42a6d44e3d0",
                alias=["Real Madrid", "Madrid"],
                enabled=False,  # Only this field updated
                taxonomy_id=100,
                created_at="2024-01-01T00:00:00Z",
                created_by="test_user",
                updated_at="2024-01-01T00:00:00Z",
                updated_by="test_user",
            )
            mock_update.return_value = updated_entity

            response = client.put(
                f"{settings.API_V1_STR}/entity/f50ec0b7-f960-400d-91f0-c42a6d44e3d0",
                headers=auth_headers,
                json={
                    "enabled": False,  # Only update enabled field
                },
            )

            assert response.status_code == 200
            data = response.json()
            assert data["enabled"] is False
            assert data["alias"] == ["Real Madrid", "Madrid"]  # Unchanged
            mock_update.assert_called_once()

    def test_delete_entity_success(self, client, auth_headers):
        """Test successful entity deletion."""
        with patch("app.business.entity.EntityManager.delete_entity_by_uuid") as mock_delete:
            mock_delete.return_value = None

            response = client.delete(
                f"{settings.API_V1_STR}/entity/f50ec0b7-f960-400d-91f0-c42a6d44e3d0", headers=auth_headers
            )

            assert response.status_code == 200
            mock_delete.assert_called_once_with(entity_uuid="f50ec0b7-f960-400d-91f0-c42a6d44e3d0")

    def test_delete_entity_unauthorized(self, client):
        """Test unauthorized access to delete entity."""
        response = client.delete(f"{settings.API_V1_STR}/entity/f50ec0b7-f960-400d-91f0-c42a6d44e3d0")
        assert response.status_code == 403

    def test_entity_endpoints_without_auth_header(self, client):
        """Test all entity endpoints without authentication header."""
        endpoints = [
            ("GET", f"{settings.API_V1_STR}/entity"),
            ("GET", f"{settings.API_V1_STR}/entity/f50ec0b7-f960-400d-91f0-c42a6d44e3d0"),
            ("GET", f"{settings.API_V1_STR}/entity/by-taxonomy/100"),
            ("POST", f"{settings.API_V1_STR}/entity"),
            ("PUT", f"{settings.API_V1_STR}/entity/f50ec0b7-f960-400d-91f0-c42a6d44e3d0"),
            ("DELETE", f"{settings.API_V1_STR}/entity/f50ec0b7-f960-400d-91f0-c42a6d44e3d0"),
        ]

        for method, url in endpoints:
            if method == "GET":
                response = client.get(url)
            elif method == "POST":
                response = client.post(url, json={"alias": ["test"], "taxonomy_id": 100})
            elif method == "PUT":
                response = client.put(url, json={"alias": ["test"]})
            elif method == "DELETE":
                response = client.delete(url)

            assert response.status_code == 403

    def test_entity_endpoints_with_invalid_auth(self, client):
        """Test all entity endpoints with invalid authentication."""
        invalid_headers = {settings.AUTH_HEADER_KEY: "invalid_token"}

        endpoints = [
            ("GET", f"{settings.API_V1_STR}/entity"),
            ("GET", f"{settings.API_V1_STR}/entity/f50ec0b7-f960-400d-91f0-c42a6d44e3d0"),
            ("GET", f"{settings.API_V1_STR}/entity/by-taxonomy/100"),
            ("POST", f"{settings.API_V1_STR}/entity"),
            ("PUT", f"{settings.API_V1_STR}/entity/f50ec0b7-f960-400d-91f0-c42a6d44e3d0"),
            ("DELETE", f"{settings.API_V1_STR}/entity/f50ec0b7-f960-400d-91f0-c42a6d44e3d0"),
        ]

        for method, url in endpoints:
            if method == "GET":
                response = client.get(url, headers=invalid_headers)
            elif method == "POST":
                response = client.post(url, headers=invalid_headers, json={"alias": ["test"], "taxonomy_id": 100})
            elif method == "PUT":
                response = client.put(url, headers=invalid_headers, json={"alias": ["test"]})
            elif method == "DELETE":
                response = client.delete(url, headers=invalid_headers)

            assert response.status_code == 403
