#!/usr/bin/env bash
set -euo pipefail

cd "$(dirname "$0")/.."

mkdir -p artifacts/solver_logs

solver="${SOLVER:-artifacts/solvers/roundingsat}"
input="${INPUT:-artifacts/problem835_one_color_augmented.opb}"
time_limit_seconds="${TIME_LIMIT_SECONDS:-21600}"
log="${LOG:-artifacts/solver_logs/augmented_one_colour_roundingsat_lp0_6h.log}"
ulimit_v_kb="${ULIMIT_V_KB:-27262976}"

if [[ ! -x "$solver" ]]; then
  echo "solver not executable: $solver" >&2
  exit 2
fi

if [[ ! -f "$input" ]]; then
  echo "input not found: $input" >&2
  exit 2
fi

ulimit -v "$ulimit_v_kb"
/usr/bin/time -v "$solver" \
  --lp=0 \
  --time-limit="$time_limit_seconds" \
  --print-sol=1 \
  "$input" > "$log" 2>&1
