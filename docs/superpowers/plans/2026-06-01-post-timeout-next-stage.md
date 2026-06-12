# Post-Timeout Next Stage Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Move from repeated raw one-colour OPB portfolio runs to smaller, diagnosable subproblems: D-only search, fixed-D conditional search, and solver/encoding comparison.

**Architecture:** Keep the current one-colour generator as the baseline, but add two narrower generators. The D-only generator tests existence of a single \(S(4,5,21)\) block system \(D_a\). The fixed-D conditional generator tests whether one verified \(D_a\) admits the eleven \(G_j\) families required by the one-colour shadow.

**Tech Stack:** Python standard library, unittest, OPB export, RoundingSat under WSL, existing `src.erdos835_one_color` conventions.

---

## Current Evidence

- All first-round and follow-up RoundingSat runs ended with `s TIMELIMIT`.
- Best observed branch: `lubybase15`, reaching `15,372,000` conflicts in the follow-up.
- No `SAT`, no `UNSAT`, no certificate.
- Memory and swap were healthy, so failure mode is search hardness, not resource exhaustion.
- The note says local block neighbourhoods, fixed-4-set checks, and intersection numbers do not give a hand contradiction.

Conclusion: stop repeating the same strengthened one-colour OPB as the only tactic. The next useful work is to split the target into smaller certifiable experiments.

---

## File Map

- Modify `src/erdos835_one_color.py`: add D-only OPB export helpers and CLI flag/subcommand.
- Create `src/conditional_one_color.py`: fixed-D conditional model, OPB export, and stats.
- Create `src/design_io.py`: read/write selected block systems in a stable plain-text format.
- Create `tests/test_d_only.py`: D-only stats, OPB export, and symmetry-break tests.
- Create `tests/test_conditional_one_color.py`: toy fixed-D conditional tests.
- Modify `README.md`: document the post-timeout workflow.
- Modify `docs/current_information.md`: replace stale "next run" state with actual timeout results and new plan.
- Modify `docs/progress_log.md`: record the timeout table and follow-up decision.

---

## Task 1: Record The Solver Outcome

**Files:**
- Modify: `docs/progress_log.md`
- Modify: `docs/current_information.md`

- [ ] **Step 1: Add a progress-log entry**

Add a dated entry with:

```text
2026-06-01:
- Baseline plus portfolio runs all reached TIMELIMIT.
- Best first/follow-up branch: lubybase15, 15,372,000 conflicts.
- No SAT/UNSAT/certificate.
- Memory stayed healthy; no swap.
- Decision: stop repeating raw strengthened one-colour OPB as the only strategy.
```

- [ ] **Step 2: Update current-information decision**

Replace any text implying the next step is still raw OPB portfolio with:

```text
The post-timeout route is:
1. D-only S(4,5,21) search.
2. If a D is found, fixed-D conditional one-colour search.
3. Compare OPB against CNF/exact-cover encodings only after the smaller targets are available.
```

- [ ] **Step 3: Verify docs contain no stale claim**

Run:

```powershell
Select-String -Path docs\*.md -Pattern 'no solver result yet|next solver runs should|LaTeX note compiles'
```

Expected: either no stale line, or every match is intentionally revised.

---

## Task 2: Add D-Only Exact-Cover Export

**Files:**
- Modify: `src/erdos835_one_color.py`
- Create: `tests/test_d_only.py`

- [ ] **Step 1: Write failing D-only stats test**

Create `tests/test_d_only.py`:

```python
import unittest

from src.erdos835_one_color import OneColorConfig, compute_d_only_stats


class DOnlyTests(unittest.TestCase):
    def test_problem_835_d_only_counts(self):
        stats = compute_d_only_stats(OneColorConfig.problem_835())

        self.assertEqual(stats.variables, 20349)
        self.assertEqual(stats.constraints, 5985)
        self.assertEqual(stats.constraint_length, 17)


if __name__ == "__main__":
    unittest.main()
```

- [ ] **Step 2: Run red test**

Run:

```powershell
python -m unittest discover -s tests -p test_d_only.py -v
```

Expected: import failure for `compute_d_only_stats`.

- [ ] **Step 3: Implement D-only stats**

Add a frozen dataclass in `src/erdos835_one_color.py`:

```python
@dataclass(frozen=True)
class DOnlyStats:
    variables: int
    constraints: int
    constraint_length: int


def compute_d_only_stats(config: OneColorConfig) -> DOnlyStats:
    config.validate()
    return DOnlyStats(
        variables=comb(config.v, config.t + 1),
        constraints=comb(config.v, config.t),
        constraint_length=config.v - config.t,
    )
```

- [ ] **Step 4: Add D-only OPB export tests**

Extend `tests/test_d_only.py`:

