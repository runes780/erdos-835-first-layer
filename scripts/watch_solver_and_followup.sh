#!/usr/bin/env bash
set -euo pipefail

cd "$(dirname "$0")/.."

python3 -m src.solver_watchdog \
  --interval-seconds "${WATCH_INTERVAL_SECONDS:-300}" \
  --max-followups "${MAX_FOLLOWUPS:-1}" \
  --followup-jobs "${FOLLOWUP_JOBS:-4}" \
  --followup-time-limit "${FOLLOWUP_TIME_LIMIT_SECONDS:-21600}" \
  --followup-prefix "${FOLLOWUP_PREFIX:-auto_followup}" \
  --report "${WATCH_REPORT:-artifacts/solver_logs/solver_watchdog_report.md}" \
  --state "${WATCH_STATE:-artifacts/solver_logs/solver_watchdog_state.json}" \
  --include-resources \
  ${DISABLE_FOLLOWUP:+--disable-followup} \
  ${WATCH_ONCE:+--once}
