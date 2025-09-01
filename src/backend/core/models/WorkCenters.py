from sqlalchemy import String
from sqlalchemy.orm import mapped_column, Mapped, relationship
from src.backend.core.models import Base, ShiftTasks


class WorkCenters(Base):
    __tablename__ = "work_centers"

    name: Mapped[str] = mapped_column(String(128), nullable=False)
    code: Mapped[str] = mapped_column(String(64), nullable=False, unique=True)

    shift_tasks: Mapped[list["ShiftTasks"]] = relationship(
        "ShiftTasks", back_populates="work_center"
    )
