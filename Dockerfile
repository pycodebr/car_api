FROM python:3.13.7-alpine3.22

WORKDIR /app
ENV PATH="${PATH}:/root/.local/bin"
ENV POETRY_VERSION=2.1.4

RUN apk add curl && \
    curl -sSL https://install.python-poetry.org | python3 -

COPY pyproject.toml poetry.lock /

RUN poetry install \
        --no-interaction \
        --no-root \
        --no-ansi \
        --without dev