from src.backend.core.crud import CrudDB
from src.backend.core.models import Batches
from sqlalchemy.ext.asyncio import AsyncSession


class BatchesRepo(CrudDB[Batches]):
    def __init__(self, session: AsyncSession):
        super().__init__(model=Batches, session=session)
