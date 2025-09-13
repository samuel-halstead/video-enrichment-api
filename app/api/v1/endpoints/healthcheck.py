from fastapi import APIRouter, Depends, status

from app.api.dependencies import ManagerFactory
from app.business.healthcheck import HealthcheckManager
from app.schemas.healthcheck import HealthcheckStatus

router = APIRouter(prefix="/healthcheck", tags=["Healthcheck"])


@router.get(
    "",
    response_model=HealthcheckStatus,
    status_code=status.HTTP_200_OK,
)
async def healthcheck(
    manager: HealthcheckManager = Depends(ManagerFactory.for_healthchecks),
) -> HealthcheckStatus:
    """
    Healthcheck should response status OK and 200 HTTP Response Code.

    Args:
        manager(HealthcheckManager): The manager (domain) with the business logic.

    Returns:
        (json): message OK
    """

    return manager.status()
