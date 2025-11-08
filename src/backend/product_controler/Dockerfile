FROM python:3.13-slim

WORKDIR /app

COPY poetry.lock pyproject.toml ./
RUN pip install --upgrade pip && pip install poetry \
    && poetry config virtualenvs.create false \
    && poetry install --no-root --only main

COPY src ./src

CMD ["uvicorn", "src.backend.app.main:app", "--host", "0.0.0.0", "--port", "8000"]
