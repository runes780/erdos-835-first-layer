#!/usr/bin/env bash
set -euo pipefail

cd "$(dirname "$0")/.."

: "${BRANCH:=a}"
: "${TIME_LIMIT_SECONDS:=3600}"
: "${SOLVER:=artifacts/solvers/roundingsat}"
: "${OPB:=artifacts/problem835_e1_g4_branch_${BRANCH}.opb}"
: "${LOG:=artifacts/solver_logs/e1_g4_branch_${BRANCH}_roundingsat_lp0_1h.log}"

mkdir -p "$(dirname "$LOG")"

/usr/bin/time -v "$SOLVER" \
  --lp=0 \
  "--time-limit=${TIME_LIMIT_SECONDS}" \
  --print-sol=1 \
  "$OPB" \
  > "$LOG" 2>&1
