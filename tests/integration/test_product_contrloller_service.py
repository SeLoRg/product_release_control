import pytest
from datetime import datetime, date, timezone, timedelta
from sqlalchemy import select

from src.backend.core.models import WorkCenters, Batches, ShiftTasks, Products
from src.backend.product_controler.exceptions.exceptions import (
    UniqueCodeAlreadyUsedError,
    UniqueCodeAttachedToAnotherBatchError,
    UniqueCodeNotFoundError,
)
from src.backend.product_controler.schemas.schemas import (
    ShiftTaskIn,
    ShiftTaskSchemaAll,
    ShiftTaskUpdate,
    ProductsIn,
)


class TestIntegrationProductControllerService:
    @pytest.mark.parametrize(
        "shift_task_data_in",
        [
            ShiftTaskIn(
                task_description="Task 1",
                is_closed=False,
                work_center="WC1",
                shift="A",
                brigade="B1",
                batch_number=101,
                ekn_code="EKN1",
                batch_date=date(2025, 9, 7),
                nomenclature="Nom1",
                shift_start=datetime(2025, 9, 7, 8, 0),
                shift_end=datetime(2025, 9, 7, 16, 0),
            ),
            ShiftTaskIn(
                task_description="Task 2",
                is_closed=True,
                work_center="WC2",
                shift="B",
                brigade="B2",
                batch_number=102,
                ekn_code="EKN2",
                batch_date=date(2025, 9, 8),
                nomenclature="Nom2",
                shift_start=datetime(2025, 9, 8, 9, 0),
                shift_end=datetime(2025, 9, 8, 17, 0),
            ),
        ],
    )
    @pytest.mark.asyncio
    async def test_add_shift_task(
        self,
        product_controller_service_intgr,
        shift_task_data_in,
    ):
        result = await product_controller_service_intgr.shift_task_add(
            shift_task_data_in
        )

        # Проверяем Pydantic-схему
        assert result.id is not None
        assert result.work_center.name == shift_task_data_in.work_center
        assert len(result.batches) == 1

        # Проверка на создание записей в бд
        work_center_in_db = await product_controller_service_intgr.session.scalar(
            select(WorkCenters).where(
                WorkCenters.name == shift_task_data_in.work_center
            )
        )

        assert work_center_in_db is not None

        shift_task_in_db = await product_controller_service_intgr.session.scalar(
            select(ShiftTasks).where(
                ShiftTasks.task_description == shift_task_data_in.task_description
            )
        )

        assert shift_task_in_db is not None

        batch_in_db = await product_controller_service_intgr.session.scalar(
            select(Batches).where(
                Batches.batch_number == shift_task_data_in.batch_number
            )
        )

        assert batch_in_db is not None
        assert batch_in_db.shift_task_id == shift_task_in_db.id

    @pytest.mark.asyncio
    async def test_get_shift_task_by_id_all(
        self, product_controller_service_intgr, init_db
    ):
        result = await product_controller_service_intgr.shift_task_get_by_id(
            shift_task_id=init_db["shift"].id
        )

        # Проверки
        assert result is not None
        assert isinstance(result, ShiftTaskSchemaAll)
        assert result.id == init_db["shift"].id
        assert result.work_center.name == init_db["work_center"].name
        assert len(result.batches) == len(init_db["shift"].batches)

        batch_schema = result.batches[0]
        assert batch_schema.batch_number == init_db["batch"].batch_number
        assert len(batch_schema.products) == len(init_db["batch"].products)

        unique_codes = {p.unique_code for p in batch_schema.products}
        assert unique_codes == {
            init_db["product1"].unique_code,
            init_db["product2"].unique_code,
        }

    @pytest.mark.parametrize(
        "update_data, expect_task_desc, expect_closed",
        [
            (
                ShiftTaskUpdate(task_description="Updated shift task", is_closed=True),
                "Updated shift task",
                True,
            ),
            (
                ShiftTaskUpdate(is_closed=False),
                None,
                False,
            ),
        ],
    )
    @pytest.mark.asyncio
    async def test_partial_update_shift_task_by_id(
        self,
        product_controller_service_intgr,
        init_db,
        update_data,
        expect_task_desc,
        expect_closed,
    ):
        shift_id = init_db["shift"].id

        # --- Обновляем ---
        updated_result = (
            await product_controller_service_intgr.partial_update_shift_task_by_id(
                shift_task_id=shift_id, shift_task_update_in=update_data
            )
        )

        # Проверяем реальные данные в базе
        shift_in_db: list[ShiftTasks] = (
            await product_controller_service_intgr.shift_task_repo.get_by_filter(
                id=shift_id
            )
        )
        shift_in_db: ShiftTasks = shift_in_db[0]

        # --- Проверки task_description ---
        if expect_task_desc:
            assert updated_result.task_description == expect_task_desc
            assert shift_in_db.task_description == expect_task_desc
        else:
            # task_description не менялся
            assert updated_result.task_description == init_db["shift"].task_description
            assert shift_in_db.task_description == init_db["shift"].task_description

        # --- Проверки закрытия ---
        assert updated_result.is_closed is expect_closed
        assert shift_in_db.is_closed is expect_closed

        if expect_closed:
            assert updated_result.closed_at is not None
            assert shift_in_db.closed_at is not None
        else:
            assert updated_result.closed_at is None
            assert shift_in_db.closed_at is None

    @pytest.mark.asyncio
    async def test_get_shift_tasks_list(self, product_controller_service_intgr):
        now = datetime.now(tz=timezone.utc)

        wc = WorkCenters(name="WC1")
        product_controller_service_intgr.session.add(wc)
        await product_controller_service_intgr.session.flush()  # чтобы wc.id появился
        await product_controller_service_intgr.session.refresh(wc)

        shift1 = ShiftTasks(
            task_description="Task A",
            is_closed=False,
            shift="A",
            brigade="B1",
            shift_start=now - timedelta(hours=3),
            shift_end=now - timedelta(hours=2),
            work_center_id=wc.id,
        )
        shift2 = ShiftTasks(
            task_description="Task B",
            is_closed=True,
            shift="B",
            brigade="B2",
            shift_start=now - timedelta(hours=2),
            shift_end=now - timedelta(hours=1),
            work_center_id=wc.id,
        )
        shift3 = ShiftTasks(
            task_description="Task C",
            is_closed=False,
            shift="C",
            brigade="B3",
            shift_start=now - timedelta(hours=1),
            shift_end=now,
            work_center_id=wc.id,
        )

        product_controller_service_intgr.session.add_all([shift1, shift2, shift3])
        await product_controller_service_intgr.session.commit()

        # --- Act & Assert: сортировка по shift_start DESC ---
        results = await product_controller_service_intgr.get_shift_tasks_list(
            values_to_sort={"shift_start": "desc"}
        )
        assert [r.task_description for r in results] == ["Task C", "Task B", "Task A"]

        # --- Act & Assert: сортировка по shift_start ASC ---
        results = await product_controller_service_intgr.get_shift_tasks_list(
            values_to_sort={"shift_start": "asc"}
        )
        assert [r.task_description for r in results] == ["Task A", "Task B", "Task C"]

        # --- Act & Assert: сортировка по task_description ASC ---
        results = await product_controller_service_intgr.get_shift_tasks_list(
            values_to_sort={"task_description": "asc"}
        )
        assert [r.task_description for r in results] == ["Task A", "Task B", "Task C"]

        # --- Act & Assert: сортировка по task_description DESC ---
        results = await product_controller_service_intgr.get_shift_tasks_list(
            values_to_sort={"task_description": "desc"}
        )
        assert [r.task_description for r in results] == ["Task C", "Task B", "Task A"]

    @pytest.mark.asyncio
    async def test_add_product_to_batch(
        self, product_controller_service_intgr, init_db_to_add_product_to_batch
    ):
        """
        Проверяем метод add_product_to_batch:
        - добавление продуктов к существующим партиям
        - игнорирование несуществующих партий
        - уникальность unique_code
        """

        # --- Продукты на добавление ---
        products_to_add = [
            ProductsIn(
                unique_code=init_db_to_add_product_to_batch["product1"].unique_code,
                batch_number=111,
                batch_date=date(2025, 9, 9),
            ),
            ProductsIn(
                unique_code=init_db_to_add_product_to_batch["product2"].unique_code,
                batch_number=111,
                batch_date=date(2025, 9, 9),
            ),
            ProductsIn(
                unique_code="P003", batch_number=222, batch_date=date(2025, 9, 10)
            ),
            ProductsIn(
                unique_code="P004", batch_number=333, batch_date=date(2025, 9, 11)
            ),  # нет такой партии
        ]

        added_products = await product_controller_service_intgr.add_product_to_batch(
            products_to_add
        )

        # --- Проверки ---
        # Продукт, у которого нет партии, не добавлен
        assert all(p.unique_code != "P004" for p in added_products)

        # Проверяем, что все остальные добавлены
        assert len(added_products) == 1
        codes_added = {p.unique_code for p in added_products}
        assert codes_added == {"P003"}

        # Проверяем, что в базе модели Products создались с правильным batch_id
        p1_model = await product_controller_service_intgr.product_repo.get_by_filter(
            unique_code="P003"
        )
        assert p1_model[0].batch_id == init_db_to_add_product_to_batch["batch2"].id

    @pytest.mark.asyncio
    async def test_aggregate_product_bool(
        self,
        product_controller_service_intgr,
        init_db_to_add_product_to_batch,
        db_session_to_test,
    ):
        service = product_controller_service_intgr
        batch = init_db_to_add_product_to_batch["batch"]
        product1 = init_db_to_add_product_to_batch["product1"]

        # --- Успешная агрегация ---
        await service.aggregate_product(batch.id, product1.unique_code)

        # Проверяем, что is_aggregated реально обновилось в базе
        async with service.session.begin():
            updated_product1 = (
                await service.product_repo.get_by_filter(
                    unique_code=product1.unique_code
                )
            )[0]
            assert updated_product1.is_aggregated is True
            assert updated_product1.aggregated_at is not None

        # --- Попытка агрегировать уже агрегированный продукт ---
        with pytest.raises(UniqueCodeAlreadyUsedError):
            await service.aggregate_product(batch.id, product1.unique_code)

        # --- Попытка агрегировать продукт, который привязан к другой партии ---
        other_batch = init_db_to_add_product_to_batch["batch2"]
        product_other_batch = Products(
            unique_code="P999",
            batch_id=other_batch.id,
            is_aggregated=False,
            created_at=datetime.now(timezone.utc),
        )
        db_session_to_test.add(product_other_batch)
        await db_session_to_test.commit()

        with pytest.raises(UniqueCodeAttachedToAnotherBatchError):
            await service.aggregate_product(batch.id, "P999")

        # --- Попытка агрегировать несуществующий код ---
        with pytest.raises(UniqueCodeNotFoundError):
            await service.aggregate_product(batch.id, "NOT_EXISTING_CODE")
