#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
COMPOSE_ENV="$SCRIPT_DIR/deploy.compose.env"
COMPOSE_FILE="$SCRIPT_DIR/compose.app.yml"

docker compose --env-file "$COMPOSE_ENV" -f "$COMPOSE_FILE" up -d worker "$@"
