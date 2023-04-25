########################################################################################################################
######## Build base - docker dependencies
########################################################################################################################
FROM python:3.11.8-bookworm as build-base

RUN apt update && \
    apt install -yq \
        python3 \
        python3-pip \
        python-is-python3 \
        python3-ipython \
        podman \
        wget \
        gcc \
        g++ \
        tar \
        gzip \
        zip \
        make
ENV TERM xterm

WORKDIR /opt/big_salad
COPY requirements ./requirements/

########################################################################################################################
######## python pinner - container for pinning requirements
########################################################################################################################
FROM build-base as python-pinner
COPY pyproject.toml .
RUN mkdir -p /opt/big_salad/src \
    && pip install \
    --no-cache-dir \
    -r requirements/build.txt

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

COPY pyproject.toml .
COPY README.md .
COPY src ./src
COPY tests ./tests
RUN pip install -e .
ENV IN_DOCKER=true

########################################################################################################################
######## Dev - test image
########################################################################################################################
FROM dev-base as dev

COPY pyproject.toml .
COPY README.md .
COPY src ./src
COPY tests ./tests
RUN pip install \
    -e \
    .[dev]

ENV IN_DOCKER=true
