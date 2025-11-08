from typing import Optional, List, Literal
from datetime import datetime, timezone
from sqlalchemy import select, Result, exc, desc, asc
from sqlalchemy.orm import selectinload
from src.backend.core.crud import CrudDB
from src.backend.core.crud.BaseRepository import T
from src.backend.core.models import ShiftTasks, Batches
from sqlalchemy.ext.asyncio import AsyncSession


class ShiftTasksRepo(CrudDB[ShiftTasks]):
    def __init__(self, session: AsyncSession):
        super().__init__(model=ShiftTasks, session=session)

    async def get_by_id_all(
        self,
        shift_task_id: int,
        limit: int = 100,
        skip: int = 0,
    ) -> T | None:
        """Возвращает полную модель с подгрузкой связей"""

        try:
            stmt = (
                select(self.model)
                .limit(limit)
                .offset(skip)
                .where(self.model.id == shift_task_id)
                .options(
                    selectinload(self.model.batches).selectinload(Batches.products),
                    selectinload(self.model.work_center),
                )
            )
            res: Result = await self.session.execute(stmt)

            return res.scalar_one_or_none()

        except exc.NoResultFound:
            return None
        except exc.SQLAlchemyError as e:
            raise ValueError(f"Failed to get {self.model.__name__}: {str(e)}")

    async def update_by_id(self, object_id: int, **update_fields) -> Optional[T]:
        if "is_closed" in update_fields and update_fields["is_closed"]:
            if update_fields["is_closed"]:
                update_fields["closed_at"] = datetime.now(timezone.utc)
            else:
                update_fields["closed_at"] = None

        updated_model = await super().update_by_id(object_id, **update_fields)

        await self.session.refresh(
            updated_model, attribute_names=["batches", "work_center"]
        )

        return updated_model

    async def get_by_filter_sorted(
        self,
        values_to_sort: Optional[dict[str, Literal["desc", "asc"]]] = None,
        limit: int = 100,
        skip: int = 0,
        **filters,
    ) -> List[T]:
        try:
            filters_conditions = [
                getattr(self.model, key) == value
                for key, value in filters.items()
                if hasattr(self.model, key)
            ]
            stmt = select(self.model).options(
                selectinload(self.model.batches), selectinload(self.model.work_center)
            )

            if filters_conditions:
                stmt = stmt.filter(*filters_conditions)

            if values_to_sort:
                order_by_clauses = []

                for key, value in values_to_sort.items():
                    col = getattr(self.model, key)
                    if value == "desc":
                        col = desc(col)
                    else:
                        col = asc(col)
                    order_by_clauses.append(col)

                stmt = stmt.order_by(*order_by_clauses)

            else:
                stmt = stmt.order_by(desc(self.model.shift_start))

            stmt = stmt.limit(limit).offset(skip)
            res: Result = await self.session.execute(stmt)

            return list(res.scalars().all())

        except exc.NoResultFound:
            return []
        except exc.SQLAlchemyError as e:
            raise ValueError(f"Failed to get {self.model.__name__}: {str(e)}")
