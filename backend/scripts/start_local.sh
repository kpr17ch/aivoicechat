#!/usr/bin/env bash

# Local development launcher for the FastAPI backend.

set -Eeuo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
BACKEND_DIR="$(cd "${SCRIPT_DIR}/.." && pwd)"
REPO_ROOT="$(cd "${BACKEND_DIR}/.." && pwd)"
VENV_DIR="${BACKEND_DIR}/.venv"
PYTHON_BIN="${PYTHON_BIN:-python3}"
HASH_FILE="${VENV_DIR}/.requirements-hash"

cd "${BACKEND_DIR}"

if ! command -v "${PYTHON_BIN}" >/dev/null 2>&1; then
  echo "Python executable '${PYTHON_BIN}' not found. Set PYTHON_BIN to a valid interpreter." >&2
  exit 1
fi

if [ ! -d "${VENV_DIR}" ]; then
  echo "[backend] Creating virtual environment at ${VENV_DIR}"
  "${PYTHON_BIN}" -m venv "${VENV_DIR}"
fi

# shellcheck disable=SC1091
source "${VENV_DIR}/bin/activate"

if ! command -v shasum >/dev/null 2>&1; then
  echo "The 'shasum' command is required but not available on this system." >&2
  exit 1
fi

REQUIREMENTS_HASH="$(shasum -a 256 requirements.txt | awk '{print $1}')"
SHOULD_INSTALL_DEPS=true
if [ -f "${HASH_FILE}" ] && [ "$(cat "${HASH_FILE}")" = "${REQUIREMENTS_HASH}" ]; then
  SHOULD_INSTALL_DEPS=false
fi

if ${SHOULD_INSTALL_DEPS}; then
  echo "[backend] Installing Python dependencies"
  python -m pip install --upgrade pip >/dev/null
  pip install --quiet -r requirements.txt
  echo "${REQUIREMENTS_HASH}" > "${HASH_FILE}"
fi

export PYTHONPATH="${BACKEND_DIR}${PYTHONPATH:+:${PYTHONPATH}}"
export REPO_ROOT

python "${BACKEND_DIR}/scripts/ensure_local_db.py"

echo "[backend] Running migrations"
alembic -c "${BACKEND_DIR}/alembic.ini" upgrade head

PORT="${PORT:-8000}"
HOST="${HOST:-0.0.0.0}"

echo "[backend] Starting uvicorn on ${HOST}:${PORT}"
exec uvicorn app.main:app --reload --host "${HOST}" --port "${PORT}"
