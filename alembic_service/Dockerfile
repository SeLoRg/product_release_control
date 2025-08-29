FROM python:3.13-slim-bookworm

RUN pip install --upgrade pip && pip install poetry

WORKDIR /alembic_service

COPY pyproject.toml poetry.lock* ./
RUN poetry config virtualenvs.create false && poetry install

COPY alembic_service .

WORKDIR /src
COPY src/backend/core/models ./backend/core/models
COPY src/backend/core/configs ./backend/core/configs


WORKDIR /alembic_service
