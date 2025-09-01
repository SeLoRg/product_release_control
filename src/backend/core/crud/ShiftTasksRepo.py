from src.backend.core.crud import CrudDB
from src.backend.core.models import ShiftTasks
from sqlalchemy.ext.asyncio import AsyncSession


class ShiftTasksRepo(CrudDB[ShiftTasks]):
    def __init__(self, session: AsyncSession):
        super().__init__(model=ShiftTasks, session=session)
