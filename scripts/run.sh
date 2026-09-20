#!/usr/bin/env bash
# Starts the Doculyze backend (FastAPI, :8000) and frontend (Vite dev
# server, :5173) together, and stops both on Ctrl+C.
#
# Assumes you've already run, once:
#   cd backend  && python3 -m venv venv && venv/bin/pip install -r requirements.txt
#   cd frontend && npm install
# and copied backend/.env.example -> backend/.env with a real GROQ_API_KEY.

set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
BACKEND_DIR="$ROOT_DIR/backend"
FRONTEND_DIR="$ROOT_DIR/frontend"

PYTHON_BIN="$BACKEND_DIR/venv/bin/python"
if [ ! -x "$PYTHON_BIN" ]; then
  echo "No virtualenv found at backend/venv — falling back to system python3."
  echo "(Run 'python3 -m venv venv' inside backend/ first for an isolated setup.)"
  PYTHON_BIN="python3"
fi

if [ ! -f "$BACKEND_DIR/.env" ]; then
  echo "backend/.env is missing. Copy backend/.env.example to backend/.env" >&2
  echo "and add your GROQ_API_KEY before running this script." >&2
  exit 1
fi

cleanup() {
  echo
  echo "Stopping..."
  kill "${BACKEND_PID:-}" "${FRONTEND_PID:-}" 2>/dev/null || true
}
trap cleanup EXIT INT TERM

echo "Starting backend on http://localhost:8000 ..."
(cd "$BACKEND_DIR" && "$PYTHON_BIN" -m uvicorn app:app --reload --port 8000) &
BACKEND_PID=$!

echo "Starting frontend on http://localhost:5173 ..."
(cd "$FRONTEND_DIR" && npm run dev) &
FRONTEND_PID=$!

wait
