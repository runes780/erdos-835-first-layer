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
python3 -m src.erdos835_one_color opb --no-row-comments --output artifacts/problem835_one_color.opb
```

For the 32GB i5-13400 Windows PC, see `docs/pc_execution.md` and
`docs/solver_runbook.md`.  The recommended path is WSL2 Ubuntu, one-colour OPB
first, and strict solver time/memory limits.

If this repo is opened by Codex on the Windows PC, start from `TASKS.md`.

## Files

- `src/erdos835_one_color.py`: parameter model, statistics, and sparse row
  generator.
- `src/verify_one_color.py`: verifier for candidate one-color solutions.
- `tests/test_one_color.py`: unit tests, including a small resolvable toy
  instance.
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
