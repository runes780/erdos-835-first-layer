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

Mathematical status at that checkpoint:

- No solution claim.
- No solver result yet at that time.
- Main target: decide whether the one-colour exact-cover system is UNSAT.
- If raw solving stalls, move to fixed-\(D_a\), symmetry breaking, or smaller
  derived subsystems.

Added Windows-Codex handoff:

- `TASKS.md` now gives the exact task sequence for Codex on the Windows PC:
  clone, smoke test, OPB export, optional bounded solver attempt, logging,
  result classification, and next-step decision rules.

Windows WSL continuation run:

- Repository cloned on the Windows PC at `E:\code\835` from
  `https://github.com/runes780/erdos-835-first-layer.git`.
- WSL environment: Ubuntu 24.04.1 LTS, Python 3.12.3.
- Available WSL memory was about 15GiB with 4GiB swap, below the recommended
  24GiB-28GiB solver budget in `docs/pc_execution.md`.
- Disk available on `/mnt/e`: about 117GB.
- `python3 -m unittest discover -s tests -v` passed all 7 tests.
- `bash scripts/wsl_smoke.sh` passed and generated `artifacts/toy.opb`.
- `bash scripts/export_problem835_opb.sh` generated:

```text
artifacts/problem835_stats.json
artifacts/problem835_one_color.opb
```

Generated OPB evidence:

```text
size: 56M
lines: 284089
sha256: 6135434d0edc4f76b4f91fa7c9e6b30e503dab794bd1d010163acc339e89b7e4
```

The generated statistics matched the README headline counts:

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

Solver status:

- No compatible solver was found in PATH among `roundingSat`, `roundingsat`,
  `sat4j-pb`, `minisat+`, and `clasp`.
- Per `TASKS.md`, no bounded solver attempt was started.
- Result classification: not run because no solver was available.

Windows WSL solver continuation:

- Added `C:\Users\runes780\.wslconfig` with WSL2 memory set to 28GB, 16
  processors, and 8GB swap, then restarted WSL.
- Confirmed WSL memory after restart: about 27GiB RAM and 8GiB swap.
- Downloaded the official RoundingSat Linux x86_64 static binary from the
  upstream GitLab artifact into `artifacts/solvers/roundingsat`.
- RoundingSat identity from solver log:

```text
RoundingSat 2
branch HEAD
commit d4edbf7
binary sha256: cf115250c7539000b39b950d53ddf9d1dfd4ca0d004caf52038a116e7efe3ed5
```

Parser issue found and fixed:

- The previous OPB export used inline column comments after each semicolon,
  for example `; * T:0,1,2,3`.
- RoundingSat treats those inline comments as malformed input and immediately
  reports `Inconsistent input constraint`.
- Added a `--no-column-comments` export option and updated the README plus WSL
  export scripts to use `--no-row-comments --no-column-comments`.
- Added a regression test for solver-compatible comment-free OPB export.
- Verification after the fix: `python3 -m unittest discover -s tests -v`
  passed all 8 tests.
- The regenerated toy OPB was accepted by RoundingSat and returned SAT.

Regenerated solver-compatible full OPB:

```text
size: 51M
lines: 284089
sha256: 1723a177b783386cd238c440ecd4055bdb03fcf6c9fd0ba23f54e05f3ff10243
```

The statistics still matched the README headline counts.

Bounded raw RoundingSat attempt:

```text
command: /usr/bin/time -v timeout 2h artifacts/solvers/roundingsat --print-sol=1 artifacts/problem835_one_color.opb
ulimit_v_kb: 27262976
log: artifacts/solver_logs/raw_one_colour_roundingsat_2h_fixed.log
exit: 124
wall time: 2:03:29
peak RSS: 1662740 KB
swap: 0
solver status line: s UNKNOWN
result classification: UNKNOWN / timeout
```

Selected final solver counters:

```text
#variables 617253
#constraints 568176
conflicts 9200
decisions 54456
propagations 19877484
input clauses 284088
input cardinalities 284088
formula constraints 568176
LP total time 2747.5 s
```

Interpretation:

- This is not evidence of SAT or UNSAT.
- The raw one-colour OPB instance did not finish within the first bounded
  2-hour RoundingSat run.
- Memory was not the bottleneck in this run; the process stayed near 1.6GB RSS
  and did not swap.
