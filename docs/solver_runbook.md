# Solver runbook

This runbook is for executing the one-colour exact-cover instance on the 32GB
i5-13400 Windows PC, preferably inside WSL2 Ubuntu.

## First commands

Clone and enter the repo:

```bash
git clone https://github.com/runes780/erdos-835-first-layer
cd erdos-835-first-layer
```

Run the local checks:

```bash
bash scripts/wsl_smoke.sh
```

Export the full one-colour OPB instance:

```bash
bash scripts/export_problem835_opb.sh
```

Expected generated files:

```text
artifacts/problem835_stats.json
artifacts/problem835_one_color.opb
```

The OPB file is ignored by git because it is generated.

After the raw 2-hour run timed out with RoundingSat's LP spending most of the
time, the preferred next export is the strengthened one-colour instance:

```bash
bash scripts/export_problem835_augmented_opb.sh
```

This adds:

- the triple-matching symmetry break
  `D:{0,1,2,3,4}, D:{0,1,2,5,6}, ..., D:{0,1,2,19,20}`;
- the redundant relative-design constraints
  `sum_{U superset T} x_{j,U}=8` for every `j` and 4-set `T`.
- the redundant \(D_a\) lower-subset count constraints for subset sizes
  0, 1, 2, and 3.

## Resource policy

Use the first run to learn whether the raw model is easy or hard.  Do not run
unbounded jobs at the beginning.

Recommended first limits:

```text
wall time: 2-6 hours
memory: stop manually if process memory exceeds about 26GB
disk: keep at least 100GB free before proof logging
```

If WSL2 has a memory cap, allocate about 24GB-28GB to WSL and leave the rest to
Windows.

For RoundingSat, disable LP on this model unless a later benchmark reverses the
evidence:

```bash
TIME_LIMIT_SECONDS=21600 bash scripts/run_roundingsat_lp0_augmented_6h.sh
```

For a short benchmark, override the time limit:

```bash
TIME_LIMIT_SECONDS=600 LOG=artifacts/solver_logs/augmented_one_colour_roundingsat_lp0_10m.log \
  bash scripts/run_roundingsat_lp0_augmented_6h.sh
```

RoundingSat is effectively single-core on this instance.  To use more CPU, run
a bounded portfolio of different restart/propagation variants:

```bash
SKIP_BASELINE=1 MAX_JOBS=5 TIME_LIMIT_SECONDS=21600 \
  PREFIX=portfolio_extra_6h \
  MANIFEST=artifacts/solver_logs/portfolio_extra_6h.jsonl \
  bash scripts/run_roundingsat_portfolio.sh
```

Use `SKIP_BASELINE=1` when a baseline `--lp=0` process is already running.
The first safe portfolio tier is one baseline plus five variants.  Escalate
toward 10-12 variants only when the machine can be dedicated to the run.

After the strengthened portfolio times out, use the staged `E_m` ladder before
returning to the full one-colour instance:

```bash
bash scripts/export_problem835_e1_opb.sh
TIME_LIMIT_SECONDS=7200 bash scripts/run_roundingsat_e1_2h.sh
```

The first generated `E_1` instance has:

```text
variables: 74613
constraints: 27906
size: 9.2M
```

This default `E_1` export uses triple matching, the safe off-triple block
`D:0,1,3,5,7`, and redundant D lower-count constraints.  A 10-minute six-way
portfolio reached `s TIMELIMIT` on every branch; the best branch was
`lubybase15` with 1,079,995 conflicts and peak RSS about 129MB.  This is a good
candidate for a broader portfolio: it uses one CPU core and very little memory
per process.

The pairwise CNF/CDCL route for the same `E_1` target is:

```bash
bash scripts/export_problem835_e1_cnf.sh
TIME_LIMIT_SECONDS=7200 bash scripts/run_cadical_e1_2h.sh
```

This CNF is pairwise exact-one plus symmetry units only.  It intentionally does
not include D lower-count equalities; use the OPB ladder for those constraints,
or a later bounded-cardinality CNF encoding.

If the default CaDiCaL run times out, run a bounded parameter portfolio:

```bash
SKIP_BASELINE=1 MAX_JOBS=6 TIME_LIMIT_SECONDS=3600 \
  PREFIX=e1_cadical_portfolio_1h \
  MANIFEST=artifacts/solver_logs/e1_cadical_portfolio_1h.jsonl \
  bash scripts/run_cadical_portfolio.sh
```

Start with six CaDiCaL jobs on the 32GB PC.  The default 2-hour CaDiCaL run
peaked below 1GB RSS, so this uses more CPU while still leaving a large memory
margin.

