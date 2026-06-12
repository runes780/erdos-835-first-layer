#!/usr/bin/env bash
set -euo pipefail

cd "$(dirname "$0")/.."

mkdir -p artifacts

python3 -m src.extension_ladder_cnf stats \
  --v 21 \
  --t 4 \
  --extension-count 1 \
  --symmetry-break triple-matching-off-triple \
  --json \
  > artifacts/problem835_e1_cnf_stats.json

python3 -m src.extension_ladder_cnf cnf \
  --v 21 \
  --t 4 \
  --extension-count 1 \
  --symmetry-break triple-matching-off-triple \
  --output artifacts/problem835_e1.cnf

sha256sum artifacts/problem835_e1.cnf > artifacts/problem835_e1.cnf.sha256
