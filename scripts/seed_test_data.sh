#!/usr/bin/env bash
# Uploads every file in docs/sample-documents/ straight to the local
# backend's /upload endpoint — useful for testing the pipeline without
# going through the frontend UI.
#
# Usage: ./seed_test_data.sh [api-base-url]
#   defaults to http://localhost:8000

set -euo pipefail

API_BASE="${1:-http://localhost:8000}"
SAMPLES_DIR="$(dirname "$0")/../docs/sample-documents"

if ! curl -sf "${API_BASE}/health" > /dev/null; then
  echo "Couldn't reach ${API_BASE}/health — is the backend running?" >&2
  echo "(cd backend && uvicorn app:app --port 8000)" >&2
  exit 1
fi

shopt -s nullglob
files=("$SAMPLES_DIR"/*.pdf "$SAMPLES_DIR"/*.png "$SAMPLES_DIR"/*.jpg "$SAMPLES_DIR"/*.jpeg "$SAMPLES_DIR"/*.txt)

if [ ${#files[@]} -eq 0 ]; then
  echo "No sample documents found in $SAMPLES_DIR — add a few files first."
  exit 1
fi

for file in "${files[@]}"; do
  name="$(basename "$file")"
  b64="$(base64 -w0 "$file" 2>/dev/null || base64 "$file")"

  echo "==> Uploading ${name}"
  response="$(curl -sf -X POST "${API_BASE}/upload" \
    -H "Content-Type: application/json" \
    -d "{\"file\": \"${b64}\", \"file_name\": \"${name}\"}")"

  doc_id="$(echo "$response" | python3 -c 'import sys,json; print(json.load(sys.stdin)["documentId"])')"
  echo "    started processing, documentId=${doc_id}"
  echo "    check it with: curl ${API_BASE}/result/${doc_id}"
done
