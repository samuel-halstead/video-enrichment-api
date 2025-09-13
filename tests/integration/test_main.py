import pytest
from fastapi.testclient import TestClient

from app.core.config import settings
from app.core.enums import ServiceAvailability
from app.main import app
from app.schemas.healthcheck import HealthcheckStatus


@pytest.fixture
def client():
    return TestClient(app)


def test_health_check(client):
    """
    GIVEN The health respose.
    WHEN health check endpoint is called with GET method.
    THEN response with status 200 and rigth body is returned.
    """

    health_response = HealthcheckStatus(
        name=settings.PROJECT_NAME,
        status=ServiceAvailability.Up,
    )

    response = client.get("".join([settings.API_V1_STR, "/healthcheck"]))
    assert response.status_code == 200

    value = response.json()
    assert value["name"] == health_response.name
    assert value["status"] == health_response.status.value
