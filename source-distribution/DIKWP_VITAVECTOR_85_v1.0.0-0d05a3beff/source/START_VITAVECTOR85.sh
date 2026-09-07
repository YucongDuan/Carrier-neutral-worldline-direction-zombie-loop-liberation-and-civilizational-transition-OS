#!/usr/bin/env sh
set -eu
cd "$(dirname "$0")"
PYTHON=${PYTHON:-python3}
command -v "$PYTHON" >/dev/null 2>&1 || PYTHON=python
exec "$PYTHON" start_showcase.py "$@"
