from pydantic import BaseModel


class EntityIdsRequest(BaseModel):
    entity_ids: list[int]
