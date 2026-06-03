# Erdős Problem 835: first-layer exact-cover test

This repository isolates one computationally checkable obstruction suggested by
the current discussion around Erdős problem 835.

The reduction studied here is the one-color shadow of the first-layer
conditions in the first remaining case \(k=16\).  In the notation used below,
the target instance has

```text
v = 21, t = 4, extension_count = 11.
```

For one fixed color \(a\), write

- \(D_a=\{S\in {V\choose 5}:D(S)=a\}\);
- \(G_{j,a}=\{U\in {V\choose 6}:g_j(U)=a\}\), for \(j=1,\ldots,11\).

The exact-cover constraints are:

1. Every 4-set is contained in exactly one selected 5-set \(S\in D_a\).
2. For every \(j\) and every 5-set \(S\),
   \[
   1_{S\in D_a}+\#\{U\in G_{j,a}:S\subset U\}=1.
   \]
3. For every 6-set \(U\),
   \[
   \#\{j:U\in G_{j,a}\}+\#\{S\in D_a:S\subset U\}=1.
   \]

If this one-color exact-cover instance is impossible, then the proposed
first-layer object for \(k=16\) is impossible, hence the original coloring
cannot exist in that case.

## Quick checks

Run the test suite:

```bash
python3 -m unittest discover -s tests -v
```

Print the #835 instance statistics:

```bash
python3 -m src.erdos835_one_color stats
```

Expected headline counts:

```text
D rows: 20349
x rows: 596904
total rows: 617253
t-subset columns: 5985
(j,S) columns: 223839
U-shadow columns: 54264
total columns: 284088
total incidences: 4829496
constraint lengths: (17, 17, 17)
```

Inspect the sparse exact-cover rows without materializing the whole instance:

```bash
python3 -m src.erdos835_one_color rows --limit 10
```

Export a pseudo-Boolean OPB instance:

```bash
python3 -m src.erdos835_one_color opb --no-row-comments --no-column-comments --output artifacts/problem835_one_color.opb
```

Export the current strengthened OPB instance:

```bash
bash scripts/export_problem835_augmented_opb.sh
```

This version adds the safe triple-matching symmetry break through the fixed
triple `{0,1,2}` and the redundant relative-design constraints
`sum_{U superset T} x_{j,U}=8` for each `j` and each 4-set `T`.  It also
adds the redundant \(D_a\) lower-subset count constraints for subset sizes
0, 1, 2, and 3.

Run the strengthened instance with RoundingSat's LP disabled:

```bash
TIME_LIMIT_SECONDS=21600 bash scripts/run_roundingsat_lp0_augmented_6h.sh
```

Run a small RoundingSat portfolio when more CPU use is desired:

```bash
SKIP_BASELINE=1 MAX_JOBS=5 TIME_LIMIT_SECONDS=21600 \
  PREFIX=portfolio_extra_6h \
  MANIFEST=artifacts/solver_logs/portfolio_extra_6h.jsonl \
  bash scripts/run_roundingsat_portfolio.sh
```

This starts independent single-core solver variants with separate logs and a
JSONL manifest, while leaving an already-running baseline process alone.

After the strengthened one-colour portfolio times out, move to the smaller
staged extension ladder.  The first target is `E_1`, which keeps \(D_a\) and
one point-extension family but drops the other ten families:

```bash
bash scripts/export_problem835_e1_opb.sh
TIME_LIMIT_SECONDS=7200 bash scripts/run_roundingsat_e1_2h.sh
```

The generated `E_1` OPB has 74,613 variables and 26,343 constraints with the
basic triple-matching symmetry break.  The current default export also adds
the safe off-triple block `D:0,1,3,5,7` and the redundant D lower-count
constraints, giving 27,906 constraints.  If `E_1` is UNSAT, the first-layer
object is already impossible.  If `E_1` is SAT or inconclusive, continue up the
ladder: `E_2`, `E_4`, `E_8`, then `E_11`.

The D-only target remains useful as an auxiliary check:

```bash
bash scripts/export_problem835_d_only_opb.sh
TIME_LIMIT_SECONDS=7200 bash scripts/run_roundingsat_d_only_2h.sh
```

This asks only whether the fixed-colour \(D_a\) block system
\(S(4,5,21)\) exists under the current symmetry break and redundant lower-count
constraints.  If this produces a SAT witness, verify the selected blocks before
building the fixed-D conditional one-colour instance.

The current CNF/CDCL route for `E_1` is:

```bash
bash scripts/export_problem835_e1_cnf.sh
TIME_LIMIT_SECONDS=7200 bash scripts/run_cadical_e1_2h.sh
```

This exports a pairwise DIMACS encoding with 74,613 variables and 3,607,768
clauses.  This baseline CNF has the triple/off-triple symmetry units, but it
does not include the OPB-only D lower-count constraints.  CaDiCaL can be used
from `artifacts/solvers/cadical_pkg/usr/bin` if the local package has been
downloaded and extracted.

After a default CaDiCaL timeout, run a small parameter portfolio:

