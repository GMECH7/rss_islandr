#!/usr/bin/env bash
# Runs inside the build container (see build_installer/docker/Dockerfile.build): builds the .deb from a clean copy of /src
# and copies it to /src/dist.
set -euo pipefail

export HOME=/tmp/home
export POETRY_VIRTUALENVS_IN_PROJECT=false
export POETRY_VIRTUALENVS_PATH=/tmp/venvs
WORK_DIR=/tmp/work
mkdir -p "$HOME" "$WORK_DIR"

tar -C /src --exclude=.venv --exclude=dist --exclude=build --exclude=.git --exclude=__pycache__ \
    --exclude=.cov_files --exclude=.pytest_cache -cf - . | tar -C "$WORK_DIR" -xf -
cd "$WORK_DIR"

poetry install --no-interaction
poetry run rss-build --deb

mkdir -p /src/dist
cp dist/*.deb /src/dist/
