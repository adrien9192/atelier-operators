#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")"
export $(grep -v '^#' .env | xargs)
exec uvicorn app:app --host 0.0.0.0 --port 8030
