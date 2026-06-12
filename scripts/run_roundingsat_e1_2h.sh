#!/usr/bin/env bash
set -euo pipefail

cd "$(dirname "$0")/.."

: "${TIME_LIMIT_SECONDS:=7200}"
: "${SOLVER:=artifacts/solvers/roundingsat}"
: "${OPB:=artifacts/problem835_e1.opb}"
: "${LOG:=artifacts/solver_logs/e1_roundingsat_lp0_2h.log}"

mkdir -p "$(dirname "$LOG")"

/usr/bin/time -v "$SOLVER" \
  --lp=0 \
  "--time-limit=${TIME_LIMIT_SECONDS}" \
  --print-sol=1 \
  "$OPB" \
  > "$LOG" 2>&1
