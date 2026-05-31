# Task brief for Codex on the Windows PC

This file is the handoff brief for running this repository on the Windows PC
with 32GB RAM and an Intel i5-13400 CPU.  Use WSL2 Ubuntu unless the user gives
a different environment.

## Objective

Run the first-stage computational experiment for Erdős problem 835:

1. verify the repository works on the Windows/WSL machine;
2. export the one-colour exact-cover OPB instance;
3. try a bounded solver run if a compatible OPB/PB solver is available;
4. record enough evidence for the next mathematical decision.

Do not attempt the full seventeen-colour global model in this first run.

## Important constraints

- This repository does not claim a solution.
- A timeout is not evidence of SAT or UNSAT.
- Stop the solver if the machine starts swapping heavily.
- Keep generated files under `artifacts/`.
- Do not commit generated OPB files or solver logs unless the user explicitly
  asks.
- Use strict time and memory budgets for the first raw solve.

Recommended first solver budget:

```text
wall time: 2-6 hours
memory: stop manually if process memory exceeds about 26GB
disk: keep at least 100GB free before proof logging
```

## Step 1: clone and inspect

```bash
git clone https://github.com/runes780/erdos-835-first-layer
cd erdos-835-first-layer
git status --short
python3 --version
df -h .
free -h
```

Expected: clean git status, Python 3 available, enough free disk.

## Step 2: run smoke checks

```bash
bash scripts/wsl_smoke.sh
```

Expected:

- unit tests pass;
- #835 instance statistics print;
- a small toy OPB file is generated at `artifacts/toy.opb`.

If this fails, fix the local environment before doing any solver work.

## Step 3: export the full one-colour OPB instance

```bash
bash scripts/export_problem835_opb.sh
```

Expected generated files:

```text
artifacts/problem835_stats.json
artifacts/problem835_one_color.opb
```

Record:

```bash
ls -lh artifacts/problem835_one_color.opb artifacts/problem835_stats.json
wc -l artifacts/problem835_one_color.opb
sha256sum artifacts/problem835_one_color.opb
cat artifacts/problem835_stats.json
```

Expected OPB size from the Mac export was about 56MB.  Small differences in
line endings are acceptable, but the statistics must match the README.

## Step 4: find an available solver

Check for common pseudo-Boolean / OPB solvers:

```bash
command -v roundingSat || true
command -v roundingsat || true
command -v sat4j-pb || true
command -v minisat+ || true
command -v clasp || true
```

If no compatible solver is available, stop after OPB export and report that the
instance is generated but no solver is installed.  Do not invent a solver path.

If the user approves installing tools, install one compatible OPB/PB solver and
record the exact install command and solver version.

## Step 5: run one bounded solver attempt

Use the solver's own timeout option if available.  Otherwise use Linux
`timeout`.  Keep logs in `artifacts/`.

Template:

```bash
mkdir -p artifacts/solver_logs
/usr/bin/time -v timeout 6h SOLVER_COMMAND artifacts/problem835_one_color.opb \
  > artifacts/solver_logs/raw_one_colour_6h.log 2>&1
```

Replace `SOLVER_COMMAND` with the actual solver command.  Do not run an
unbounded job.

During the run, monitor memory in another shell:

```bash
watch -n 30 'free -h; ps -eo pid,ppid,comm,%mem,%cpu,rss,vsz --sort=-rss | head -20'
```

Stop the run if memory pressure causes heavy swap.

## Step 6: classify the result

After the solver exits, inspect the log:

```bash
tail -100 artifacts/solver_logs/raw_one_colour_6h.log
```

Classify as exactly one of:

```text
UNSAT
SAT
UNKNOWN / timeout
crash / memory failure
not run because no solver was available
```

## Step 7: what to report back

Report these items to the user:

```text
machine and environment:
Python version:
solver name/version:
exact command:
wall time:
peak memory if available:
OPB file size:
OPB sha256:
result classification:
last relevant solver log lines:
next recommendation:
```

If the result is UNSAT:

1. preserve all logs and proof/certificate files;
2. verify the certificate if the solver supports independent checking;
3. do not claim a mathematical result until the certificate is verified.

If the result is SAT:

1. preserve the witness;
2. convert or parse the selected variables;
3. run the one-colour verifier before making any claim.

If the result is timeout or memory failure:

1. do not keep rerunning the same raw model;
2. move to fixed-\(D_a\), symmetry breaking, or smaller derived subsystems;
3. use `prompts/pro_next_round.md` to ask for stronger hand constraints.

## Current expected outcome

The most likely first outcome is UNKNOWN/timeout, not a decisive SAT/UNSAT.
That is still useful: it tells us whether the raw one-colour OPB model is easy
enough for the 32GB PC or whether the next step must be mathematical reduction.

