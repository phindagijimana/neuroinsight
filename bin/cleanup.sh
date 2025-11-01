#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "$0")/.." && pwd)"

echo "[CLEANUP] Removing Python caches..."
find "$ROOT_DIR" -type d -name __pycache__ -prune -exec rm -rf {} +

echo "[CLEANUP] Truncating log files (keeping files)..."
for f in "$ROOT_DIR"/logs/*.out; do
  [ -f "$f" ] && : > "$f" || true
done

echo "[CLEANUP] Removing empty temporary visualization folders..."
find "$ROOT_DIR/data/outputs" -type d -name "visualizations_new" -exec rm -rf {} + || true

echo "[CLEANUP] Done."





