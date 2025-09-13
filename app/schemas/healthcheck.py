from pydantic import BaseModel

from app.core.enums import ServiceAvailability


class HealthcheckStatus(BaseModel):

    """
    Healthcheck HTTP response schema.
    """

    name: str
    status: ServiceAvailability
