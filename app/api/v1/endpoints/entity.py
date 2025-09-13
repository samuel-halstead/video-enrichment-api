from fastapi import APIRouter, Depends, status
from video_enrichment_orm.schemas.entity import Entity, EntityCreate, EntityUpdate

from app.api.dependencies import ManagerFactory
from app.business.entity import EntityManager

router = APIRouter(prefix="/entity", tags=["Entity"])


@router.get(
    "",
    response_model=list[Entity],
    status_code=status.HTTP_200_OK,
)
async def get_all_entities(
    manager: EntityManager = Depends(ManagerFactory.for_entity),
) -> list[Entity]:
    """
    Get all enabled entities should respond status OK and 200 HTTP Response Code.

    Args:
        manager(EntityManager): The manager (domain) with the business logic.

    Returns:
        (json): list of enabled entities
    """

    return manager.get_all_entities()


@router.get(
    "/{entity_uuid}",
    response_model=Entity,
    status_code=status.HTTP_200_OK,
)
async def get_entity_by_uuid(
    entity_uuid: str,
    manager: EntityManager = Depends(ManagerFactory.for_entity),
) -> Entity:
    """
    Get entity by uuid should respond status OK and 200 HTTP Response Code.

    Args:
        entity_uuid(str): The uuid of the entity.
        manager(EntityManager): The manager (domain) with the business logic.

    Returns:
        (json): Entity
    """

    return manager.get_entity_by_uuid(entity_uuid=entity_uuid)


@router.get(
    "/by-taxonomy/{taxonomy_id}",
    response_model=list[Entity],
    status_code=status.HTTP_200_OK,
)
async def get_entities_by_taxonomy_id(
    taxonomy_id: int,
    manager: EntityManager = Depends(ManagerFactory.for_entity),
) -> list[Entity]:
    """
    Get enabled entities by taxonomy id should respond status OK and 200 HTTP Response Code.

    Args:
        taxonomy_id(int): The taxonomy id to filter entities.
        manager(EntityManager): The manager (domain) with the business logic.

    Returns:
        (json): list of enabled entities for the taxonomy
    """

    return manager.get_entities_by_taxonomy_id(taxonomy_id=taxonomy_id)


@router.post(
    "",
    response_model=Entity,
    status_code=status.HTTP_200_OK,
)
async def save_entity(
    entity_request: EntityCreate,
    manager: EntityManager = Depends(ManagerFactory.for_entity),
) -> Entity:
    """
    Create entity should respond status OK and 200 HTTP Response Code.

    Args:
        entity_request(EntityCreate): The definition of the entity.
        manager(EntityManager): The manager (domain) with the business logic.

    Returns:
        (json): Entity
    """

    return manager.save_entity(entity_request)


@router.put(
    "/{entity_uuid}",
    response_model=Entity,
    status_code=status.HTTP_200_OK,
)
async def update_entity(
    entity_uuid: str,
    entity_update: EntityUpdate,
    manager: EntityManager = Depends(ManagerFactory.for_entity),
) -> Entity:
    """
    Update entity should respond status OK and 200 HTTP Response Code.

    Args:
        entity_uuid(str): The uuid of the entity.
        entity_update(EntityUpdate): The entity update data.
        manager(EntityManager): The manager (domain) with the business logic.

    Returns:
        (json): Updated Entity
    """

    return manager.update_entity_by_uuid(entity_uuid=entity_uuid, entity_update=entity_update)


@router.delete(
    "/{entity_uuid}",
    response_model=None,
    status_code=status.HTTP_200_OK,
)
async def delete_entity(
    entity_uuid: str,
    manager: EntityManager = Depends(ManagerFactory.for_entity),
) -> None:
    """
    Delete entity by uuid should respond status OK and 200 HTTP Response Code.

    Args:
        entity_uuid(str): The uuid of the entity.
        manager(EntityManager): The manager (domain) with the business logic.

    Returns:
        (json): None
    """

    return manager.delete_entity_by_uuid(entity_uuid=entity_uuid)
