#!/usr/bin/env bash
set -euo pipefail

cd "$(dirname "$0")/.."

python3 -m src.roundingsat_portfolio \
  --solver "${SOLVER:-artifacts/solvers/roundingsat}" \
  --input "${INPUT:-artifacts/problem835_one_color_augmented.opb}" \
  --time-limit "${TIME_LIMIT_SECONDS:-1800}" \
  --max-jobs "${MAX_JOBS:-5}" \
  --start-index "${START_INDEX:-0}" \
  --log-dir "${LOG_DIR:-artifacts/solver_logs}" \
  --prefix "${PREFIX:-portfolio_lp0}" \
  --manifest "${MANIFEST:-artifacts/solver_logs/portfolio_lp0.jsonl}" \
  ${SKIP_BASELINE:+--skip-baseline} \
  ${DRY_RUN:+--dry-run}
