from src.backend.core.models import Base, Batches
from sqlalchemy.orm import mapped_column, Mapped, relationship
from sqlalchemy import ForeignKey, func, DateTime, String, Boolean
import datetime


class Products(Base):
    __tablename__ = "products"

    unique_code: Mapped[str] = mapped_column(String(128), nullable=False, unique=True)
    batch_id: Mapped[int] = mapped_column(ForeignKey("batches.id"), nullable=False)
    is_aggregated: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)

    aggregated_at: Mapped[datetime.datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
        default=None,
    )

    created_at: Mapped[datetime.datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
        default=lambda: datetime.datetime.now(datetime.timezone.utc),
    )

    # связь
    batch: Mapped["Batches"] = relationship("Batches", back_populates="products")