After the Kissat timeout on the unchanged E1 CNF, generate the two
residual-orbit branches:

```bash
bash scripts/export_problem835_e1_branch_cnfs.sh
BRANCH=a TIME_LIMIT_SECONDS=7200 bash scripts/run_kissat_e1_branch_2h.sh
BRANCH=b TIME_LIMIT_SECONDS=7200 bash scripts/run_kissat_e1_branch_2h.sh
```

The two branch units are `D:0,1,3,6,8` and `D:0,1,3,6,9`.  Both branches must
be covered before drawing any global conclusion.

For the compact PB version with extra G4 equalities:

```bash
bash scripts/export_problem835_e1_g4_branch_opbs.sh
BRANCH=a TIME_LIMIT_SECONDS=3600 bash scripts/run_roundingsat_e1_g4_branch_1h.sh
BRANCH=b TIME_LIMIT_SECONDS=3600 bash scripts/run_roundingsat_e1_g4_branch_1h.sh
```

If both E1 branch experiments time out, move to the E2 pairwise CNF branches:

```bash
bash scripts/export_problem835_e2_branch_cnfs.sh
BRANCH=a TIME_LIMIT_SECONDS=7200 bash scripts/run_kissat_e2_branch_2h.sh
BRANCH=b TIME_LIMIT_SECONDS=7200 bash scripts/run_kissat_e2_branch_2h.sh
```

Each E2 branch CNF has 128,877 variables, 6,449,846 clauses, and the same two
D branch units.  Both branches must be interpreted together; a single SAT,
UNSAT, or timeout result is not a global conclusion.

If both E2 branches time out, do not repeat the same unstrengthened branch
CNFs.  The next Pro-model engineering target is a strengthened CNF with
selected redundant cardinality constraints.  Start with branch-local
`D3 <= 9` and `G4 <= 8` constraints using a bounded sequential-counter or
totalizer encoding, then test whether the resulting CNF size and Kissat
preprocessing remain manageable.

The implemented sequential-counter route is:

```bash
bash scripts/export_problem835_e1_d3_g4_branch_cnfs.sh
BRANCH=a TIME_LIMIT_SECONDS=7200 bash scripts/run_kissat_e1_d3_g4_branch_2h.sh
BRANCH=b TIME_LIMIT_SECONDS=7200 bash scripts/run_kissat_e1_d3_g4_branch_2h.sh
```

This starts with E1 rather than E2 because E1 is still decisive and the
strengthened E1 CNF is smaller: 8,357,853 variables and 21,071,999 clauses per
branch.  The estimated E2 D3/G4 CNF is larger, at 14,875,917 variables and
37,559,876 clauses per branch, so run E1 first as the size and propagation
probe.

## What to log

For every solver attempt, save:

```text
solver name and version
exact command
wall-clock time
peak memory if available
result status: SAT / UNSAT / UNKNOWN / timeout / crash
solver log
output witness or certificate, if produced
```

Do not treat a timeout as mathematical evidence.  It only says the current
formulation and solver were not enough within the chosen budget.

## How to interpret outcomes

### UNSAT

This would be a major result for the first-layer attack.  Next steps:

1. Preserve the solver log and certificate/proof, if available.
2. Verify the certificate with an independent checker if the solver supports
   one.
3. Record exact tool versions and machine details.
4. Only then draft a mathematical/forum note saying the one-colour first-layer
   shadow is UNSAT.

### SAT

This does not solve problem 835.  It means the one-colour shadow alone is
consistent.  Next steps:

1. Extract the selected \(D\)-blocks and \(G_j\)-blocks.
2. Run `src.verify_one_color.verify_one_color` on the witness.
3. Study automorphisms, local counts, and whether multiple colours can be
   assembled compatibly.

### Timeout or memory pressure

This is the most likely first outcome.  Next steps:

1. Stop if swapping begins.
2. Move to fixed-\(D_a\) instances or symmetry-reduced variants.
3. Ask the Pro model for hand-derived local constraints and smaller UNSAT
   cores using `prompts/pro_next_round.md`.

## Decision tree

```text
Run staged E_1 OPB with --lp=0 for 2-6 hours or a portfolio
  |
  +-- UNSAT -> verify certificate -> write formal note
  |
  +-- SAT -> verify witness -> continue to E_2
  |
  +-- UNKNOWN/timeout -> add E_1 symmetry/portfolio variants -> rerun
  |
  +-- memory blowup -> reduce model before further raw solving
```
