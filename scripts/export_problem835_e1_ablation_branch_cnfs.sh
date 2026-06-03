#!/usr/bin/env bash
set -euo pipefail

cd "$(dirname "$0")/.."

: "${MODE:=all}"

mkdir -p artifacts

mode_flag() {
  case "$1" in
    d3) echo "--add-d3-upper-counts" ;;
    g4) echo "--add-g4-upper-counts" ;;
    *) echo "unsupported MODE $1" >&2; exit 2 ;;
  esac
}

generate_branch() {
  local mode="$1"
  local label="$2"
  local block="$3"
  local stem="artifacts/problem835_e1_${mode}_branch_${label}"
  local flag
  flag="$(mode_flag "$mode")"

  python3 -m src.extension_ladder_cnf stats \
    --v 21 \
    --t 4 \
    --extension-count 1 \
    --symmetry-break triple-matching-off-triple \
    --force-d-block "$block" \
    "$flag" \
    --json \
    > "${stem}_cnf_stats.json"

  python3 -m src.extension_ladder_cnf cnf \
    --v 21 \
    --t 4 \
    --extension-count 1 \
    --symmetry-break triple-matching-off-triple \
    --force-d-block "$block" \
    "$flag" \
    --output "${stem}.cnf"

  sha256sum "${stem}.cnf" > "${stem}.cnf.sha256"
}

generate_mode() {
  local mode="$1"
  generate_branch "$mode" a "0,1,3,6,8"
  generate_branch "$mode" b "0,1,3,6,9"
}

case "$MODE" in
  all)
    generate_mode d3
    generate_mode g4
    ;;
  d3|g4)
    generate_mode "$MODE"
    ;;
  *)
    echo "unsupported MODE $MODE" >&2
    exit 2
    ;;
esac
