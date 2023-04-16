########################################################################################################################
######## Build base - docker dependencies
########################################################################################################################
FROM python:3.11-slim as build-base

RUN apt-get update \
    && apt-get install -y \
      build-essential

WORKDIR /opt
COPY requirements ./requirements/
COPY pyproject.toml .
COPY README.md .

########################################################################################################################
######## python pinner - container for pinning requirements
########################################################################################################################
FROM build-base as python-pinner

RUN mkdir -p /opt/src \
    && pip install \
    --no-cache-dir \
    .[build]

########################################################################################################################
######## Relase base - pip dependencies for runtime
########################################################################################################################
FROM build-base as release-base
RUN pip install \
    --no-cache-dir \
    -r requirements/main.txt

########################################################################################################################
######## Dev base - pip dependencies for testing
########################################################################################################################
FROM release-base as dev-base
RUN pip install \
    --no-cache-dir \
    -r requirements/dev.txt

########################################################################################################################
######## Release - runtime image
########################################################################################################################
FROM release-base as release

COPY src ./src
COPY tests ./tests
RUN pip install .

########################################################################################################################
######## Dev - test image
########################################################################################################################
FROM dev-base as dev

COPY src ./src
COPY tests ./tests
RUN pip install \
    --no-cache-dir \
    .[dev]