#!/usr/bin/env bash
set -euo pipefail

IMAGE_NAME="trading-bot"
CONTAINER_NAME="trading-bot-run"

if [[ -n "${1:-}" ]]; then
  IMAGE_NAME="$1"
fi

DOCKER_BUILDKIT=1 docker build -t "$IMAGE_NAME" .

if docker ps -a --format '{{.Names}}' | grep -Eq "^${CONTAINER_NAME}$"; then
  docker rm -f "$CONTAINER_NAME" >/dev/null
fi

docker run --name "$CONTAINER_NAME" --rm "$IMAGE_NAME"
