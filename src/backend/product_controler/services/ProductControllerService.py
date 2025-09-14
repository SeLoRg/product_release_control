import datetime
from logging import Logger
from typing import Optional, Literal, Any, ClassVar

from sqlalchemy.ext.asyncio import AsyncSession
from src.backend.core.logging.LogMeta import LogMeta
from src.backend.core.crud import CrudDB, ShiftTasksRepo
from src.backend.core.models import ShiftTasks, Batches, Products
from src.backend.product_controler.schemas.schemas import (
    ShiftTaskIn,
    WorkCenterSchema,
    BatchSchema,
    ShiftTaskCreate,
    ShiftTaskSchema,
    ShiftTaskSchemaAll,
    ShiftTaskUpdate,
    ProductsIn,
)
from src.backend.product_controler.exceptions.exceptions import (
    UniqueCodeAttachedToAnotherBatchError,
    UniqueCodeNotFoundError,
    UniqueCodeAlreadyUsedError,
)


class ProductControllerService(metaclass=LogMeta):
    logger: ClassVar[Logger]

    def __init__(
        self,
        session: AsyncSession,
        shift_task_repo: ShiftTasksRepo,
        product_repo: CrudDB,
        work_center: CrudDB,
        batche_repo: CrudDB,
    ):
        self.session = session
        self.shift_task_repo = shift_task_repo
        self.product_repo = product_repo
        self.work_center_repo = work_center
        self.batche_repo = batche_repo

    @staticmethod
    async def _get_or_create(repo: CrudDB, filter_kwargs: dict, create_data: dict):
        """Проверка существования объекта и создание при необходимости"""

        existing: list = await repo.get_by_filter(**filter_kwargs)

        if existing:
            return existing[0]

        return await repo.create(**create_data)

    async def shift_task_add(self, shift_task_data_in: ShiftTaskIn) -> ShiftTaskSchema:
        shift_task_data_dct = shift_task_data_in.model_dump()
        work_center_data = WorkCenterSchema(name=shift_task_data_dct.get("work_center"))
        batche_data = BatchSchema(**shift_task_data_dct)
        shift_task_data = ShiftTaskCreate(**shift_task_data_dct)

        async with self.session.begin():
            # Work center
            work_center_model = await self._get_or_create(
                repo=self.work_center_repo,
                filter_kwargs={"name": work_center_data.name},
                create_data=work_center_data.model_dump(exclude_none=True),
            )
            shift_task_data.work_center_id = work_center_model.id

            # Shift task
            shift_task_model = await self._get_or_create(
                repo=self.shift_task_repo,
                filter_kwargs={
                    "task_description": shift_task_data.task_description,
                    "brigade": shift_task_data.brigade,
                    "shift": shift_task_data.shift,
                    "shift_start": shift_task_data.shift_start,
                },
                create_data=shift_task_data.model_dump(exclude_none=True),
            )
            batche_data.shift_task_id = shift_task_model.id

            # Batch
            await self._get_or_create(
                repo=self.batche_repo,
                filter_kwargs={
                    "shift_task_id": shift_task_model.id,
                    "batch_number": batche_data.batch_number,
                },
                create_data=batche_data.model_dump(exclude_none=True),
            )
            await self.session.refresh(
                shift_task_model, attribute_names=["batches", "work_center"]
            )

        # Конвертация в Pydantic-схемы
        shift_task_schema = ShiftTaskSchema.model_validate(shift_task_model)

        return shift_task_schema

    async def shift_task_get_by_id(
        self, shift_task_id: int, limit: int = 100, skip: int = 0
    ) -> ShiftTaskSchemaAll | None:
        """Возвращает Сменное задание со всеми связями"""

        shift_task: ShiftTasks | None = await self.shift_task_repo.get_by_id_all(
            shift_task_id=shift_task_id, limit=limit, skip=skip
        )

        if shift_task is None:
            return None

        return ShiftTaskSchemaAll.model_validate(shift_task)

    async def partial_update_shift_task_by_id(
        self, shift_task_id: int, shift_task_update_in: ShiftTaskUpdate
    ) -> ShiftTaskSchema:
        updated_model: ShiftTasks = await self.shift_task_repo.update_by_id(
            object_id=shift_task_id,
            **shift_task_update_in.model_dump(exclude_none=True),
        )

        return ShiftTaskSchema.model_validate(updated_model)

    async def get_shift_tasks_list(
        self,
        values_to_sort: Optional[dict[str, Literal["desc", "asc"]]] = None,
        offset: int = 0,
        limit: int = 100,
        **filters,
    ) -> list[ShiftTaskSchema]:
        """
        Возвращает  массив Сменных заданий,
        найденных по фильтрам, отсортированные по 'values_to_sort'
        """

        sorted_shift_tasks: list[ShiftTasks] = (
            await self.shift_task_repo.get_by_filter_sorted(
                values_to_sort=values_to_sort,
                offset=offset,
                limit=limit,
                filters=filters,
            )
        )

        return [ShiftTaskSchema.model_validate(model) for model in sorted_shift_tasks]

    async def add_product_to_batch(
        self, products_to_add: list[ProductsIn]
    ) -> list[ProductsIn]:
        products_data: list[tuple] = [
            (product.batch_number, product.batch_date) for product in products_to_add
        ]

        async with self.session.begin():
            batches: list[Batches] = await self.batche_repo.get_by_filter_tuple(
                filters={("batch_number", "batch_date"): products_data}
            )

            self.logger.debug(f"batches={batches}")

            add_products = []
            batch_map: dict[tuple, Any] = {
                (b.batch_number, b.batch_date): b for b in batches
            }

            self.logger.debug(f"batch_map={batch_map}")

            for product in products_to_add:
                batch = batch_map.get((product.batch_number, product.batch_date))

                if batch is None:
                    continue

                self.logger.debug(
                    f"batch={batch.batch_number}, {batch.batch_date}\nproduct={product}"
                )

                if (
                    product.batch_number == batch.batch_number
                    and product.batch_date == batch.batch_date
                ):
                    async with self.session.begin_nested():
                        try:
                            new_model = await self.product_repo.create(
                                unique_code=product.unique_code, batch_id=batch.id
                            )
                            self.logger.debug(f"new_model={new_model}\n-----")

                            if new_model is not None:
                                add_products.append(product)

                        except ValueError:
                            pass

        return add_products

    async def aggregate_product(self, batch_id: int, unique_code: str) -> None:
        async with self.session.begin():
            products: list[Products] = await self.product_repo.get_by_filter(
                unique_code=unique_code
            )
            if len(products) < 1:
                raise UniqueCodeNotFoundError("Product with this unique code not found")

            product = products[0]

            if product.batch_id != batch_id:
                raise UniqueCodeAttachedToAnotherBatchError(
                    "Unique code is attached to another batch"
                )

            if product.is_aggregated:
                raise UniqueCodeAlreadyUsedError(product.aggregated_at)

            product.is_aggregated = True
            product.aggregated_at = datetime.datetime.now(tz=datetime.timezone.utc)
