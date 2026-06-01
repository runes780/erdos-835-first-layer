# Extension Ladder E_m Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add a smaller staged exact-cover ladder \(E_m\), starting with \(E_1\), so the next solver target tests one point-extension before returning to the full eleven-family shadow.

**Architecture:** Keep `src.erdos835_one_color` as the full one-colour model. Add a focused `src.extension_ladder` module for \(E_m\): D rows plus `m` extension-family rows, D-star exact-one constraints, point-extension exact-one constraints, and optional cross-family disjointness constraints for `m >= 2`.

**Tech Stack:** Python standard library, unittest, OPB pseudo-Boolean export, existing block naming conventions, RoundingSat under WSL.

---

## Current Decision

The previous post-timeout plan made D-only the next main target. The newer mathematical advice changes the priority:

1. `E_1` first, because it is a decisive necessary condition and much smaller than the full one-colour instance.
2. Then `E_2`, `E_4`, `E_8`, and `E_11` if earlier stages are satisfiable or inconclusive.
3. Keep D-only as auxiliary evidence, not the main branch.
4. Use the stronger safe `E_1` normalization from the later advice: triple
   matching, off-triple block `D:0,1,3,5,7`, and D lower-count constraints.

For \(v=21,t=4,m=1\), base `E_1` has:

- variables: `74613`
- exact-one constraints: `26334`
- disjointness constraints: `0`
- exact-one incidences: `447678`

For `m >= 2`, add one at-most-one constraint per 6-set:

```text
sum_j x_{j,U} <= 1
```

At `m=11`, the disjointness plus the D-star and point-extension equations are the staged version of the one-colour shadow; the missing allowed-6-set equality follows by counting for integer solutions.

With the current stronger `E_1` script, the generated OPB has 27,906
constraints: 26,334 base exact-one constraints, ten symmetry units, and 1,562
D lower-count constraints.

---

## File Map

- Create `src/extension_ladder.py`: stats, row index, OPB export, and CLI for staged \(E_m\).
- Create `tests/test_extension_ladder.py`: TDD coverage for `E_1`, `E_2`, toy OPB export, and CLI behavior.
- Create `scripts/export_problem835_e1_opb.sh`: WSL-friendly `E_1` export.
- Create `scripts/run_roundingsat_e1_2h.sh`: bounded `E_1` RoundingSat run.
- Modify `README.md`: document the staged ladder as the active route.
- Modify `docs/current_information.md`: mark D-only as auxiliary and `E_1` as next target.
- Modify `docs/progress_log.md`: record the pivot and any smoke-run result.

---

## Task 1: Add E_m Stats

**Files:**
- Create: `tests/test_extension_ladder.py`
- Create: `src/extension_ladder.py`

- [ ] **Step 1: Write the failing `E_1` stats test**

Add:

```python
import unittest

from src.erdos835_one_color import OneColorConfig
from src.extension_ladder import compute_extension_ladder_stats


class ExtensionLadderStatsTests(unittest.TestCase):
    def test_e1_counts_match_staged_reduction(self):
        stats = compute_extension_ladder_stats(OneColorConfig(v=21, t=4, extension_count=1))

        self.assertEqual(stats.d_rows, 20349)
        self.assertEqual(stats.x_rows, 54264)
        self.assertEqual(stats.total_variables, 74613)
        self.assertEqual(stats.exact_one_constraints, 26334)
        self.assertEqual(stats.disjointness_constraints, 0)
        self.assertEqual(stats.total_constraints, 26334)
        self.assertEqual(stats.exact_one_incidences, 447678)
        self.assertEqual(stats.disjointness_incidences, 0)
        self.assertEqual(stats.total_incidences, 447678)
```

- [ ] **Step 2: Run the red test**

Run:

```powershell
python -m unittest tests.test_extension_ladder.ExtensionLadderStatsTests.test_e1_counts_match_staged_reduction -v
```

Expected: import failure for `src.extension_ladder`.

- [ ] **Step 3: Implement the stats dataclass and function**

Create:

```python
@dataclass(frozen=True)
class ExtensionLadderStats:
    d_rows: int
    x_rows: int
    total_variables: int
    d_star_constraints: int
    point_extension_constraints: int
    exact_one_constraints: int
    disjointness_constraints: int
    total_constraints: int
    d_row_exact_one_incidences: int
    x_row_exact_one_incidences: int
    exact_one_incidences: int
    disjointness_incidences: int
    total_incidences: int
```

