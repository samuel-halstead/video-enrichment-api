from fastapi import HTTPException, status
from video_enrichment_orm.managers.db_taxonomy import db_taxonomy_manager
from video_enrichment_orm.schemas.taxonomy import (
    Taxonomy,
    TaxonomyCreate,
    TaxonomyUpdate,
)


class TaxonomyManager:
    def __init__(self) -> None:
        self._db_taxonomy = db_taxonomy_manager

    def get_all_taxonomies(self) -> list[Taxonomy]:
        return self._db_taxonomy.get_taxonomies()

    def get_taxonomy_by_id(self, taxonomy_id: int) -> Taxonomy:
        try:
            taxonomy = self._db_taxonomy.get_taxonomy_by_id(taxonomy_id=taxonomy_id)
            return taxonomy
        except ValueError as e:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e)) from e

    def get_taxonomy_by_uuid(self, taxonomy_uuid: str) -> Taxonomy:
        try:
            taxonomy = self._db_taxonomy.get_taxonomy_by_uuid(taxonomy_uuid=taxonomy_uuid)
            return taxonomy
        except ValueError as e:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e)) from e

    def save_taxonomy(self, taxonomy: TaxonomyCreate) -> Taxonomy:
        # Check if taxonomy exists
        if taxonomy.taxonomy_id:
            try:
                self._db_taxonomy.get_taxonomy_by_id(taxonomy_id=taxonomy.taxonomy_id)
            except ValueError as e:
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e)) from e

        taxonomy_request = TaxonomyCreate(
            uuid=taxonomy.uuid,
            label=taxonomy.label,
            taxonomy_id=taxonomy.taxonomy_id,
        )

        taxonomy = self._db_taxonomy.save_taxonomy(taxonomy=taxonomy_request)
        return taxonomy

    def update_taxonomy_by_uuid(self, taxonomy_uuid: str, taxonomy_update: TaxonomyUpdate) -> Taxonomy:
        try:
            taxonomy = self._db_taxonomy.update_taxonomy(taxonomy_update=taxonomy_update, uuid=taxonomy_uuid)
            return taxonomy
        except ValueError as e:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e)) from e

    def delete_taxonomy_by_id(self, taxonomy_id: int) -> None:
        return self._db_taxonomy.delete_taxonomy_by_id(taxonomy_id=taxonomy_id)

    def delete_taxonomy_by_uuid(self, taxonomy_uuid: str) -> None:
        return self._db_taxonomy.delete_taxonomy_by_uuid(taxonomy_uuid=taxonomy_uuid)
