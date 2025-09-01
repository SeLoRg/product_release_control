from sqlalchemy.orm import mapped_column, Mapped, relationship
from sqlalchemy import ForeignKey, String, Integer, UniqueConstraint
from src.backend.core.models import Base, ShiftTasks, Products
import datetime


class Batches(Base):
    __tablename__ = "batches"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    shift_task_id: Mapped[int] = mapped_column(
        ForeignKey("shift_tasks.id"), nullable=False
    )

    batch_number: Mapped[int] = mapped_column(nullable=False)
    batch_date: Mapped[datetime.date] = mapped_column(nullable=False)
    nomenclature: Mapped[str] = mapped_column(String(128), nullable=False)
    ekn_code: Mapped[str] = mapped_column(String(64), nullable=False)

    __table_args__ = (
        UniqueConstraint(
            "shift_task_id", "batch_number", "batch_date", name="uq_shift_batch"
        ),
    )

    # Связи
    shift_task: Mapped["ShiftTasks"] = relationship(
        "ShiftTasks", back_populates="batches"
    )
    products: Mapped[list["Products"]] = relationship(
        "Products", back_populates="batch", cascade="all, delete-orphan"
    )
