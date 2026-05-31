# Running on the 32GB i5-13400 Windows PC

Your Windows PC is the better execution target than the current Mac, but it is
still a medium-sized machine for this instance.  Treat the full one-colour
problem as a staged experiment, not as a guaranteed overnight solve.

Recommended setup:

- Use WSL2 Ubuntu.
- Keep at least 100GB free disk before exporting full OPB files and solver logs.
- Close memory-heavy applications before solver runs.
- If WSL memory is capped, set it to about 24GB-28GB, leaving Windows enough
  memory to remain stable.
- Prefer command-line pseudo-Boolean/SAT solvers.  GPU is not relevant here.

Suggested first run:

```bash
cd erdos-835-first-layer
bash scripts/wsl_smoke.sh
```

Then export the full one-colour OPB instance:

```bash
bash scripts/export_problem835_opb.sh
```

This creates:

```text
artifacts/problem835_stats.json
artifacts/problem835_one_color.opb
```

Do not start with the full 17-colour problem.  The best order is:

1. one-colour OPB export;
2. one-colour solver run with a strict time limit;
3. fixed-\(D_a\) or symmetry-reduced variants if the raw instance is too hard;
4. only then consider assembling multiple colours.

For a 32GB PC, a useful first solver budget is 2-6 hours with solver logs
enabled.  If memory exceeds 26GB or the machine begins swapping, stop and move
to smaller derived subsystems.
