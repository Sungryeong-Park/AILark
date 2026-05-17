#!/bin/bash

PROJECT_DIR="$(cd "$(dirname "$0")/.." && pwd)"

"$PROJECT_DIR/.venv/bin/python" "$PROJECT_DIR/src/main.py"
