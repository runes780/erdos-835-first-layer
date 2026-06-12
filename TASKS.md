# Task brief for Codex on the Windows PC

This file is the handoff brief for running this repository on the Windows PC
with 32GB RAM and an Intel i5-13400 CPU.  Use WSL2 Ubuntu unless the user gives
a different environment.

## Objective

Run the first-stage computational experiment for Erdős problem 835:

1. verify the repository works on the Windows/WSL machine;
2. export the one-colour exact-cover OPB instance;
3. export the strengthened OPB instance after the raw smoke export;
4. if the strengthened instance times out, switch to the staged `E_m` ladder,
   starting with `E_1`;
5. try a bounded `--lp=0` solver run if RoundingSat is available;
6. record enough evidence for the next mathematical decision.

Do not attempt the full seventeen-colour global model in this first run.

## Important constraints

- This repository does not claim a solution.
- A timeout is not evidence of SAT or UNSAT.
- Stop the solver if the machine starts swapping heavily.
- Keep generated files under `artifacts/`.
- Do not commit generated OPB files or solver logs unless the user explicitly
  asks.
- Use strict time and memory budgets for the strengthened solve.

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

Then export the strengthened instance:

```bash
bash scripts/export_problem835_augmented_opb.sh
```

This appends the triple-matching symmetry break and the redundant
`G_j` 4-set count constraints, plus the redundant \(D_a\) lower-subset count
constraints for subset sizes 0, 1, 2, and 3.

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

Use RoundingSat with LP disabled unless a later benchmark gives a better
setting.  Keep logs in `artifacts/solver_logs/`.

Template:

```bash
mkdir -p artifacts/solver_logs
TIME_LIMIT_SECONDS=21600 bash scripts/run_roundingsat_lp0_augmented_6h.sh
```

For a short test run, set `TIME_LIMIT_SECONDS=600` and a distinct `LOG=...`.
Do not run an unbounded job.

During the run, monitor memory in another shell:

```bash
watch -n 30 'free -h; ps -eo pid,ppid,comm,%mem,%cpu,rss,vsz --sort=-rss | head -20'
```

Stop the run if memory pressure causes heavy swap.

## Step 6: classify the result

After the solver exits, inspect the log:

```bash
tail -100 artifacts/solver_logs/augmented_one_colour_roundingsat_lp0_6h.log
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

1. do not keep rerunning the same model without changing constraints or solver settings;
2. move to the staged `E_m` ladder, starting with `E_1`;
3. use D-only, fixed-\(D_a\), and symmetry-breaking runs as auxiliary derived
   subsystems;
4. use `prompts/pro_next_round.md` to ask for stronger hand constraints.

## Current expected outcome

The first raw RoundingSat run already ended UNKNOWN/timeout, with LP time as
the bottleneck rather than RAM.  The current expected outcome is still probably
UNKNOWN/timeout.  The strengthened `--lp=0` portfolio also timed out, so the
current active benchmark is the staged `E_1` OPB:

```bash
bash scripts/export_problem835_e1_opb.sh
TIME_LIMIT_SECONDS=7200 bash scripts/run_roundingsat_e1_2h.sh
```

If the `E_1` OPB portfolio times out, switch to the pairwise CNF/CDCL route:

```bash
bash scripts/export_problem835_e1_cnf.sh
TIME_LIMIT_SECONDS=7200 bash scripts/run_cadical_e1_2h.sh
```

The local CaDiCaL binary may be unpacked under
`artifacts/solvers/cadical_pkg/usr/bin/cadical`.

The E1 CNF is a baseline pairwise exact-one encoding plus symmetry unit
clauses.  It does not include D lower-count equalities.  After the baseline
Kissat timeout, generate the two residual-orbit branch CNFs:

```bash
bash scripts/export_problem835_e1_branch_cnfs.sh
BRANCH=a TIME_LIMIT_SECONDS=7200 bash scripts/run_kissat_e1_branch_2h.sh
BRANCH=b TIME_LIMIT_SECONDS=7200 bash scripts/run_kissat_e1_branch_2h.sh
```

For the strengthened OPB branch version with D lower counts and G4 equalities:

```bash
bash scripts/export_problem835_e1_g4_branch_opbs.sh
BRANCH=a TIME_LIMIT_SECONDS=3600 bash scripts/run_roundingsat_e1_g4_branch_1h.sh
BRANCH=b TIME_LIMIT_SECONDS=3600 bash scripts/run_roundingsat_e1_g4_branch_1h.sh
```

If the default CaDiCaL run also times out, use a bounded parameter portfolio
instead of repeating the same command:

```bash
SKIP_BASELINE=1 MAX_JOBS=6 TIME_LIMIT_SECONDS=3600 \
  PREFIX=e1_cadical_portfolio_1h \
  MANIFEST=artifacts/solver_logs/e1_cadical_portfolio_1h.jsonl \
  bash scripts/run_cadical_portfolio.sh
```