```python
from src.erdos835_one_color import export_d_only_opb


    def test_d_only_opb_exports_exact_cover_constraints(self):
        config = OneColorConfig(v=6, t=1, extension_count=2)

        text = export_d_only_opb(config)

        self.assertEqual(text.splitlines()[0], "* #variable= 15 #constraint= 6")
        self.assertIn("+1 x1 +1 x2 +1 x3 +1 x4 +1 x5 = 1 ; * T:0", text)
```

- [ ] **Step 5: Implement `export_d_only_opb`**

Use existing row naming style:

```python
def export_d_only_opb(config: OneColorConfig, include_comments: bool = True) -> str:
    from io import StringIO

    output = StringIO()
    write_d_only_opb(config, output, include_comments=include_comments)
    return output.getvalue()
```

Then implement `write_d_only_opb` by creating one variable for every 5-set and one equality for every 4-set.

- [ ] **Step 6: Verify D-only tests pass**

Run:

```powershell
python -m unittest discover -s tests -p test_d_only.py -v
```

Expected: all D-only tests pass.

---

## Task 3: Add Stable D-Block File I/O

**Files:**
- Create: `src/design_io.py`
- Create: `tests/test_design_io.py`

- [ ] **Step 1: Write failing parser test**

Create `tests/test_design_io.py`:

```python
import unittest

from src.design_io import parse_blocks, format_blocks


class DesignIoTests(unittest.TestCase):
    def test_parse_and_format_blocks(self):
        text = "0 1 2 3 4\n0,1,2,5,6\n"

        blocks = parse_blocks(text)

        self.assertEqual(blocks, [(0, 1, 2, 3, 4), (0, 1, 2, 5, 6)])
        self.assertEqual(format_blocks(blocks), "0 1 2 3 4\n0 1 2 5 6\n")
```

- [ ] **Step 2: Implement parser and formatter**

Create `src/design_io.py`:

```python
from __future__ import annotations

from src.erdos835_one_color import Block


def parse_blocks(text: str) -> list[Block]:
    blocks: list[Block] = []
    for raw_line in text.splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#"):
            continue
        parts = line.replace(",", " ").split()
        block = tuple(sorted(int(part) for part in parts))
        blocks.append(block)
    return blocks


def format_blocks(blocks: list[Block]) -> str:
    return "".join(" ".join(str(point) for point in block) + "\n" for block in blocks)
```

- [ ] **Step 3: Run tests**

Run:

```powershell
python -m unittest discover -s tests -p test_design_io.py -v
```

Expected: parser tests pass.

---

## Task 4: Add D-Only Verifier

**Files:**
- Create: `src/verify_d_only.py`
- Create: `tests/test_verify_d_only.py`

- [ ] **Step 1: Write failing verifier test**

Create a small `t=1, v=6` toy exact cover:

```python
import unittest

from src.erdos835_one_color import OneColorConfig
from src.verify_d_only import verify_d_only


class VerifyDOnlyTests(unittest.TestCase):
    def test_toy_d_only_design_passes(self):
        config = OneColorConfig(v=6, t=1, extension_count=2)
        blocks = [(0, 1), (2, 3), (4, 5)]

        self.assertEqual(verify_d_only(config, blocks), [])

    def test_duplicate_point_cover_fails(self):
        config = OneColorConfig(v=6, t=1, extension_count=2)
        blocks = [(0, 1), (0, 2), (4, 5)]

        errors = verify_d_only(config, blocks)

        self.assertTrue(any("T:0" in error for error in errors))
```

- [ ] **Step 2: Implement verifier**

Create `src/verify_d_only.py`:

```python
from __future__ import annotations

from collections import Counter
from itertools import combinations

from src.erdos835_one_color import Block, OneColorConfig, format_block, iter_comb_tuples


def verify_d_only(config: OneColorConfig, blocks: list[Block]) -> list[str]:
    config.validate()
    counts: Counter[Block] = Counter()
    for block in blocks:
        if len(block) != config.t + 1:
            return [f"wrong block size: {format_block(block)}"]
        for subblock in combinations(block, config.t):
            counts[tuple(sorted(subblock))] += 1

    errors: list[str] = []
    for t_block in iter_comb_tuples(config.v, config.t):
        count = counts[t_block]
        if count != 1:
            errors.append(f"T:{format_block(t_block)} covered {count} times")
    return errors
```

- [ ] **Step 3: Run verifier tests**

Run:

```powershell
python -m unittest discover -s tests -p test_verify_d_only.py -v
```

Expected: verifier tests pass.

---

## Task 5: Add Fixed-D Conditional Model

**Files:**
- Create: `src/conditional_one_color.py`
- Create: `tests/test_conditional_one_color.py`

- [ ] **Step 1: Write conditional stats test**

Use a toy design from `tests/test_one_color.py`:

```python
import unittest

from src.conditional_one_color import compute_conditional_stats
from src.erdos835_one_color import OneColorConfig


class ConditionalOneColorTests(unittest.TestCase):
    def test_problem_835_conditional_counts_from_note(self):
        config = OneColorConfig.problem_835()

        stats = compute_conditional_stats(config, d_block_count=1197, allowed_u_count=35112)

        self.assertEqual(stats.variables, 386232)
        self.assertEqual(stats.constraints, 245784)
        self.assertEqual(stats.incidences, 2703624)
```

