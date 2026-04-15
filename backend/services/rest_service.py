from typing import Any, Optional
from uuid import UUID


class IRestService:
    def create(self, entity: Any) -> Any:
        pass

    def get_all(self, user_id: Optional[int] = None, limit: int = 10, offset: int = 0) -> Any:
        pass

    def get_one(self, entity_id: UUID | int, user_id: Optional[int] = None) -> Any:
        pass

    def update(self, entity_id: UUID | int, entity_data: dict, user_id: Optional[int] = None) -> Any:
        pass

    def delete(self, entity_id: UUID | int, user_id: Optional[int] = None) -> Any:
        pass