Use:

```python
d_rows = comb(v, t + 1)
u_rows = comb(v, t + 2)
x_rows = m * u_rows
d_star_constraints = comb(v, t)
point_extension_constraints = m * d_rows
disjointness_constraints = u_rows if m >= 2 else 0
d_row_exact_one_incidences = d_rows * ((t + 1) + m)
x_row_exact_one_incidences = x_rows * (t + 2)
disjointness_incidences = x_rows if m >= 2 else 0
```

- [ ] **Step 4: Add and pass the `E_2` stats test**

Add:

```python
    def test_e2_counts_include_disjointness_constraints(self):
        stats = compute_extension_ladder_stats(OneColorConfig(v=21, t=4, extension_count=2))

        self.assertEqual(stats.total_variables, 128877)
        self.assertEqual(stats.exact_one_constraints, 46683)
        self.assertEqual(stats.disjointness_constraints, 54264)
        self.assertEqual(stats.total_constraints, 100947)
        self.assertEqual(stats.exact_one_incidences, 793611)
        self.assertEqual(stats.disjointness_incidences, 108528)
        self.assertEqual(stats.total_incidences, 902139)
```

Run:

```powershell
python -m unittest tests.test_extension_ladder.ExtensionLadderStatsTests -v
```

Expected: both stats tests pass.

---

## Task 2: Add E_m OPB Export

**Files:**
- Modify: `tests/test_extension_ladder.py`
- Modify: `src/extension_ladder.py`

- [ ] **Step 1: Write failing toy OPB test for `E_1`**

Add:

```python
from src.extension_ladder import export_extension_ladder_opb


class ExtensionLadderOpbTests(unittest.TestCase):
    def test_e1_opb_has_d_star_and_point_extension_equalities(self):
        config = OneColorConfig(v=4, t=1, extension_count=1)

        text = export_extension_ladder_opb(config)

        lines = text.splitlines()
        self.assertEqual(lines[0], "* #variable= 10 #constraint= 10")
        self.assertIn("* row 1 D:0,1", lines)
        self.assertIn("* row 10 X:0:1,2,3", lines)
        self.assertIn("+1 x1 +1 x2 +1 x3 = 1 ; * T:0", lines)
        self.assertIn("+1 x1 +1 x7 +1 x8 = 1 ; * P:0:0,1", lines)
        self.assertNotIn(" <= 1 ; * U:", text)
```

- [ ] **Step 2: Implement row index and `E_1` OPB**

Rows are stable:

1. all `D:S` rows for `(t+1)`-sets;
2. for each `j`, all `X:j:U` rows for `(t+2)`-sets.

Constraints:

```text
T exact-one:       sum_{S superset T} D:S = 1
P exact-one: D:S + sum_{U superset S} X:j:U = 1
```

- [ ] **Step 3: Add failing toy OPB test for `E_2` disjointness**

Add:

```python
    def test_e2_opb_adds_cross_family_disjointness(self):
        config = OneColorConfig(v=4, t=1, extension_count=2)

        text = export_extension_ladder_opb(config)

        lines = text.splitlines()
        self.assertEqual(lines[0], "* #variable= 14 #constraint= 20")
        self.assertIn("+1 x7 +1 x11 <= 1 ; * U:0,1,2", lines)
```

- [ ] **Step 4: Implement disjointness constraints**

For every `U`, write:

```text
sum_j X:j:U <= 1
```

only when `extension_count >= 2`.

- [ ] **Step 5: Add no-comment export test**

Add:

```python
    def test_opb_can_omit_non_header_comments(self):
        config = OneColorConfig(v=4, t=1, extension_count=2)

        text = export_extension_ladder_opb(
            config,
            include_row_comments=False,
            include_column_comments=False,
        )

        self.assertTrue(all(line.startswith("* #") or " * " not in line for line in text.splitlines()))
```

Run:

```powershell
python -m unittest tests.test_extension_ladder -v
```

Expected: all extension ladder tests pass.

---

## Task 3: Add CLI and Scripts

