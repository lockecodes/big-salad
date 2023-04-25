SHELL=bash
CONTAINER_NAME:=big-salad
VERSION:=$(shell git describe --tags --always)
PODMAN ?= false
PODMAN_COMPOSE ?= false
DOCKER:="$(shell if ${PODMAN}; then \
		echo podman; \
		else echo docker; \
	fi \
)"
DOCKER_COMPOSE:="$(shell if ${PODMAN_COMPOSE}; then \
		echo podman-compose; \
		else echo docker-compose; \
	fi \
)"

########################################################################################################################
########## Docker builds
########################################################################################################################
BUILD_TARGET ?= 'release'
.PHONY: build-config
build-config:
	VERSION=${VERSION} \
		${DOCKER_COMPOSE} \
		-f docker-compose.yaml \
		-f docker-compose.${BUILD_TARGET}.yaml \
		config

.PHONY: build-base
build-base:
	BUILD_TARGET='release-base' ${MAKE} build-config
	VERSION=${VERSION} \
		${DOCKER_COMPOSE} \
		-f docker-compose.yaml \
		-f docker-compose.release-base.yaml \
		build \
		bs

.PHONY: build-release
build-release:
	BUILD_TARGET='release' ${MAKE} build-config
	VERSION=latest \
		${DOCKER_COMPOSE} \
		-f docker-compose.yaml \
		-f docker-compose.release.yaml \
		build \
		bs

.PHONY: build-dev
build-dev:
	BUILD_TARGET='dev' ${MAKE} build-config
	VERSION=${VERSION} \
		${DOCKER_COMPOSE} \
		-f docker-compose.yaml \
		-f docker-compose.dev.yaml \
		build \
		bs

.PHONY: build-pinner
build-pinner:
	BUILD_TARGET='python-pinner' ${MAKE} build-config
	VERSION=${VERSION} \
		${DOCKER_COMPOSE} \
		-f docker-compose.yaml \
		-f docker-compose.python-pinner.yaml \
		build \
		bs

.PHONY: build
build: build-base build-release build-dev
	@echo "Built base -> release -> dev"


########################################################################################################################
########################################################################################################################
########################################################################################################################

########################################################################################################################
########## Local dev commands
########################################################################################################################

.PHONY: lint
lint:
	VERSION=${VERSION} \
		${DOCKER_COMPOSE} \
			-f docker-compose.yaml \
			-f docker-compose.dev.yaml \
			run \
			--rm \
			bs \
			bash -c "black \
				--config /opt/big_salad/pyproject.toml . \
				&& pylint --recursive=y \
				/opt/big_salad/src /opt/big_salad/tests"

.PHONY: shell
shell:
	VERSION=${VERSION} \
		${DOCKER_COMPOSE} \
		-f docker-compose.yaml \
		-f docker-compose.dev.yaml \
		run \
			--rm \
			bs \
			bash

.PHONY: test
test:
	VERSION=${VERSION} \
		${DOCKER_COMPOSE} \
			-f docker-compose.yaml \
			-f docker-compose.dev.yaml \
			run \
			--rm \
			bs \
			/bin/bash -c "coverage run \
			-m pytest -v tests \
			&& coverage report \
			&& coverage xml \
			&& coverage html"

########################################################################################################################
########### End local dev targets
########################################################################################################################

########################################################################################################################
########### Update python pins targets
########################################################################################################################

.PHONY: update-pins
update-pins: build-pinner # update the dependency pins
	VERSION=${VERSION} \
		${DOCKER_COMPOSE} \
		-f docker-compose.yaml \
		-f docker-compose.python-pinner.yaml \
		run \
			--rm \
			bs \
			/bin/bash -c "python -m piptools compile \
				--upgrade \
				--resolver backtracking \
				-o requirements/main.txt \
				--verbose \
				pyproject.toml \
			&& python -m piptools compile \
				--extra dev \
				--upgrade \
				--resolver backtracking \
				-o requirements/dev.txt \
				--verbose \
				pyproject.toml \
			&& python -m pip install \
				--upgrade \
				-r requirements/main.txt \
				-r requirements/dev.txt \
				--verbose \
				-e . \
			&& python -m pip check"

########################################################################################################################
########### End update python pins
########################################################################################################################
