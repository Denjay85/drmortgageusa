#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
FUNNEL_DIR="$ROOT_DIR/funnels/refiwatch"

cd "$FUNNEL_DIR"
rm -rf dist
npm ci
npm run build

echo "RefiWatch funnel build refreshed at $FUNNEL_DIR/dist/public"