**Files:**
- Modify: `src/extension_ladder.py`
- Create: `scripts/export_problem835_e1_opb.sh`
- Create: `scripts/run_roundingsat_e1_2h.sh`

- [ ] **Step 1: Add CLI smoke test**

Use the module directly from PowerShell:

```powershell
python -m src.extension_ladder stats --v 21 --t 4 --extension-count 1
```

Expected output contains:

```text
total variables: 74613
total constraints: 26334
```

- [ ] **Step 2: Implement CLI commands**

Commands:

```text
stats
opb
```

Flags:

```text
--v
--t
--extension-count
--output
--json
--no-comments
--no-row-comments
--no-column-comments
--symmetry-break {none,triple-matching}
```

- [ ] **Step 3: Add export script**

Create `scripts/export_problem835_e1_opb.sh`:

```bash
#!/usr/bin/env bash
set -euo pipefail

cd "$(dirname "$0")/.."

mkdir -p artifacts

python3 -m src.extension_ladder opb \
  --v 21 \
  --t 4 \
  --extension-count 1 \
  --symmetry-break triple-matching \
  --no-comments \
  --output artifacts/problem835_e1.opb
```

- [ ] **Step 4: Add run script**

Create `scripts/run_roundingsat_e1_2h.sh`:

```bash
#!/usr/bin/env bash
set -euo pipefail

cd "$(dirname "$0")/.."

: "${TIME_LIMIT_SECONDS:=7200}"
: "${SOLVER:=artifacts/solvers/roundingsat}"
: "${OPB:=artifacts/problem835_e1.opb}"
: "${LOG:=artifacts/solver_logs/e1_roundingsat_lp0_2h.log}"

mkdir -p "$(dirname "$LOG")"

/usr/bin/time -v "$SOLVER" \
  --lp=0 \
  "--time-limit=${TIME_LIMIT_SECONDS}" \
  --print-sol=1 \
  "$OPB" \
  > "$LOG" 2>&1
```

---

## Task 4: Verify and Run E1 Smoke

**Files:**
- Modify: `README.md`
- Modify: `docs/current_information.md`
- Modify: `docs/progress_log.md`

- [ ] **Step 1: Run Python tests**

Run:

```powershell
python -m unittest discover -s tests -v
```

Expected: all tests pass.

- [ ] **Step 2: Syntax-check shell scripts**

Run:

```powershell
wsl -d Ubuntu bash -lc "cd /mnt/e/code/835 && bash -n scripts/export_problem835_e1_opb.sh && bash -n scripts/run_roundingsat_e1_2h.sh"
```

Expected: exit code `0`.

- [ ] **Step 3: Generate E1 OPB**

Run:

```powershell
wsl -d Ubuntu bash -lc "cd /mnt/e/code/835 && bash scripts/export_problem835_e1_opb.sh && head -n 1 artifacts/problem835_e1.opb && ls -lh artifacts/problem835_e1.opb"
```

Expected header:

```text
* #variable= 74613 #constraint= 26343
```

The extra nine constraints are the triple-matching symmetry break.

- [ ] **Step 4: Run a bounded smoke solver**

Run:

```powershell
wsl -d Ubuntu bash -lc "cd /mnt/e/code/835 && TIME_LIMIT_SECONDS=600 LOG=artifacts/solver_logs/e1_roundingsat_lp0_10m.log bash scripts/run_roundingsat_e1_2h.sh"
```

Expected: solver returns `SAT`, `UNSAT`, `UNKNOWN`, or `TIMELIMIT` without crashing.

- [ ] **Step 5: Record the outcome**

Append the E1 generation and smoke result to `docs/progress_log.md`, and update `README.md` plus `docs/current_information.md` so the active target is no longer described as D-only-first.

---

## Decision Rules

- If `E_1` is `UNSAT`, preserve the log and rerun with proof logging before making a public mathematical claim.
- If `E_1` is `SAT`, extract/verify the witness if the solver prints it, then continue to `E_2`.
- If `E_1` reaches `TIMELIMIT`, try stronger safe D symmetry breaking and a solver portfolio on `E_1`; do not jump back to the full \(E_{11}\) instance.
- If `E_2`, `E_4`, or `E_8` are SAT, continue up the ladder.
- If `E_11` is UNSAT with a checked certificate, that rules out the one-colour shadow and therefore the first-layer object.
