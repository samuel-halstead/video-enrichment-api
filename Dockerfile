ARG BASE_IMAGE=python
ARG BASE_TAG=3.11.13-slim

FROM ${BASE_IMAGE}:${BASE_TAG}

# Set environment variables
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONFAULTHANDLER=1 \
    PYTHONHASHSEED=random \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    PIP_DEFAULT_TIMEOUT=100 \
    POETRY_VERSION=1.8.4 \
    POETRY_NO_INTERACTION=1 \
    POETRY_VIRTUALENVS_CREATE=0 \
    LANG=en_US.UTF-8 \
    LANGUAGE=en_US.UTF-8 \
    LC_ALL=en_US.UTF-8

RUN export DEBIAN_FRONTEND=noninteractive \
    && apt-get update \
    && apt-get install --no-install-recommends -y locales \
    && sed -i -e '/en_US.UTF-8/s/^# //g' /etc/locale.gen \
    && locale-gen \
    && rm -rf /var/lib/apt/lists/*

RUN pip install "poetry==$POETRY_VERSION"

RUN apt-get update \
    && apt-get install --no-install-recommends -y curl build-essential \
    jq

RUN pip install virtualenv==20.30.0

# copy project requirement files here to ensure they will be cached.
COPY poetry.lock pyproject.toml ./

# install runtime deps - uses $POETRY_VIRTUALENVS_IN_PROJECT internally
RUN poetry config virtualenvs.create false \
    && poetry install

# Add app
WORKDIR /usr/src/app
COPY . .

EXPOSE 8080

# Run
ENTRYPOINT ["bash", "entrypoint.sh"]
