FROM python:3.13.7-alpine3.22

ARG APPNAME=carapi

SHELL ["/bin/sh", "-o", "pipefail", "-c"]
ENV PATH="${PATH}:/home/${APPNAME}/.local/bin"\
    POETRY_VERSION=2.1.4 \
    POETRY_VIRTUALENVS_IN_PROJECT=true \
    POETRY_NO_INTERACTION=1

RUN apk add --no-cache \
        curl=8.14.1-r1 && \
    adduser -s /bin/sh -D ${APPNAME}

USER ${APPNAME}
WORKDIR /home/${APPNAME}

RUN curl -sSL https://install.python-poetry.org | python3 -

COPY pyproject.toml poetry.lock ./

RUN poetry install \
        --no-root \
        --no-ansi \
        --without dev

COPY . .

CMD ["poetry", "run", "fastapi", "dev", "--host", "0.0.0.0", "car_api/app.py"]
