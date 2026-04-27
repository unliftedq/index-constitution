#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

cd "$ROOT_DIR"

rm -rf dist/
python -m build
python -m twine check dist/*
python -m twine upload --repository testpypi dist/*

echo "Uploaded to TestPyPI successfully."
