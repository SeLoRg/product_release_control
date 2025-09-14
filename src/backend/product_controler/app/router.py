from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException
from src.backend.product_controler.services import ProductControllerService
from src.backend.product_controler.schemas.schemas import (
    ShiftTaskIn,
    ShiftTaskSchema,
    ShiftTaskSchemaAll,
    ShiftTaskUpdate,
    ValuesToSort,
    ProductsIn,
)
from src.backend.core.dependencies import get_product_controller_service


product_controller_router = APIRouter(
    tags=["product_controller"], prefix="/product-controller"
)
product_controller_service = Annotated[
    ProductControllerService, Depends(get_product_controller_service)
]


@product_controller_router.post("/shift_task/", response_model=ShiftTaskSchema)
async def add_shift_task(
    data: ShiftTaskIn, product_controller: product_controller_service
):
    return await product_controller.shift_task_add(shift_task_data_in=data)


@product_controller_router.get(
    "/shift_task/{shift_task_id}", response_model=ShiftTaskSchemaAll
)
async def get_shift_task(
    shift_task_id: int,
    product_controller: product_controller_service,
    limit: int = 100,
    offset: int = 0,
):
    return_value = await product_controller.shift_task_get_by_id(
        shift_task_id=shift_task_id, limit=limit, skip=offset
    )

    if return_value is None:
        raise HTTPException(status_code=404, detail="Not founded")

    return return_value


@product_controller_router.patch(
    "/shift_task/{shift_task_id}", response_model=ShiftTaskSchema
)
async def update_shift_task(
    shift_task_id: int,
    data_in: ShiftTaskUpdate,
    product_controller: product_controller_service,
):
    return await product_controller.partial_update_shift_task_by_id(
        shift_task_id=shift_task_id, shift_task_update_in=data_in
    )


@product_controller_router.post(
    "/shift_task/list", response_model=list[ShiftTaskSchema]
)
async def get_shift_tasks_list(
    product_controller: product_controller_service, data: ValuesToSort
):
    return await product_controller.get_shift_tasks_list(
        values_to_sort=data.values_to_sort,
        offset=data.offset,
        limit=data.limit,
        filters=data.filters,
    )


@product_controller_router.post("/product/", response_model=list[ProductsIn])
async def add_product(
    product_controller: product_controller_service, data: list[ProductsIn]
):
    return await product_controller.add_product_to_batch(products_to_add=data)


@product_controller_router.put("/product/{batch_id}", status_code=200)
async def aggregate_product(
    product_controller: product_controller_service, batch_id: int, unique_code: str
):
    await product_controller.aggregate_product(
        batch_id=batch_id, unique_code=unique_code
    )
    return {"status": "ok"}
