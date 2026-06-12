#!/usr/bin/env bash
set -euo pipefail

cd "$(dirname "$0")/.."

python3 -m src.cadical_portfolio \
  --solver "${SOLVER:-artifacts/solvers/cadical_pkg/usr/bin/cadical}" \
  --input "${INPUT:-artifacts/problem835_e1.cnf}" \
  --time-limit "${TIME_LIMIT_SECONDS:-1800}" \
  --max-jobs "${MAX_JOBS:-5}" \
  --start-index "${START_INDEX:-0}" \
  --log-dir "${LOG_DIR:-artifacts/solver_logs}" \
  --prefix "${PREFIX:-cadical_portfolio}" \
  --manifest "${MANIFEST:-artifacts/solver_logs/cadical_portfolio.jsonl}" \
  --time-bin "${TIME_BIN:-/usr/bin/time}" \
  --timeout-bin "${TIMEOUT_BIN:-timeout}" \
  ${SKIP_BASELINE:+--skip-baseline} \
  ${DRY_RUN:+--dry-run}