- Next recommended direction is mathematical/model reduction: fixed-\(D_a\),
  symmetry breaking, or smaller derived subsystems rather than repeating the
  same raw model unchanged.

Mathematical audit incorporated:

- Added the complement-invariance proof for \(S(k-1,k,2k)\) when \(k\) is
  even.
- Recorded the corrected \(k=16\) layer equation and the first-layer packing
  proposition: an \(LS(4,5,21)\) colouring \(D\) plus eleven simultaneous
  point-extensions \(g_1,\ldots,g_{11}\) satisfying pointwise complementarity
  on every 6-set.
- Added the one-colour parameter tables, intersection-number tables, the
  fixed-4-set \(K_{17}\) local model, and the fixed-block local feasibility
  argument to `notes/erdos835_first_layer_note.tex`.
- Recorded the larger combined \(D+g_1+\cdots+g_{11}\) first-layer exact-cover
  target as a later-stage model:

```text
rows / Boolean row variables: 10493301
exact-cover columns: 5446749
row-column incidences: 92594733
```

Implemented strengthened one-colour OPB export:

- Added `--symmetry-break triple-matching`, which forces the nine \(D_a\)-blocks
  through `{0,1,2}`:

```text
{0,1,2,3,4}, {0,1,2,5,6}, ..., {0,1,2,19,20}
```

- Added `--add-g4-counts`, which appends the redundant constraints
  `sum_{U superset T} x_{j,U}=8` for each \(j\) and 4-set \(T\).
- Added:

```text
scripts/export_problem835_augmented_opb.sh
scripts/run_roundingsat_lp0_augmented_6h.sh
```

Verification after the implementation:

```text
python -m unittest discover -s tests -v
  -> 11 tests passed
```

LaTeX note compilation was not run because `pdflatex` is not installed in
either Windows PATH or the WSL Ubuntu environment.

Generated strengthened OPB:

```text
path: artifacts/problem835_one_color_augmented.opb
header: * #variable= 617253 #constraint= 349932
size: 144M
lines: 349933
sha256: b8598dbb03a8a39c5d5ed40d352fa5b5366aed0c4ba4130e2d901c4645bb32e5
```

Short strengthened RoundingSat benchmark:

```text
command: TIME_LIMIT_SECONDS=60 LOG=artifacts/solver_logs/augmented_one_colour_roundingsat_lp0_60s.log bash scripts/run_roundingsat_lp0_augmented_6h.sh
solver option: --lp=0
solver status line: s TIMELIMIT
result classification: UNKNOWN / timeout
conflicts: 103961
decisions: 388792
propagations: 231614420
LP total time: 0 s
wall time: 1:06.45
peak RSS: 578120 KB
```

Interpretation:

- This is not evidence of SAT or UNSAT.
- The strengthened OPB is syntactically accepted by RoundingSat.
- Disabling LP remains the right solver setting for the next bounded run.
- The next useful computation is a 10-minute to 6-hour strengthened
  `--lp=0` run, not another default-LP raw run.

Follow-up strengthened benchmark:

```text
command: TIME_LIMIT_SECONDS=600 LOG=artifacts/solver_logs/augmented_one_colour_roundingsat_lp0_10m.log bash scripts/run_roundingsat_lp0_augmented_6h.sh
solver option: --lp=0
solver status line: s TIMELIMIT
result classification: UNKNOWN / timeout
conflicts: 860430
decisions: 2832254
propagations: 1942783662
LP total time: 0 s
wall time: 10:10.15
peak RSS: 656836 KB
```

This remained memory-light and did not produce SAT/UNSAT.

Added another low-cost redundant constraint family:

- Implemented `--add-d-lower-counts`, adding the forced \(D_a\) lower-subset
  counts for subset sizes 0, 1, 2, and 3.
- The augmented export script now includes these constraints as well as the
  triple-matching symmetry break and G4 constraints.
- Verification:

```text
python -m unittest discover -s tests -v
  -> 13 tests passed
bash -n scripts/export_problem835_augmented_opb.sh
bash -n scripts/run_roundingsat_lp0_augmented_6h.sh
  -> passed
```

Regenerated strengthened OPB with \(D_a\) lower counts:

```text
path: artifacts/problem835_one_color_augmented.opb
header: * #variable= 617253 #constraint= 351494
size: 149M
lines: 351495
sha256: b5d1c392b35fddc33289ed1263dd5f3c91409a2983e75c1240b0aaae38f4f0a0
```

Short benchmark for the regenerated strengthened OPB:

```text
command: TIME_LIMIT_SECONDS=60 LOG=artifacts/solver_logs/augmented_dlower_one_colour_roundingsat_lp0_60s.log bash scripts/run_roundingsat_lp0_augmented_6h.sh
solver option: --lp=0
solver status line: s TIMELIMIT
result classification: UNKNOWN / timeout
conflicts: 102916
decisions: 380959
propagations: 226581315
LP total time: 0 s
wall time: 1:07.04
peak RSS: 585808 KB
```

The added \(D_a\) lower counts are accepted by RoundingSat and do not create
memory pressure.  They also do not produce an immediate contradiction in the
first 60 seconds.

Implemented a portfolio launcher:

- Added `src/roundingsat_portfolio.py`, which launches independent RoundingSat
  variants with separate logs and a JSONL manifest.
- Added `scripts/run_roundingsat_portfolio.sh`.
- The launcher avoids shell quoting problems by building argv arrays in
  Python instead of composing one large shell command.
- Verification:

```text
python -m unittest discover -s tests -v
  -> 16 tests passed
bash -n scripts/run_roundingsat_portfolio.sh
  -> passed
DRY_RUN=1 SKIP_BASELINE=1 MAX_JOBS=2 ... bash scripts/run_roundingsat_portfolio.sh
  -> printed count0 and count1 dry-run entries
```

Started a first portfolio tier while keeping the existing baseline run:

```text
baseline roundingsat PID: 24
portfolio launcher manifest: artifacts/solver_logs/portfolio_extra_6h.jsonl
variants:
  count0      --prop-counting=0
  count1      --prop-counting=1
  luby50      --luby-mult=50
  luby200     --luby-mult=200
  lubybase15  --luby-base=1.5
```

Initial resource check after portfolio launch:

```text
active RoundingSat instances: 6
per-instance RSS: about 558MB to 726MB
WSL memory used: about 4.0GiB of 27GiB
swap used: 0B
```

Interpretation:

- This is a reasonable first CPU-increase tier.
- It uses roughly six CPU cores instead of one, without memory pressure.
- Escalating to 10-12 extra variants is possible later, but should be reserved
  for when the PC can be dedicated to the run.

## 2026-06-01

Baseline plus portfolio runs all reached `TIMELIMIT`.

Best first/follow-up branch:

```text
lubybase15, 15,372,000 conflicts
```

Outcome:

- No SAT witness.
- No UNSAT certificate.
- No mathematical exclusion of \(k=16\).
- Memory stayed healthy and swap stayed at 0B, so the failure mode was search
  hardness rather than memory pressure.

Final watchdog report:

```text
action: stop_no_result
running roundingsat processes: 0
completed followups: 1
```

Timeout table:

```text
lubybase15       TIMELIMIT   15,372,000 conflicts
luby200          TIMELIMIT   12,646,000 conflicts
count0_luby50    TIMELIMIT   12,265,000 conflicts
luby50_bumpfalse TIMELIMIT   11,787,000 conflicts
baseline         TIMELIMIT    8,300,000 conflicts
count1           TIMELIMIT    3,881,000 conflicts
```

Decision:

- Stop repeating the raw strengthened one-colour OPB as the only strategy.
- Keep the one-colour exact-cover target as the main certifiable target.
- Next implementation target: split the work into D-only \(S(4,5,21)\) search
  and fixed-\(D_a\) conditional one-colour search.

Implemented the first post-timeout split:

- Added D-only OPB export for the \(S(4,5,21)\) block system.
- Added stable block-list I/O helpers.
- Added a D-only verifier.
- Added fixed-\(D_a\) conditional one-colour stats and OPB export.
- Added D-only export/run scripts.

Verification:

```text
python -m unittest discover -s tests -v
  -> 32 tests passed
```

Generated D-only OPB:

```text
path: artifacts/problem835_d_only.opb
header: * #variable= 20349 #constraint= 7556
size: 5.8M
sha256: a75e8e80da66b52d7dc6f589a7ffda663be286940b22fbb7944008fb0a073ea8
```

