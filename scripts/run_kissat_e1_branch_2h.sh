#!/usr/bin/env bash
set -euo pipefail

cd "$(dirname "$0")/.."

: "${BRANCH:=a}"
: "${TIME_LIMIT_SECONDS:=7200}"
: "${SOLVER:=artifacts/solvers/kissat}"
: "${CNF:=artifacts/problem835_e1_branch_${BRANCH}.cnf}"
: "${LOG:=artifacts/solver_logs/e1_kissat_branch_${BRANCH}_2h.log}"

mkdir -p "$(dirname "$LOG")"

/usr/bin/time -v timeout "${TIME_LIMIT_SECONDS}" "$SOLVER" -s "$CNF" \
  > "$LOG" 2>&1
