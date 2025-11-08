from abc import ABC, abstractmethod
from typing import TypeVar, Generic, List, Optional
from uuid import UUID

T = TypeVar("T")


class BaseRepository(ABC, Generic[T]):
    """Абстрактный репозиторий для Dependency Inversion Principle"""

    @abstractmethod
    async def get_by_filter(
        self,
        limit: int = 100,
        skip: int = 0,
        **filters,
    ) -> List[T]:
        """Получить объекты по фильтрам"""

    @abstractmethod
    async def create(self, **kwargs) -> T:
        """Создать объект"""

    @abstractmethod
    async def update_by_id(self, object_id: UUID, **update_fields) -> Optional[T]:
        """Обновить объект по ID"""

    @abstractmethod
    async def delete_by_id(self, object_id: UUID) -> None:
        """Удалить объект по ID"""