D-only 10-minute RoundingSat smoke:

```text
command: TIME_LIMIT_SECONDS=600 LOG=artifacts/solver_logs/d_only_roundingsat_lp0_10m.log bash scripts/run_roundingsat_d_only_2h.sh
solver option: --lp=0
solver status line: s TIMELIMIT
result classification: UNKNOWN / timeout
conflicts: 1,486,000
wall time: 10:05.75
peak RSS: 219,984 KB
swap: 0
```

Interpretation:

- D-only is much smaller and memory-light.
- No quick D-only SAT/UNSAT result appeared in 10 minutes.
- This is now a suitable target for stronger D-only symmetry breaking and
  encoding comparisons before returning to the full one-colour shadow.

Revised next target after the later planning discussion:

- The main branch is now the staged extension ladder \(E_m\), not D-only-first.
- `E_1` keeps \(D_a\) plus one point-extension family.
- `E_m` for `m >= 2` adds cross-family disjointness
  `sum_j x_{j,U} <= 1`.
- Planned ladder: `E_1 -> E_2 -> E_4 -> E_8 -> E_11`.
- D-only remains useful, but as an auxiliary diagnostic.

Implemented `E_m` support:

- Added `src/extension_ladder.py`.
- Added `tests/test_extension_ladder.py`.
- Added `scripts/export_problem835_e1_opb.sh`.
- Added `scripts/run_roundingsat_e1_2h.sh`.
- Added the plan file
  `docs/superpowers/plans/2026-06-01-extension-ladder-em.md`.

Verification:

```text
python -m unittest discover -s tests -v
  -> 39 tests passed

wsl -d Ubuntu bash -lc "cd /mnt/e/code/835 && bash -n scripts/export_problem835_e1_opb.sh && bash -n scripts/run_roundingsat_e1_2h.sh"
  -> passed
```

Generated `E_1` OPB:

```text
path: artifacts/problem835_e1.opb
header: * #variable= 74613 #constraint= 26343
size: 4.4M
sha256: a24524b5d26534bfcf45095a9a924ee7af48d4724116eb6534a924d0756ef7b8
```

`E_1` 5-minute RoundingSat smoke:

```text
command: TIME_LIMIT_SECONDS=300 LOG=artifacts/solver_logs/e1_roundingsat_lp0_5m.log bash scripts/run_roundingsat_e1_2h.sh
solver option: --lp=0
solver status line: s TIMELIMIT
result classification: UNKNOWN / timeout
conflicts: 875,035
wall time: 5:04.05
peak RSS: 174,204 KB
swap: 0
```

Interpretation:

- No SAT/UNSAT result yet.
- The new `E_1` target is dramatically smaller than full one-colour and lighter
  than D-only in memory.
- Because it is single-core and about 174MB RSS in this smoke run, the next
  reasonable execution step is a portfolio of many `E_1` variants before
  escalating to `E_2`.

Implemented stronger `E_1` normalization from the later model advice:

- Added `triple-matching-off-triple`, which appends the safe block
  `D:0,1,3,5,7` after the triple-matching normalization.
- Added `--add-d-lower-counts` to the staged `E_m` OPB exporter.
- Updated `scripts/export_problem835_e1_opb.sh` to use both strengthening
  options.

Verification:

```text
python -m unittest discover -s tests -p "test_extension_ladder.py" -v
  -> 9 tests passed

python -m unittest discover -s tests -p "test_one_color.py" -v
  -> 14 tests passed
```

Regenerated stronger `E_1` OPB:

```text
path: artifacts/problem835_e1.opb
header: * #variable= 74613 #constraint= 27906
size: 9.2M
sha256: 94126fe65c3bd94d2a036eddbabb18e55d58f42cd6795abb2ba84662a40cc21e
```

Stronger `E_1` 5-minute smoke:

```text
command: TIME_LIMIT_SECONDS=300 LOG=artifacts/solver_logs/e1_stronger_roundingsat_lp0_5m.log bash scripts/run_roundingsat_e1_2h.sh
solver option: --lp=0
solver status line: s TIMELIMIT
result classification: UNKNOWN / timeout
conflicts: 755,349
wall time: 5:03.39
peak RSS: 161,720 KB
swap: 0
```

Stronger `E_1` 10-minute six-way portfolio:

