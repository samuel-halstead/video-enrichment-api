from fastapi import APIRouter, Depends, status
from video_enrichment_orm.schemas.taxonomy import (
    Taxonomy,
    TaxonomyCreate,
    TaxonomyUpdate,
)

from app.api.dependencies import ManagerFactory
from app.business.taxonomy import TaxonomyManager

router = APIRouter(prefix="/taxonomy", tags=["Taxonomy"])


@router.get(
    "",
    response_model=list[Taxonomy],
    status_code=status.HTTP_200_OK,
)
async def get_all_taxonomies(
    manager: TaxonomyManager = Depends(ManagerFactory.for_taxonomy),
) -> list[Taxonomy]:
    """
    Get all taxonomies should respond status OK and 200 HTTP Response Code.

    Args:
        manager(TaxonomyManager): The manager (domain) with the business logic.

    Returns:
        (json): list of taxonomies
    """

    return manager.get_all_taxonomies()


@router.get(
    "/{taxonomy_uuid}",
    response_model=Taxonomy,
    status_code=status.HTTP_200_OK,
)
async def get_taxonomy_by_uuid(
    taxonomy_uuid: str,
    manager: TaxonomyManager = Depends(ManagerFactory.for_taxonomy),
) -> Taxonomy:
    """
    Get taxonomy by uuid should respond status OK and 200 HTTP Response Code.

    Args:
        taxonomy_uuid(str): The uuid of the taxonomy.
        manager(TaxonomyManager): The manager (domain) with the business logic.

    Returns:
        (json): Taxonomy
    """

    return manager.get_taxonomy_by_uuid(taxonomy_uuid=taxonomy_uuid)


@router.post(
    "",
    response_model=Taxonomy,
    status_code=status.HTTP_200_OK,
)
async def save_taxonomy(
    taxonomy_request: TaxonomyCreate,
    manager: TaxonomyManager = Depends(ManagerFactory.for_taxonomy),
) -> Taxonomy:
    """
    Create taxonomy should respond status OK and 200 HTTP Response Code.

    Args:
        taxonomy_request(TaxonomyCreate): The definition of the taxonomy.
        manager(TaxonomyManager): The manager (domain) with the business logic.

    Returns:
        (json): Taxonomy
    """

    return manager.save_taxonomy(taxonomy_request)


@router.put(
    "/{taxonomy_uuid}",
    response_model=Taxonomy,
    status_code=status.HTTP_200_OK,
)
async def update_taxonomy(
    taxonomy_uuid: str,
    taxonomy_update: TaxonomyUpdate,
    manager: TaxonomyManager = Depends(ManagerFactory.for_taxonomy),
) -> Taxonomy:
    """
    Update taxonomy should respond status OK and 200 HTTP Response Code.

    Args:
        taxonomy_uuid(str): The uuid of the taxonomy.
        taxonomy_update(TaxonomyUpdate): The taxonomy update data.
        manager(TaxonomyManager): The manager (domain) with the business logic.

    Returns:
        (json): Updated Taxonomy
    """

    return manager.update_taxonomy_by_uuid(taxonomy_uuid=taxonomy_uuid, taxonomy_update=taxonomy_update)


@router.delete(
    "/{taxonomy_uuid}",
    response_model=None,
    status_code=status.HTTP_200_OK,
)
async def delete_taxonomy(
    taxonomy_uuid: str,
    manager: TaxonomyManager = Depends(ManagerFactory.for_taxonomy),
) -> None:
    """
    Delete taxonomy by uuid should respond status OK and 200 HTTP Response Code.

    Args:
        taxonomy_uuid(str): The uuid of the taxonomy.
        manager(TaxonomyManager): The manager (domain) with the business logic.

    Returns:
        (json): None
    """

    return manager.delete_taxonomy_by_uuid(taxonomy_uuid=taxonomy_uuid)
