#!/usr/bin/env bash
set -euo pipefail

cd "$(dirname "$0")/.."

mkdir -p artifacts

generate_branch() {
  local label="$1"
  local first_block="$2"
  local second_block="$3"
  local stem="artifacts/problem835_e2_d3_terminal_${label}"

  python3 -m src.extension_ladder_cnf stats \
    --v 21 \
    --t 4 \
    --extension-count 2 \
    --symmetry-break triple-matching-off-triple \
    --force-d-block "$first_block" \
    --force-d-block "$second_block" \
    --add-d3-upper-counts \
    --json \
    > "${stem}_cnf_stats.json"

  python3 -m src.extension_ladder_cnf cnf \
    --v 21 \
    --t 4 \
    --extension-count 2 \
    --symmetry-break triple-matching-off-triple \
    --force-d-block "$first_block" \
    --force-d-block "$second_block" \
    --add-d3-upper-counts \
    --output "${stem}.cnf"

  sha256sum "${stem}.cnf" > "${stem}.cnf.sha256"
}

generate_branch a_star "0,1,3,6,8" "0,1,3,9,11"
generate_branch b1 "0,1,3,6,9" "0,1,3,8,10"
generate_branch b2 "0,1,3,6,9" "0,1,3,8,11"