```text
command: INPUT=artifacts/problem835_e1.opb TIME_LIMIT_SECONDS=600 MAX_JOBS=6 PREFIX=e1_stronger_portfolio_10m MANIFEST=artifacts/solver_logs/e1_stronger_portfolio_10m.jsonl bash scripts/run_roundingsat_portfolio.sh
result classification: all TIMELIMIT
```

Portfolio table:

```text
lubybase15  TIMELIMIT  1,079,995 conflicts  peak RSS 129,252 KB
luby50      TIMELIMIT    939,773 conflicts  peak RSS 150,372 KB
count0      TIMELIMIT    935,212 conflicts  peak RSS 166,848 KB
baseline    TIMELIMIT    899,749 conflicts  peak RSS 161,952 KB
luby200     TIMELIMIT    887,136 conflicts  peak RSS 173,320 KB
count1      TIMELIMIT    491,226 conflicts  peak RSS 265,852 KB
```

Interpretation:

- No mathematical result yet.
- `lubybase15` is again the strongest RoundingSat variant.
- Memory remains negligible for this machine, so a longer `E_1` portfolio can
  use more CPU without risking swap.

Started a longer stronger `E_1` portfolio:

```text
command: INPUT=artifacts/problem835_e1.opb TIME_LIMIT_SECONDS=7200 MAX_JOBS=10 PREFIX=e1_stronger_portfolio_2h MANIFEST=artifacts/solver_logs/e1_stronger_portfolio_2h.jsonl bash scripts/run_roundingsat_portfolio.sh
variants: baseline, count0, count1, luby50, luby200, lubybase15, lubybase3, bumpfalse, cancel0, bumplits0
initial per-process RSS: about 72MB to 88MB
initial WSL memory used: about 1.4GiB of 27GiB
initial swap: 0B
```

Final result of the longer stronger `E_1` portfolio:

```text
result classification: all TIMELIMIT
active roundingsat processes after run: 0
WSL memory after run: about 642MiB used of 27GiB
swap after run: 0B
```

Final table:

```text
lubybase15  TIMELIMIT  5,250,782 conflicts  peak RSS 231,372 KB
count0      TIMELIMIT  4,697,372 conflicts  peak RSS 399,232 KB
luby50      TIMELIMIT  4,402,180 conflicts  peak RSS 409,796 KB
luby200     TIMELIMIT  4,243,352 conflicts  peak RSS 499,656 KB
baseline    TIMELIMIT  4,089,435 conflicts  peak RSS 471,460 KB
cancel0     TIMELIMIT  4,086,835 conflicts  peak RSS 471,612 KB
bumpfalse   TIMELIMIT  4,082,594 conflicts  peak RSS 471,844 KB
bumplits0   TIMELIMIT  4,073,628 conflicts  peak RSS 471,760 KB
lubybase3   TIMELIMIT  3,129,844 conflicts  peak RSS 462,676 KB
count1      TIMELIMIT  1,906,750 conflicts  peak RSS 499,072 KB
```

Verification after this run:

```text
python -m unittest discover -s tests -v
  -> 42 tests passed
```

Interpretation:

- No SAT witness and no UNSAT certificate.
- The strongest OPB/RoundingSat branch remains `lubybase15`.
- `count1` remains consistently poor on this instance.
- Memory is not the limiting factor.  The next main step should be a CNF/CDCL
  version of `E_1`, preferably with Kissat/CaDiCaL, rather than simply extending
  the same OPB portfolio.

Implemented pairwise DIMACS CNF export for staged `E_m`:

- Added `src/extension_ladder_cnf.py`.
- Added `tests/test_extension_ladder_cnf.py`.
- Added `scripts/export_problem835_e1_cnf.sh`.
- Added `scripts/run_cadical_e1_2h.sh`.

CNF encoding:

```text
exact-one constraints: one positive clause plus all pairwise negative clauses
E_m disjointness constraints: pairwise negative clauses
symmetry break: unit clauses
cardinality networks: not used
```

Generated `E_1` CNF:

```text
path: artifacts/problem835_e1.cnf
header: p cnf 74613 3607768
lines: 3,607,769
size: 57M
sha256: 690112c309acc78a7dd58fee800f5f8097f479bab6177b6179980f6a51b4269f
```

Prepared CaDiCaL without sudo:

```text
method: apt-get download cadical; dpkg-deb -x ...
path: artifacts/solvers/cadical_pkg/usr/bin/cadical
version output: 1.7.3
```

CaDiCaL 10-minute CNF smoke:

```text
command: TIME_LIMIT_SECONDS=600 LOG=artifacts/solver_logs/e1_cadical_10m.log bash scripts/run_cadical_e1_2h.sh
result classification: UNKNOWN / timeout
exit status: 124
conflicts: 2,980,586
wall time: 10:00.04
peak RSS: 696,880 KB
swap: 0
```

Interpretation:

- CNF/CDCL route is now operational.
- No SAT witness or UNSAT certificate yet.
- CaDiCaL uses more memory than RoundingSat on `E_1`, but still far below the
  machine limit.
- A 2-hour CaDiCaL baseline was started:

```text
command: TIME_LIMIT_SECONDS=7200 LOG=artifacts/solver_logs/e1_cadical_2h.log bash scripts/run_cadical_e1_2h.sh
initial status: running normally
initial RSS: about 500MB
```

Final CaDiCaL 2-hour CNF baseline:

```text
result classification: UNKNOWN / timeout
exit status: 124
conflicts: 34,615,957
decisions: 101,541,116
propagations: 22,753,179,630
wall time: 2:00:00
peak RSS: 930,980 KB
swap: 0
```

Interpretation:

- No SAT witness and no UNSAT certificate.
- CNF/CDCL is operational and memory-light, but default CaDiCaL did not solve
  `E_1` within 2 hours.
- Compared with OPB/RoundingSat, CaDiCaL reaches many more conflicts in the
  same wall-clock budget, so CNF remains the better next engineering route.
- Next useful experiment: run a small CaDiCaL parameter portfolio or obtain a
  Kissat binary, rather than returning to the same OPB encoding.

Prepared the CaDiCaL parameter portfolio:

```text
added: src/cadical_portfolio.py
added: tests/test_cadical_portfolio.py
added: scripts/run_cadical_portfolio.sh
portfolio variants: -P1, -P2, -O1, -O2, -L1, -L10, mixed variants
recommended first tier: skip baseline, 6 jobs, 1 hour each
```

The intent is to use more of the CPU without exceeding memory: CaDiCaL's
2-hour baseline peaked below 1GB RSS, so a six-way portfolio should remain
well inside a 32GB machine while testing materially different search paths.

Started the first CaDiCaL portfolio tier:

```text
command: SKIP_BASELINE=1 MAX_JOBS=6 TIME_LIMIT_SECONDS=3600 PREFIX=e1_cadical_portfolio_1h MANIFEST=artifacts/solver_logs/e1_cadical_portfolio_1h.jsonl bash scripts/run_cadical_portfolio.sh
variants: -P1, -P2, -O1, -O2, -L1, -L10
manifest: artifacts/solver_logs/e1_cadical_portfolio_1h.jsonl
initial status: all six cadical processes running
initial memory: about 3.3GiB used in WSL, 0B swap
```

After the initial resource check, launched the remaining non-baseline CaDiCaL
variants too:

```text
command: SKIP_BASELINE=1 START_INDEX=6 MAX_JOBS=3 TIME_LIMIT_SECONDS=3600 PREFIX=e1_cadical_portfolio_1h_extra MANIFEST=artifacts/solver_logs/e1_cadical_portfolio_1h_extra.jsonl bash scripts/run_cadical_portfolio.sh
variants: -P1 -O1, -P2 -O1, -P1 -L1
combined active branches: 9
post-launch memory: about 4.3GiB used in WSL, 0B swap
```

Final result of the 9-branch CaDiCaL portfolio:

```text
result classification: UNKNOWN / timeout on every branch
SAT witness: none
UNSAT certificate: none
swap: 0
```

Per-branch summary:

