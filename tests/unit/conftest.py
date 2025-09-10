import pytest
from unittest.mock import AsyncMock
from sqlalchemy.ext.asyncio import AsyncSession

from src.backend.product_controler.services.ProductControllerService import (
    ProductControllerService,
)


@pytest.fixture
def mock_session():
    """Мокаем асинхронную сессию SQLAlchemy"""
    return AsyncMock(spec=AsyncSession)


@pytest.fixture
def mock_repos():
    """Мокаем все репозитории разом"""
    return {
        "shift_task_repo": AsyncMock(),
        "product_repo": AsyncMock(),
        "work_center_repo": AsyncMock(),
        "batche_repo": AsyncMock(),
    }


@pytest.fixture
def product_controller_service(mock_session, mock_repos):
    """Сервис с замоканными зависимостями"""
    return ProductControllerService(
        session=mock_session,
        shift_task_repo=mock_repos["shift_task_repo"],
        product_repo=mock_repos["product_repo"],
        work_center=mock_repos["work_center_repo"],
        batche_repo=mock_repos["batche_repo"],
    )
