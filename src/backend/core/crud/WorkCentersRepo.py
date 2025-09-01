from src.backend.core.crud import CrudDB
from src.backend.core.models import WorkCenters
from sqlalchemy.ext.asyncio import AsyncSession


class WorkCentersRepo(CrudDB[WorkCenters]):
    def __init__(self, session: AsyncSession):
        super().__init__(model=WorkCenters, session=session)