```text
preprocess1_optimize1: conflicts 3,942,942; decisions 8,968,208; RSS 740,300 KB
preprocess1_local1:    conflicts 3,926,112; decisions 8,921,308; RSS 736,776 KB
preprocess1:           conflicts 3,890,606; decisions 8,249,031; RSS 753,712 KB
preprocess2_optimize1: conflicts 3,807,999; decisions 8,688,431; RSS 761,816 KB
local10:               conflicts 3,638,926; decisions 8,637,942; RSS 739,740 KB
local1:                conflicts 3,487,636; decisions 8,381,461; RSS 727,616 KB
preprocess2:           conflicts 3,421,414; decisions 8,286,646; RSS 711,660 KB
optimize1:             conflicts 3,276,824; decisions 8,115,461; RSS 704,696 KB
optimize2:             conflicts 2,016,117; decisions 7,543,278; RSS 748,776 KB
```

Interpretation:

- Running nine CaDiCaL branches concurrently used memory safely, but each
  branch got less CPU than the single 2-hour baseline.
- The aggregate portfolio explored different search paths, but no branch
  solved `E_1`.
- The best next step is not to repeat the same 9-way, 1-hour portfolio.  Better
  next options are either a stronger CDCL solver such as Kissat on the same
  CNF, or a more informative encoding/symmetry change before another long run.

Prepared Kissat from the official release binary:

```text
source: https://github.com/arminbiere/kissat/releases/tag/rel-4.0.4
asset: kissat-4.0.4-linux-amd64.zip
installed binary: artifacts/solvers/kissat
version: 4.0.4
```

Kissat 10-minute smoke on the `E_1` CNF:

```text
command: timeout 600 artifacts/solvers/kissat -s artifacts/problem835_e1.cnf
log: artifacts/solver_logs/e1_kissat_10m.log
result classification: UNKNOWN / timeout
SAT witness: none
UNSAT certificate: none
conflicts: 4,860,049
decisions: 75,808,300
propagations: 4,219,292,529
conflict rate: 8,124.91 per second
Kissat reported RSS: 222 MB
```

Interpretation:

- Kissat is materially faster than the previous CaDiCaL 10-minute smoke
  (4.86M vs 2.98M conflicts).
- It also uses much less memory on this instance.
- The next run should be a longer single Kissat run on the same `E_1` CNF
  before changing the mathematical encoding.

Kissat 2-hour run on the same `E_1` CNF:

```text
command: timeout 7200 artifacts/solvers/kissat -s artifacts/problem835_e1.cnf
log: artifacts/solver_logs/e1_kissat_2h.log
result classification: UNKNOWN / timeout
exit status: 124
SAT witness: none
UNSAT certificate: none
conflicts: 57,070,395
decisions: 880,874,492
propagations: 48,143,111,456
conflict rate: 7,930.41 per second
Kissat reported RSS: 224 MB
/usr/bin/time peak RSS: 229,012 KB
wall time: 2:00:00
swap: 0
```

Interpretation:

- Kissat is the best tested solver on this CNF so far by both speed and memory.
- Even 57M conflicts did not decide `E_1`, so the next step should not be a
  blind repeat of the same 2-hour command.
- The useful next decision is strategic: ask a stronger model to review whether
  to add stronger symmetry/redundant constraints, change cardinality encoding,
  try another CDCL solver portfolio, or move to a different staged target.

Pro-model audit and follow-up implementation:

```text
audit correction: the current E_1 CNF is not D-lower-count strengthened
actual E_1 CNF: pairwise exact-one + triple/off-triple symmetry units
OPB ladder before follow-up: supported D lower-count constraints, not G4
```

Implemented the recommended next scaffolding:

```text
CNF generator:
  added --force-d-block for branch units
  Branch A unit: D:0,1,3,6,8
  Branch B unit: D:0,1,3,6,9
  E_1 branch CNF stats: 74,613 variables, 3,607,769 clauses

OPB ladder generator:
  added --add-g4-counts
  E_1 G4+D-lower branch OPB header:
    * #variable= 74613 #constraint= 33892

scripts:
  scripts/export_problem835_e1_branch_cnfs.sh
  scripts/export_problem835_e1_g4_branch_opbs.sh
  scripts/run_kissat_e1_branch_2h.sh
  scripts/run_roundingsat_e1_g4_branch_1h.sh
```

This keeps the unchanged CNF results separate from the next branch-split and
G4-strengthened experiments.

Started Experiment 1, the residual-orbit `E_1` CNF split:

