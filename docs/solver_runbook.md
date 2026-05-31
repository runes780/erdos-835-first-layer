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
Run raw one-colour OPB for 2-6 hours
  |
  +-- UNSAT -> verify certificate -> write formal note
  |
  +-- SAT -> verify witness -> analyze structure -> try compatibility
  |
  +-- UNKNOWN/timeout -> fix D_a or add symmetry breaking -> rerun
  |
  +-- memory blowup -> reduce model before further raw solving
```

