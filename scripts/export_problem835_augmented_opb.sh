#!/usr/bin/env bash
set -euo pipefail

cd "$(dirname "$0")/.."

mkdir -p artifacts

python3 -m src.erdos835_one_color stats --json > artifacts/problem835_stats.json
python3 -m src.erdos835_one_color opb \
  --v 21 \
  --t 4 \
  --extension-count 11 \
  --no-row-comments \
  --no-column-comments \
  --symmetry-break triple-matching \
  --add-g4-counts \
  --add-d-lower-counts \
  --output artifacts/problem835_one_color_augmented.opb

ls -lh artifacts/problem835_stats.json artifacts/problem835_one_color_augmented.opb
wc -l artifacts/problem835_one_color_augmented.opb
sha256sum artifacts/problem835_one_color_augmented.opb
