from app.core.config import settings
from app.core.enums import ServiceAvailability
from app.schemas.healthcheck import HealthcheckStatus


class HealthcheckManager:

    """
    A manager to handle the business logic related with healthchecks.
    """

    @staticmethod
    def status() -> HealthcheckStatus:
        """
        Check if the backend is up and running properly.

        Returns:
            A valid HealthcheckStatus instance with a -forced- healthy status.
        """

        return HealthcheckStatus(
            name=settings.PROJECT_NAME,
            status=ServiceAvailability.Up,
        )
