#!/usr/bin/env bash
set -euo pipefail

cd "$(dirname "$0")/.."

python3 -m src.erdos835_one_color d-only-opb \
  --output artifacts/problem835_d_only.opb \
  --symmetry-break triple-matching \
  --add-d-lower-counts \
  --no-comments