```bash
SKIP_BASELINE=1 MAX_JOBS=6 TIME_LIMIT_SECONDS=3600 \
  PREFIX=e1_cadical_portfolio_1h \
  MANIFEST=artifacts/solver_logs/e1_cadical_portfolio_1h.jsonl \
  bash scripts/run_cadical_portfolio.sh
```

Generate the two residual-orbit branch CNFs recommended after the Kissat
timeout:

```bash
bash scripts/export_problem835_e1_branch_cnfs.sh
BRANCH=a TIME_LIMIT_SECONDS=7200 bash scripts/run_kissat_e1_branch_2h.sh
BRANCH=b TIME_LIMIT_SECONDS=7200 bash scripts/run_kissat_e1_branch_2h.sh
```

Generate the G4-strengthened OPB branches:

```bash
bash scripts/export_problem835_e1_g4_branch_opbs.sh
BRANCH=a TIME_LIMIT_SECONDS=3600 bash scripts/run_roundingsat_e1_g4_branch_1h.sh
BRANCH=b TIME_LIMIT_SECONDS=3600 bash scripts/run_roundingsat_e1_g4_branch_1h.sh
```

After both E1 branch approaches time out, run the Pro-model E2 branch
experiment:

```bash
bash scripts/export_problem835_e2_branch_cnfs.sh
BRANCH=a TIME_LIMIT_SECONDS=7200 bash scripts/run_kissat_e2_branch_2h.sh
BRANCH=b TIME_LIMIT_SECONDS=7200 bash scripts/run_kissat_e2_branch_2h.sh
```

For the 32GB i5-13400 Windows PC, see `docs/pc_execution.md` and
`docs/solver_runbook.md`.  The recommended path is WSL2 Ubuntu, one-colour OPB
first, and strict solver time/memory limits.

If this repo is opened by Codex on the Windows PC, start from `TASKS.md`.

## Files

- `src/erdos835_one_color.py`: parameter model, statistics, and sparse row
  generator.
- `src/extension_ladder.py`: staged `E_m` generator for one, two, four, eight,
  or eleven extension families.
- `src/verify_one_color.py`: verifier for candidate one-color solutions.
- `tests/test_one_color.py`: unit tests, including a small resolvable toy
  instance.
- `scripts/export_problem835_opb.sh`: raw full one-colour OPB export.
- `scripts/export_problem835_augmented_opb.sh`: strengthened OPB export with
  symmetry breaking and G4 count constraints.
- `scripts/export_problem835_d_only_opb.sh`: smaller D-only OPB export for the
  \(S(4,5,21)\) block system.
- `scripts/export_problem835_e1_opb.sh`: first staged extension-ladder OPB
  export.
- `scripts/export_problem835_e1_cnf.sh`: pairwise DIMACS CNF export for the
  first staged extension-ladder target.
- `scripts/export_problem835_e1_branch_cnfs.sh`: residual-orbit branch CNFs
  with `D:0,1,3,6,8` and `D:0,1,3,6,9`.
- `scripts/export_problem835_e1_g4_branch_opbs.sh`: E1 branch OPBs with D
  lower counts and G4 equalities.
- `scripts/export_problem835_e2_branch_cnfs.sh`: E2 residual-orbit branch CNFs
  with the same two D branch units.
- `scripts/run_roundingsat_lp0_augmented_6h.sh`: bounded RoundingSat run using
  `--lp=0`.
- `scripts/run_roundingsat_d_only_2h.sh`: bounded RoundingSat run for the
  D-only OPB instance.
- `scripts/run_roundingsat_e1_2h.sh`: bounded RoundingSat run for `E_1`.
- `scripts/run_cadical_e1_2h.sh`: bounded CaDiCaL run for the `E_1` CNF.
- `scripts/run_cadical_portfolio.sh`: launch a bounded portfolio of
  independent CaDiCaL CNF variants.
- `scripts/run_kissat_e1_branch_2h.sh`: bounded Kissat run for an E1 branch
  CNF.
- `scripts/run_kissat_e2_branch_2h.sh`: bounded Kissat run for an E2 branch
  CNF.
- `scripts/run_roundingsat_e1_g4_branch_1h.sh`: bounded RoundingSat run for a
  G4-strengthened E1 branch OPB.
- `scripts/run_roundingsat_portfolio.sh`: launch a bounded portfolio of
  independent RoundingSat variants.
- `TASKS.md`: handoff task brief for Codex on the Windows PC.
- `notes/erdos835_first_layer_note.tex`: compact mathematical note.
- `docs/current_information.md`: consolidated current mathematical and
  computational status.
- `docs/pc_execution.md`: practical execution guidance for the 32GB Windows PC.
- `docs/solver_runbook.md`: staged runbook for solver attempts and result
  interpretation.
- `docs/progress_log.md`: dated log of repo setup and verification.
- `prompts/pro_next_round.md`: prompt for a stronger model to continue the
  attack without web search.

## Current status

This repo does not claim a solution of problem 835.  It records a concrete
subproblem whose unsatisfiability would close the \(k=16\) first-layer case.
The raw and strengthened one-colour RoundingSat runs reached time limits
without SAT or UNSAT.  The active next target is now the staged extension
ladder, starting with `E_1`.  D-only and fixed-D conditional instances are kept
as auxiliary diagnostics rather than the main branch.
