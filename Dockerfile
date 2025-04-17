FROM python:3.11-slim

# Prevents poetry from asking for input
ENV POETRY_VERSION=1.8.2
ENV POETRY_NO_INTERACTION=1
ENV POETRY_VIRTUALENVS_CREATE=false
ENV PATH="/root/.local/bin:$PATH"

# Install system dependencies
RUN apt-get update && apt-get install -y curl build-essential && \
    curl -sSL https://install.python-poetry.org | python3 - && \
    apt-get remove --purge -y curl && \
    rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Copy lock + pyproject first (cache layer)
COPY pyproject.toml poetry.lock* /app/

RUN poetry install --no-root

# Now copy the full source code
COPY . /app

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
