from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from src.backend.core.crud import (
    BatchesRepo,
    ProductsRepo,
    ShiftTasksRepo,
    WorkCentersRepo,
)
from src.backend.product_controler.services import ProductControllerService
from src.backend.core.db.Database import db


def get_batches_repo(session: AsyncSession = Depends(db.get_session)):
    return BatchesRepo(session=session)


def get_products_repo(session: AsyncSession = Depends(db.get_session)):
    return ProductsRepo(session=session)


def get_shift_tasks_repo(session: AsyncSession = Depends(db.get_session)):
    return ShiftTasksRepo(session=session)


def get_work_centers_repo(session: AsyncSession = Depends(db.get_session)):
    return WorkCentersRepo(session=session)


def get_product_controller_service(
    session: AsyncSession = Depends(db.get_session),
    batches_repo=Depends(get_batches_repo),
    shift_tasks_repo=Depends(get_shift_tasks_repo),
    work_centers_repo=Depends(get_work_centers_repo),
    products_repo=Depends(get_products_repo),
):
    return ProductControllerService(
        session=session,
        shift_task_repo=shift_tasks_repo,
        product_repo=products_repo,
        work_center=work_centers_repo,
        batche_repo=batches_repo,
    )
