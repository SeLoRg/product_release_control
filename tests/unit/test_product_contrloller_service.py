from unittest.mock import AsyncMock

import pytest
from datetime import date, datetime, timezone
from src.backend.product_controler.schemas.schemas import (
    ShiftTaskIn,
    WorkCenterSchema,
    BatchSchema,
)
from src.backend.core.models import WorkCenters, ShiftTasks, Batches, Products


class TestUnitProductControllerService:
    @pytest.mark.asyncio
    @pytest.mark.parametrize(
        "shift_task_input",
        [
            {
                "task_description": "Task 1",
                "is_closed": False,
                "work_center": "WC1",
                "shift": "A",
                "brigade": "B1",
                "batch_number": 101,
                "ekn_code": "EKN1",
                "batch_date": date(2025, 9, 7),
                "nomenclature": "Nom1",
                "shift_start": datetime(2025, 9, 7, 8, 0),
                "shift_end": datetime(2025, 9, 7, 16, 0),
            },
            {
                "task_description": "Task 2",
                "is_closed": True,
                "work_center": "WC2",
                "shift": "B",
                "brigade": "B2",
                "batch_number": 102,
                "ekn_code": "EKN2",
                "batch_date": date(2025, 9, 8),
                "nomenclature": "Nom2",
                "shift_start": datetime(2025, 9, 8, 9, 0),
                "shift_end": datetime(2025, 9, 8, 17, 0),
            },
        ],
    )
    async def test_shift_task_add(
        self, product_controller_service, mock_repos, shift_task_input
    ):
        # Создаем объекты моделей для моков
        work_center_model = WorkCenters(id=1, name=shift_task_input["work_center"])
        shift_task_model = ShiftTasks(
            id=10,
            task_description=shift_task_input["task_description"],
            is_closed=shift_task_input["is_closed"],
            shift=shift_task_input["shift"],
            brigade=shift_task_input["brigade"],
            shift_start=shift_task_input["shift_start"],
            shift_end=shift_task_input["shift_end"],
            work_center_id=work_center_model.id,
        )
        batch_model = Batches(
            id=100,
            shift_task_id=shift_task_model.id,
            batch_number=shift_task_input["batch_number"],
            batch_date=shift_task_input["batch_date"],
            ekn_code=shift_task_input["ekn_code"],
            nomenclature=shift_task_input["nomenclature"],
        )

        # Настраиваем возвраты моков
        product_controller_service._get_or_create = AsyncMock(
            side_effect=[work_center_model, shift_task_model, batch_model]
        )

        shift_task_in = ShiftTaskIn(**shift_task_input)

        # Вызов метода
        result = await product_controller_service.shift_task_add(shift_task_in)
        result.work_center = WorkCenterSchema.model_validate(work_center_model)
        result.batches = [BatchSchema.model_validate(batch_model)]

        # Проверяем вызовы
        product_controller_service.session.refresh.assert_awaited_once()
        product_controller_service._get_or_create.assert_awaited()
        assert product_controller_service._get_or_create.await_count == 3

        # Проверяем возвращаемый объект (Pydantic-схема)
        assert result.id == shift_task_model.id
        assert result.work_center.name == work_center_model.name
        assert len(result.batches) == 1
        batch_result = result.batches[0]
        assert batch_result.batch_number == batch_model.batch_number
        assert batch_result.ekn_code == batch_model.ekn_code
        assert batch_result.nomenclature == batch_model.nomenclature

    @pytest.mark.asyncio
    @pytest.mark.parametrize(
        "shift_task_model",
        [
            ShiftTasks(
                id=1,
                task_description="Task 1",
                is_closed=False,
                shift="A",
                brigade="B1",
                shift_start=datetime(2025, 9, 7, 8, 0),
                shift_end=datetime(2025, 9, 7, 16, 0),
                work_center_id=1,
                work_center=WorkCenters(id=1, name="WC1"),
                batches=[
                    Batches(
                        id=101,
                        batch_number=1001,
                        ekn_code="EKN1",
                        batch_date=date(2025, 9, 7),
                        nomenclature="Nom1",
                        products=[
                            Products(
                                unique_code="P001",
                                batch_id=101,
                                is_aggregated=False,
                                created_at=datetime.now(timezone.utc),
                            ),
                            Products(
                                unique_code="P002",
                                batch_id=101,
                                is_aggregated=True,
                                created_at=datetime.now(timezone.utc),
                            ),
                        ],
                    )
                ],
            ),
            ShiftTasks(
                id=2,
                task_description="Task 2",
                is_closed=True,
                shift="B",
                brigade="B2",
                shift_start=datetime(2025, 9, 8, 9, 0),
                shift_end=datetime(2025, 9, 8, 17, 0),
                work_center_id=2,
                work_center=WorkCenters(id=2, name="WC2"),
                batches=[
                    Batches(
                        id=102,
                        batch_number=1002,
                        ekn_code="EKN2",
                        batch_date=date(2025, 9, 8),
                        nomenclature="Nom2",
                        products=[
                            Products(
                                unique_code="P101",
                                batch_id=102,
                                is_aggregated=False,
                                created_at=datetime.now(timezone.utc),
                            )
                        ],
                    )
                ],
            ),
        ],
    )
    async def test_shift_task_get_by_id_all(
        self, product_controller_service, shift_task_model
    ):
        # Замокаем метод репозитория
        product_controller_service.shift_task_repo.get_by_id_all.return_value = (
            shift_task_model
        )
        # Вызов сервиса
        result = await product_controller_service.shift_task_get_by_id(
            shift_task_model.id
        )

        # Проверяем, что метод репозитория вызвался с правильными параметрами
        product_controller_service.shift_task_repo.get_by_id_all.assert_awaited_once_with(
            shift_task_id=shift_task_model.id, limit=100, skip=0
        )

        # Проверяем возвращаемую Pydantic-схему
        assert result.id == shift_task_model.id
        assert result.work_center.name == shift_task_model.work_center.name
        assert len(result.batches) == len(shift_task_model.batches)

        for batch_schema, batch_model in zip(result.batches, shift_task_model.batches):
            assert batch_schema.id == batch_model.id
            assert batch_schema.batch_number == batch_model.batch_number
            assert len(batch_schema.products) == len(batch_model.products)
            for prod_schema, prod_model in zip(
                batch_schema.products, batch_model.products
            ):
                assert prod_schema.unique_code == prod_model.unique_code
                assert prod_schema.is_aggregated == prod_model.is_aggregated
                assert prod_schema.aggregated_at == prod_model.aggregated_at
