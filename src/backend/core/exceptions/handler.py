from fastapi import FastAPI
from fastapi.responses import JSONResponse
from src.backend.product_controler.exceptions.exceptions import (
    UniqueCodeNotFoundError,
    UniqueCodeAlreadyUsedError,
    UniqueCodeAttachedToAnotherBatchError,
)


def register_exception_handlers(app: FastAPI) -> None:
    """Регистрация всех кастомных и базовых обработчиков ошибок"""

    handlers = [
        (
            UniqueCodeNotFoundError,
            lambda req, exc: JSONResponse(
                status_code=404, content={"detail": str(exc)}
            ),
        ),
        (
            UniqueCodeAlreadyUsedError,
            lambda req, exc: JSONResponse(
                status_code=400,
                content={"detail": f"Unique code already used at {exc.aggregated_at}"},
            ),
        ),
        (
            UniqueCodeAttachedToAnotherBatchError,
            lambda req, exc: JSONResponse(
                status_code=400, content={"detail": str(exc)}
            ),
        ),
        (
            ValueError,
            lambda req, exc: JSONResponse(
                status_code=422, content={"detail": f"Invalid input: {str(exc)}"}
            ),
        ),
        (
            Exception,
            lambda req, exc: JSONResponse(
                status_code=500, content={"detail": "Internal server error"}
            ),
        ),
    ]

    for exc_class, handler_func in handlers:
        app.add_exception_handler(exc_class, handler_func)
