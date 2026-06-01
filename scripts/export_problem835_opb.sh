#!/usr/bin/env bash
set -euo pipefail

mkdir -p artifacts

python3 -m src.erdos835_one_color stats --json > artifacts/problem835_stats.json
python3 -m src.erdos835_one_color opb \
  --v 21 \
  --t 4 \
  --extension-count 11 \
  --no-row-comments \
  --no-column-comments \
  --output artifacts/problem835_one_color.opb

ls -lh artifacts/problem835_stats.json artifacts/problem835_one_color.opb
