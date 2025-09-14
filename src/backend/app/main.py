from fastapi import FastAPI

from src.backend.core.exceptions.handler import (
    register_exception_handlers,
)
from src.backend.product_controler.app.router import product_controller_router

app = FastAPI(
    title="LibraryBook",
    description="API documentation for library_book",
    version="1.0.0",
    openapi_url="/api/openapi.json",
    docs_url="/api/docs",  # Путь для Swagger UI
    redoc_url="/api/redoc",  # Путь для Redoc UI
)
app.include_router(product_controller_router)
register_exception_handlers(app)
