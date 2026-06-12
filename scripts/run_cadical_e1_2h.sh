#!/usr/bin/env bash
set -euo pipefail

cd "$(dirname "$0")/.."

: "${TIME_LIMIT_SECONDS:=7200}"
: "${SOLVER:=artifacts/solvers/cadical_pkg/usr/bin/cadical}"
: "${CNF:=artifacts/problem835_e1.cnf}"
: "${LOG:=artifacts/solver_logs/e1_cadical_2h.log}"

mkdir -p "$(dirname "$LOG")"

/usr/bin/time -v timeout "${TIME_LIMIT_SECONDS}" "$SOLVER" "$CNF" \
  > "$LOG" 2>&1
