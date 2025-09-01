from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import update, delete, exc, Result
from typing import Type, List, Optional

from src.backend.core.crud.BaseRepository import BaseRepository, T


class CrudDB(BaseRepository[T]):
    def __init__(self, model: Type[T], session: AsyncSession):
        self.model = model
        self.session = session

    async def get_by_filter(
        self,
        limit: int = 100,
        skip: int = 0,
        **filters,
    ) -> List[T]:
        try:
            filters_conditions = [
                getattr(self.model, key) == value for key, value in filters.items()
            ]
            stmt = select(self.model).limit(limit).offset(skip)

            if filters_conditions:
                stmt = stmt.filter(*filters_conditions)

            res: Result = await self.session.execute(stmt)
            return list(res.scalars().all())

        except exc.NoResultFound:
            return []
        except exc.SQLAlchemyError as e:
            raise ValueError(f"Failed to get {self.model.__name__}: {str(e)}")

    async def create(self, **kwargs) -> T:
        try:
            new_object: T = self.model(**kwargs)
            self.session.add(new_object)
            await self.session.flush()
            await self.session.refresh(new_object)
            return new_object
        except exc.SQLAlchemyError as e:
            raise ValueError(f"Failed to create {self.model.__name__}: {str(e)}")

    async def update_by_id(self, object_id: UUID, **update_fields) -> Optional[T]:
        try:
            if not update_fields:
                raise ValueError("No fields provided for update.")

            stmt = (
                update(self.model)
                .where(self.model.id == object_id)
                .values(**update_fields)
                .returning(self.model)
            )

            result: Result = await self.session.execute(stmt)
            updated_object: T | None = result.scalars().one_or_none()
            return updated_object
        except exc.SQLAlchemyError as e:
            raise ValueError(f"Failed to update {self.model.__name__}: {str(e)}")

    async def delete_by_id(self, object_id: UUID) -> None:
        try:
            stmt = delete(self.model).where(self.model.id == object_id)
            await self.session.execute(stmt)
        except exc.SQLAlchemyError as e:
            raise ValueError(f"Failed to delete {self.model.__name__}: {str(e)}")
