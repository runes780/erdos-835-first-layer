# Progress log

## 2026-05-31

Created the standalone repository:

```text
https://github.com/runes780/erdos-835-first-layer
```

Initial commit:

```text
99c9934 Add first-layer exact-cover toolkit
```

Work completed:

- encoded the one-colour first-layer exact-cover formulation for problem 835;
- implemented exact-cover statistics;
- implemented a stable sparse row generator;
- implemented OPB export;
- implemented a candidate verifier;
- added a small toy instance with tests;
- added a compact LaTeX working note;
- added a Pro-model prompt for the next mathematical attack;
- added PC/WSL execution guidance.

Local verification:

```text
python3 -m unittest discover -s tests -v
  -> 7 tests passed

bash scripts/wsl_smoke.sh
  -> passed

bash scripts/export_problem835_opb.sh
  -> produced artifacts/problem835_one_color.opb, about 56MB

pdflatex -interaction=nonstopmode erdos835_first_layer_note.tex
  -> produced a 2-page PDF
```

Machine decision:

- Current Mac: useful for development/export, not suitable for long raw solver
  runs because it has 16GB memory and low remaining disk space.
- Windows PC with i5-13400 and 32GB memory: suitable for first-stage one-colour
  OPB experiments under WSL2, with strict time and memory limits.

Current mathematical status:

- No solution claim.
- No solver result yet.
- Main target: decide whether the one-colour exact-cover system is UNSAT.
- If raw solving stalls, move to fixed-\(D_a\), symmetry breaking, or smaller
  derived subsystems.

