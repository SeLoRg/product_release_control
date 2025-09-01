from src.backend.core.models import Base, WorkCenters, Batches
from sqlalchemy.orm import mapped_column, Mapped, relationship
from sqlalchemy import String, ForeignKey
from datetime import datetime


class ShiftTasks(Base):
    __tablename__ = "shift_tasks"

    task_description: Mapped[str] = mapped_column(String(128), nullable=False)
    is_closed: Mapped[bool] = mapped_column(nullable=False, default=False)
    closed_at: Mapped[datetime | None] = mapped_column(nullable=True, default=None)
    shift: Mapped[str] = mapped_column(nullable=False)
    brigade: Mapped[str] = mapped_column(nullable=False)
    shift_start: Mapped[datetime] = mapped_column(nullable=False)
    shift_end: Mapped[datetime] = mapped_column(nullable=False)

    work_center_id: Mapped[int] = mapped_column(
        ForeignKey("work_centers.id"), nullable=False
    )

    # Связи
    work_center: Mapped["WorkCenters"] = relationship(
        "WorkCenters", back_populates="shift_tasks"
    )
    batches: Mapped[list["Batches"]] = relationship(
        "Batches", back_populates="shift_task", cascade="all, delete-orphan"
    )
