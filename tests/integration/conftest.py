import pytest_asyncio
from datetime import date, datetime, timezone
from sqlalchemy.ext.asyncio import (
    create_async_engine,
    AsyncSession,
    async_sessionmaker,
    AsyncEngine,
)

from src.backend.product_controler.services.ProductControllerService import (
    ProductControllerService,
)
from src.backend.core.models import Base, Batches, WorkCenters, ShiftTasks, Products
from src.backend.core.crud import (
    ProductsRepo,
    BatchesRepo,
    WorkCentersRepo,
    ShiftTasksRepo,
)


@pytest_asyncio.fixture(scope="function")
async def setup_bd() -> AsyncEngine:
    async_engine = create_async_engine(
        url="sqlite+aiosqlite:///:memory:", future=True, echo=False
    )
    async with async_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    yield async_engine

    async with async_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)

    await async_engine.dispose()


@pytest_asyncio.fixture(scope="function")
async def db_session(setup_bd: AsyncEngine) -> AsyncSession:
    async_factory = async_sessionmaker(
        bind=setup_bd, expire_on_commit=False, autoflush=False, autocommit=False
    )

    async with async_factory() as sess:
        yield sess


@pytest_asyncio.fixture(scope="function")
async def db_session_to_test(setup_bd: AsyncEngine) -> AsyncSession:
    async_factory = async_sessionmaker(
        bind=setup_bd, expire_on_commit=False, autoflush=False, autocommit=False
    )

    async with async_factory() as sess:
        yield sess


@pytest_asyncio.fixture()
async def init_db(db_session_to_test) -> dict:
    # --- Подготовка данных ---
    wc = WorkCenters(name="WC1")
    db_session_to_test.add(wc)
    await db_session_to_test.flush()  # чтобы wc.id появился

    shift = ShiftTasks(
        task_description="Test shift",
        is_closed=False,
        shift="A",
        brigade="B1",
        shift_start=datetime(2025, 9, 8, 8, 0, tzinfo=timezone.utc),
        shift_end=datetime(2025, 9, 8, 16, 0, tzinfo=timezone.utc),
        work_center_id=wc.id,
    )
    db_session_to_test.add(shift)
    await db_session_to_test.flush()

    batch = Batches(
        shift_task_id=shift.id,
        batch_number=101,
        ekn_code="EKN1",
        batch_date=date(2025, 9, 8),
        nomenclature="Nom1",
    )
    db_session_to_test.add(batch)
    await db_session_to_test.flush()

    product1 = Products(
        unique_code="P001",
        batch_id=batch.id,
        is_aggregated=False,
        created_at=datetime.now(timezone.utc),
    )
    product2 = Products(
        unique_code="P002",
        batch_id=batch.id,
        is_aggregated=True,
        aggregated_at=datetime.now(timezone.utc),
        created_at=datetime.now(timezone.utc),
    )
    db_session_to_test.add_all([product1, product2])
    await db_session_to_test.flush()
    await db_session_to_test.refresh(shift, attribute_names=["batches", "work_center"])
    await db_session_to_test.refresh(batch, attribute_names=["products"])
    await db_session_to_test.commit()

    models = {
        "work_center": wc,
        "shift": shift,
        "batch": batch,
        "product1": product1,
        "product2": product2,
    }

    yield models

    await db_session_to_test.delete(product1)
    await db_session_to_test.delete(product2)
    await db_session_to_test.delete(batch)
    await db_session_to_test.delete(shift)
    await db_session_to_test.delete(wc)
    await db_session_to_test.commit()


@pytest_asyncio.fixture()
async def init_db_to_add_product_to_batch(db_session_to_test, init_db) -> dict:
    shift_task = init_db["shift"]
    batch1 = Batches(
        shift_task_id=shift_task.id,
        batch_number=111,
        batch_date=date(2025, 9, 9),
        nomenclature="Nom1",
        ekn_code="EKN1",
    )
    batch2 = Batches(
        shift_task_id=shift_task.id,
        batch_number=222,
        batch_date=date(2025, 9, 10),
        nomenclature="Nom2",
        ekn_code="EKN2",
    )

    db_session_to_test.add_all((batch2, batch1))
    await db_session_to_test.commit()

    yield {"batch1": batch1, "batch2": batch2, **init_db}

    await db_session_to_test.delete(batch2)
    await db_session_to_test.delete(batch1)
    await db_session_to_test.commit()


@pytest_asyncio.fixture()
def product_controller_service_intgr(db_session):
    return ProductControllerService(
        session=db_session,
        product_repo=ProductsRepo(session=db_session),
        batche_repo=BatchesRepo(session=db_session),
        shift_task_repo=ShiftTasksRepo(session=db_session),
        work_center=WorkCentersRepo(session=db_session),
    )
