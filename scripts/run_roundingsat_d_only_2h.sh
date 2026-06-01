#!/usr/bin/env bash
set -euo pipefail

cd "$(dirname "$0")/.."

: "${TIME_LIMIT_SECONDS:=7200}"
: "${LOG:=artifacts/solver_logs/d_only_roundingsat_lp0_2h.log}"

mkdir -p "$(dirname "$LOG")"

/usr/bin/time -v artifacts/solvers/roundingsat \
  --lp=0 \
  "--time-limit=${TIME_LIMIT_SECONDS}" \
  --print-sol=1 \
  artifacts/problem835_d_only.opb \
  > "$LOG" 2>&1
