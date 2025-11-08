from src.backend.core.crud import CrudDB
from src.backend.core.models import Products
from sqlalchemy.ext.asyncio import AsyncSession


class ProductsRepo(CrudDB[Products]):
    def __init__(self, session: AsyncSession):
        super().__init__(model=Products, session=session)
