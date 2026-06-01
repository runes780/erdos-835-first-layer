#!/usr/bin/env bash
set -euo pipefail

cd "$(dirname "$0")/.."

mkdir -p artifacts

python3 -m src.extension_ladder opb \
  --v 21 \
  --t 4 \
  --extension-count 1 \
  --symmetry-break triple-matching-off-triple \
  --add-d-lower-counts \
  --no-comments \
  --output artifacts/problem835_e1.opb
