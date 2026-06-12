#!/usr/bin/env bash
set -euo pipefail

cd "$(dirname "$0")/.."

: "${MODE:=d3}"
: "${BRANCH:=a}"
: "${TIME_LIMIT_SECONDS:=7200}"
: "${SOLVER:=artifacts/solvers/kissat}"
: "${CNF:=artifacts/problem835_e1_${MODE}_branch_${BRANCH}.cnf}"
: "${LOG:=artifacts/solver_logs/e1_${MODE}_kissat_branch_${BRANCH}_2h.log}"

case "$MODE" in
  d3|g4) ;;
  *) echo "unsupported MODE $MODE" >&2; exit 2 ;;
esac

mkdir -p "$(dirname "$LOG")"

/usr/bin/time -v timeout "${TIME_LIMIT_SECONDS}" "$SOLVER" -s "$CNF" \
  > "$LOG" 2>&1
