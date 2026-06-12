#!/usr/bin/env bash
set -euo pipefail

cd "$(dirname "$0")/.."

: "${BRANCH:=a_star}"
: "${TIME_LIMIT_SECONDS:=7200}"
: "${SOLVER:=artifacts/solvers/kissat}"
: "${CNF:=artifacts/problem835_e1_d3_terminal_${BRANCH}.cnf}"
: "${LOG:=artifacts/solver_logs/e1_d3_terminal_${BRANCH}_kissat_2h.log}"

case "$BRANCH" in
  a_star|b1|b2) ;;
  *) echo "unsupported BRANCH $BRANCH" >&2; exit 2 ;;
esac

mkdir -p "$(dirname "$LOG")"

/usr/bin/time -v timeout "${TIME_LIMIT_SECONDS}" "$SOLVER" -s "$CNF" \
  > "$LOG" 2>&1