- [ ] **Step 2: Implement conditional stats**

Create `src/conditional_one_color.py`:

```python
from __future__ import annotations

from dataclasses import dataclass
from math import comb

from src.erdos835_one_color import OneColorConfig


@dataclass(frozen=True)
class ConditionalStats:
    variables: int
    constraints: int
    incidences: int


def compute_conditional_stats(
    config: OneColorConfig,
    *,
    d_block_count: int,
    allowed_u_count: int,
) -> ConditionalStats:
    non_d_five_sets = comb(config.v, config.t + 1) - d_block_count
    variables = config.extension_count * allowed_u_count
    constraints = config.extension_count * non_d_five_sets + allowed_u_count
    incidences = variables * (config.t + 3)
    return ConditionalStats(variables=variables, constraints=constraints, incidences=incidences)
```

- [ ] **Step 3: Add allowed-6-set construction**

Add a function:

```python
def allowed_u_blocks(config: OneColorConfig, d_blocks: set[Block]) -> list[Block]:
    d_set = set(d_blocks)
    allowed: list[Block] = []
    for u_block in iter_comb_tuples(config.v, config.t + 2):
        if not any(tuple(sorted(s_block)) in d_set for s_block in combinations(u_block, config.t + 1)):
            allowed.append(u_block)
    return allowed
```

- [ ] **Step 4: Test allowed-block filtering on toy data**

Add this test to `tests/test_conditional_one_color.py`:

```python
from src.conditional_one_color import allowed_u_blocks


    def test_allowed_u_blocks_remove_blocks_containing_d_block(self):
        config = OneColorConfig(v=4, t=1, extension_count=1)
        d_blocks = {(0, 1)}

        allowed = allowed_u_blocks(config, d_blocks)

        self.assertNotIn((0, 1, 2), allowed)
        self.assertNotIn((0, 1, 3), allowed)
        self.assertIn((0, 2, 3), allowed)
        self.assertIn((1, 2, 3), allowed)
```

- [ ] **Step 5: Implement conditional OPB export**

Rows are `X:j:U` only for allowed `U`. Columns are:

```text
P:j:S for each non-D 5-set S
U:U for each allowed U
```

Each row covers:

```text
P:j:S for the six S subset U
U:U
```

- [ ] **Step 6: Run conditional tests**

Run:

```powershell
python -m unittest discover -s tests -p test_conditional_one_color.py -v
```

Expected: conditional stats and toy filtering tests pass.

---

## Task 6: Run The Next Computational Experiment

**Files:**
- Create: `scripts/export_problem835_d_only_opb.sh`
- Create: `scripts/run_roundingsat_d_only_2h.sh`
- Modify: `README.md`

- [ ] **Step 1: Add D-only export script**

Create:

```bash
#!/usr/bin/env bash
set -euo pipefail

cd "$(dirname "$0")/.."

python3 -m src.erdos835_one_color d-only-opb \
  --output artifacts/problem835_d_only.opb \
  --symmetry-break triple-matching \
  --add-d-lower-counts \
  --no-comments
```

- [ ] **Step 2: Add D-only run script**

Create:

```bash
#!/usr/bin/env bash
set -euo pipefail

cd "$(dirname "$0")/.."

: "${TIME_LIMIT_SECONDS:=7200}"
: "${LOG:=artifacts/solver_logs/d_only_roundingsat_lp0_2h.log}"

/usr/bin/time -v artifacts/solvers/roundingsat \
  --lp=0 \
  "--time-limit=${TIME_LIMIT_SECONDS}" \
  --print-sol=1 \
  artifacts/problem835_d_only.opb \
  > "${LOG}" 2>&1
```

- [ ] **Step 3: Run smoke commands**

Run:

```powershell
wsl -d Ubuntu bash -lc "cd /mnt/e/code/835 && bash scripts/export_problem835_d_only_opb.sh"
wsl -d Ubuntu bash -lc "cd /mnt/e/code/835 && TIME_LIMIT_SECONDS=600 LOG=artifacts/solver_logs/d_only_roundingsat_lp0_10m.log bash scripts/run_roundingsat_d_only_2h.sh"
```

Expected: OPB generated; solver returns SAT/UNSAT/TIMELIMIT/UNKNOWN without crashing.

---

## Decision Rules After Task 6

- If D-only is `UNSAT`: this is stronger than the current target. Preserve log and rerun with proof logging/certificate support before making any public claim.
- If D-only is `SAT`: extract the D-blocks, verify them with `verify_d_only`, then run the fixed-D conditional model.
- If D-only times out: add stronger D-only symmetry breaking before returning to the full one-colour model.
- Do not run another raw strengthened one-colour portfolio until at least one smaller target has been tested.
