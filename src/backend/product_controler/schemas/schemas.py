from datetime import datetime, date
from typing import Optional, List, Literal
from pydantic import BaseModel, ConfigDict, Field


# --- Вспомогательные схемы (для связей) ---


class ProductsSchema(BaseModel):
    unique_code: str
    is_aggregated: bool
    aggregated_at: Optional[datetime] = None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True, extra="ignore")


class ProductsIn(BaseModel):
    unique_code: str
    batch_number: int
    batch_date: date

    model_config = ConfigDict(extra="ignore")


class WorkCenterSchema(BaseModel):
    id: Optional[int] = None
    name: str

    model_config = ConfigDict(from_attributes=True, extra="ignore")


class BatchSchema(BaseModel):
    id: Optional[int] = None
    batch_number: int
    batch_date: date
    shift_task_id: Optional[int] = None
    ekn_code: str
    nomenclature: str

    model_config = ConfigDict(from_attributes=True, extra="ignore")


class BatchSchemaAll(BatchSchema):
    """Партия вместе с продуктами"""

    products: List[ProductsSchema] = []


# --- Основная схема ShiftTasks ---


class ShiftTaskBase(BaseModel):
    task_description: str
    is_closed: bool
    closed_at: Optional[datetime] = None
    shift: str
    brigade: str
    shift_start: datetime
    shift_end: datetime
    work_center_id: Optional[int] = None


class ShiftTaskCreate(ShiftTaskBase):
    """Схема для создания (без id, batches и work_center)"""

    pass


class ShiftTaskUpdate(BaseModel):
    """Схема для обновления"""

    task_description: Optional[str] = None
    is_closed: Optional[bool] = None
    shift: Optional[str] = None
    brigade: Optional[str] = None
    shift_start: Optional[datetime] = None
    shift_end: Optional[datetime] = None


class ShiftTaskSchema(ShiftTaskBase):
    """Полная схема для возврата"""

    id: int
    work_center: Optional[WorkCenterSchema] = None
    batches: List[BatchSchema] = []

    model_config = ConfigDict(from_attributes=True, extra="ignore")


class ShiftTaskSchemaAll(ShiftTaskSchema):
    """Полная схема для возврата со всеми партиями и продуктами"""

    batches: List[BatchSchemaAll] = []


class ShiftTaskIn(BaseModel):
    is_closed: bool  # СтатусЗакрытия
    task_description: str  # ПредставлениеЗаданияНаСмену
    work_center: str  # Рабочий центр
    shift: str  # Смена
    brigade: str  # Бригада
    batch_number: int  # НомерПартии
    ekn_code: str
    batch_date: date  # ДатаПартии
    nomenclature: str  # Номенклатура
    shift_start: datetime  # ДатаВремяНачалаСмены
    shift_end: datetime  # ДатаВремяОкончанияСмены


# ------------- Схемы для роутера------------------


class ShiftTaskFilters(BaseModel):
    task_description: Optional[str] = Field(
        None, json_schema_extra={"example": "Упаковка"}
    )
    is_closed: Optional[bool] = Field(None, json_schema_extra={"example": False})
    closed_at: Optional[datetime] = Field(
        None, json_schema_extra={"example": "2025-09-14T10:00:00Z"}
    )
    shift: Optional[str] = Field(None, json_schema_extra={"example": "Ночная"})
    brigade: Optional[str] = Field(None, json_schema_extra={"example": "Бригада 1"})
    shift_start: Optional[datetime] = Field(
        None, json_schema_extra={"example": "2025-09-14T08:00:00Z"}
    )
    shift_end: Optional[datetime] = Field(
        None, json_schema_extra={"example": "2025-09-14T20:00:00Z"}
    )
    work_center_id: Optional[int] = Field(None, json_schema_extra={"example": 5})


class ValuesToSort(BaseModel):
    values_to_sort: Optional[dict[str, Literal["desc", "asc"]]] = Field(
        None, json_schema_extra={"example": {"shift_start": "desc"}}
    )
    offset: int = 0
    limit: int = 100
    filters: Optional[ShiftTaskFilters] = None
