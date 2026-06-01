#!/usr/bin/env bash
set -euo pipefail

cd "$(dirname "$0")/.."

mkdir -p artifacts

generate_branch() {
  local label="$1"
  local block="$2"
  local stem="artifacts/problem835_e1_g4_branch_${label}"

  python3 -m src.extension_ladder opb \
    --v 21 \
    --t 4 \
    --extension-count 1 \
    --symmetry-break triple-matching-off-triple \
    --force-d-block "$block" \
    --add-d-lower-counts \
    --add-g4-counts \
    --no-comments \
    --output "${stem}.opb"

  sha256sum "${stem}.opb" > "${stem}.opb.sha256"
}

generate_branch a "0,1,3,6,8"
generate_branch b "0,1,3,6,9"