```text
command: bash scripts/export_problem835_e1_branch_cnfs.sh
Branch A CNF: artifacts/problem835_e1_branch_a.cnf
Branch A sha256: 43e921ec164edc86f5e3937d3902f38bb47a9ceadf4d845aabd58b41217c45d3
Branch B CNF: artifacts/problem835_e1_branch_b.cnf
Branch B sha256: f89b9ba94d31e91fd1851ada595bf65418e121883fab3fee5abc9ee4330fd41a
per-branch stats: 74,613 variables, 3,607,769 clauses
```

Launched both Kissat branch runs:

```text
Branch A command: BRANCH=a TIME_LIMIT_SECONDS=7200 bash scripts/run_kissat_e1_branch_2h.sh
Branch A log: artifacts/solver_logs/e1_kissat_branch_a_2h.log
Branch B command: BRANCH=b TIME_LIMIT_SECONDS=7200 bash scripts/run_kissat_e1_branch_2h.sh
Branch B log: artifacts/solver_logs/e1_kissat_branch_b_2h.log
initial status: both kissat processes running
```

Prepared Experiment 2 inputs while Experiment 1 runs:

```text
command: bash scripts/export_problem835_e1_g4_branch_opbs.sh
Branch A OPB: artifacts/problem835_e1_g4_branch_a.opb
Branch A sha256: c3f9a2bd19b5e679cbb27c3f050918fc62dc7d371d6df74e12815b6b5283c877
Branch B OPB: artifacts/problem835_e1_g4_branch_b.opb
Branch B sha256: 29624253257a942fdb8226d84d87035d743a087730acf58152299823dc988598
per-branch header: * #variable= 74613 #constraint= 33892
```

Final result of Experiment 1, the residual-orbit `E_1` CNF split:

```text
Branch A result classification: UNKNOWN / timeout
Branch A conflicts: 48,117,911
Branch A decisions: 839,688,559
Branch A propagations: 40,541,872,067
Branch A peak RSS: 265,716 KB
Branch A wall time: 2:00:00

Branch B result classification: UNKNOWN / timeout
Branch B conflicts: 47,834,751
Branch B decisions: 826,186,962
Branch B propagations: 39,861,209,252
Branch B peak RSS: 250,580 KB
Branch B wall time: 2:00:00
```

Interpretation:

- No SAT witness and no UNSAT certificate.
- The branch split did not decide `E_1` under the current pairwise CNF in a
  2-hour Kissat run.
- This matches the Pro-model decision tree: proceed to Experiment 2, the
  G4-strengthened branch OPBs, instead of repeating the unchanged CNF run.

Started Experiment 2, the G4-strengthened branch OPB run:

```text
Branch A command: BRANCH=a TIME_LIMIT_SECONDS=3600 bash scripts/run_roundingsat_e1_g4_branch_1h.sh
Branch A log: artifacts/solver_logs/e1_g4_branch_a_roundingsat_lp0_1h.log
Branch B command: BRANCH=b TIME_LIMIT_SECONDS=3600 bash scripts/run_roundingsat_e1_g4_branch_1h.sh
Branch B log: artifacts/solver_logs/e1_g4_branch_b_roundingsat_lp0_1h.log
initial status: both roundingsat processes running
initial memory: about 843MiB used in WSL, 0B swap
```

Final result of Experiment 2, the G4-strengthened branch OPB run:

```text
Branch A result classification: TIMELIMIT / timeout
Branch A conflicts: 4,760,000
Branch A total solve time: 3540.16 s
Branch A propagation time: 2765.13 s
Branch A conflict-analysis time: 736.124 s
Branch A peak RSS: 397,556 KB
Branch A wall time: 1:00:22
Branch A exit status: 4

Branch B result classification: TIMELIMIT / timeout
Branch B conflicts: 4,658,000
Branch B total solve time: 3574.53 s
Branch B propagation time: 2766.64 s
Branch B conflict-analysis time: 734.809 s
Branch B peak RSS: 411,556 KB
Branch B wall time: 1:00:22
Branch B exit status: 4
```

Interpretation:

- No SAT witness and no UNSAT certificate.
- G4 OPB strengthening did not decide either `E_1` branch within a 1-hour
  RoundingSat `--lp=0` budget.
- Memory use stayed low, so the timeout is search complexity rather than RAM
  exhaustion.
- This follows the Pro-model decision tree toward Experiment 3: test `E_2`
  with the same two residual-orbit D branches before attempting larger `E_m`
  or full one-colour shadow runs.
