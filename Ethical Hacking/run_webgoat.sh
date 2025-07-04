#!/usr/bin/env bash
set -euo pipefail

# ─── CONFIG ────────────────────────────────────────────────────────────────

CONTAINER_NAME="webgoat"
IMAGE_NAME="webgoat/webgoat"
HOST_BIND_IP="127.0.0.1"
HTTP_PORT=8080
ADMIN_PORT=9090

# ─── CLEANUP FUNCTIONS ──────────────────────────────────────────────────────

cleanup_container() {
  # Stop & remove if a container with this name exists
  if docker ps -a --format '{{.Names}}' | grep -xq "${CONTAINER_NAME}"; then
    echo "Stopping existing container ${CONTAINER_NAME}…"
    docker stop "${CONTAINER_NAME}"
    echo "Removing existing container ${CONTAINER_NAME}…"
    docker rm "${CONTAINER_NAME}"
  fi
}

prune_unused() {
  echo "Pruning unused containers, networks, and dangling images…"
  docker container prune -f
  docker network prune   -f
  docker image  prune    -f
}

# ─── MAIN ───────────────────────────────────────────────────────────────────

echo "Fetching latest image ${IMAGE_NAME}…"
docker pull "${IMAGE_NAME}"

echo "Cleaning up old container if any…"
cleanup_container

# Optionally uncomment the next line if you want full prune each run:
# prune_unused

echo "Starting new container ${CONTAINER_NAME}…"
docker run -d \
  --name "${CONTAINER_NAME}" \
  --restart unless-stopped \
  -p "${HOST_BIND_IP}:${HTTP_PORT}:8080" \
  -p "${HOST_BIND_IP}:${ADMIN_PORT}:9090" \
  "${IMAGE_NAME}"

echo -e "\n✅ WebGoat is up and running!"
echo "   • UI: http://${HOST_BIND_IP}:${HTTP_PORT}/WebGoat"
echo "   • Admin: http://${HOST_BIND_IP}:${ADMIN_PORT}"
