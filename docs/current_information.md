# Current information summary

Date: 2026-06-01

This document records the working state of the Erdős problem 835 investigation
captured in this repository.  It is a working record, not a claim of a solution.

## Mathematical status

The current route is:

```text
Problem 835 colouring
  -> large-set formulation LS(k-1,k,2k)
  -> first remaining serious case k=16
  -> first-layer object on 21 points over F_17
  -> one-colour exact-cover shadow
```

The working assumptions from the previous reductions are:

- A colouring for the relevant case gives an \(LS(k-1,k,2k)\).
- Known necessary conditions leave \(k=16\), with \(k+1=17\), as the first
  serious case.
- The \(k=16\) first-layer derivation gives a 21-point object with one
  \(LS(4,5,21)\) map \(D\) and eleven point-extension maps \(g_j\) on 6-sets.
- Fixing one colour \(a\in\mathbb F_{17}\) gives a pure exact-cover system.

The one-colour exact-cover system remains the certifiable target, but the
active computation now attacks it through a staged extension ladder \(E_m\).
If any necessary stage is UNSAT, then the \(k=16\) first-layer object cannot
exist.  If a stage is SAT, it only says that weaker shadow is consistent.

The current strengthened version keeps the same Boolean rows but appends two
auditable families of constraints:

- a safe triple-matching symmetry break through `{0,1,2}`;
- redundant relative-design constraints
  `sum_{U superset T} x_{j,U}=8` for every extension layer `j` and every 4-set
  `T`.
- redundant \(D_a\) lower-subset count constraints for subset sizes
  0, 1, 2, and 3.

The strengthened one-colour OPB has now been tested with a baseline run,
a portfolio run, and one automatic follow-up portfolio.  All attempts reached
`TIMELIMIT`; no SAT witness or UNSAT certificate was produced.  The best
observed branch was `lubybase15`, reaching 15,372,000 conflicts in the
follow-up run.

The post-timeout route has been revised after the later planning discussion:

1. `E_1`: \(D_a\) plus one point-extension family.
2. `E_2`, `E_4`, `E_8`: add more extension families with cross-family
   disjointness.
3. `E_11`: recover the staged one-colour shadow.
4. D-only and fixed-\(D_a\) conditional searches remain auxiliary diagnostics.

The first `E_1` OPB was generated with the triple-matching symmetry break:

```text
variables: 74613
constraints: 26343
file size: 4.4M
sha256: a24524b5d26534bfcf45095a9a924ee7af48d4724116eb6534a924d0756ef7b8
```

A 5-minute RoundingSat `--lp=0` smoke run on this `E_1` instance reached
`s TIMELIMIT` after 875,035 conflicts.  Peak RSS was about 174MB with 0 swap.
This produced no mathematical conclusion, but it confirms that `E_1` is
lightweight enough for a wider portfolio.

The active `E_1` export now uses the stronger safe normalization:

- triple matching through `{0,1,2}`;
- off-triple block `D:0,1,3,5,7`;
- redundant D lower-count constraints for subset sizes 0, 1, 2, and 3.

The regenerated stronger file has:

```text
variables: 74613
constraints: 27906
file size: 9.2M
sha256: 94126fe65c3bd94d2a036eddbabb18e55d58f42cd6795abb2ba84662a40cc21e
```

A 10-minute six-way portfolio on this stronger `E_1` instance also reached
`TIMELIMIT` on every branch.  The best branch was `lubybase15`, with 1,079,995
conflicts and peak RSS about 129MB.

A follow-up 2-hour ten-way portfolio also reached `TIMELIMIT` on every branch.
The best branch was again `lubybase15`, with 5,250,782 conflicts and peak RSS
about 231MB.  Memory remained healthy and swap stayed at 0B.  This points away
from longer identical OPB/RoundingSat runs as the immediate next step; the next
main experiment should be a CNF/CDCL encoding of `E_1`.

The CNF/CDCL route is now operational.  The generated pairwise DIMACS instance
has:

```text
variables: 74613
clauses: 3607768
file size: 57M
sha256: 690112c309acc78a7dd58fee800f5f8097f479bab6177b6179980f6a51b4269f
```

This CNF is the baseline pairwise exact-one encoding plus symmetry unit
clauses.  It does not include the OPB D lower-count equalities; that mismatch
was caught in the later Pro-model audit and the documentation has been
corrected.

CaDiCaL was prepared locally without sudo by downloading and extracting the
Ubuntu package into `artifacts/solvers/cadical_pkg`.  A 10-minute CaDiCaL smoke
run reached `timeout` after 2,980,586 conflicts with peak RSS about 697MB.
A 2-hour CaDiCaL baseline also reached timeout:

```text
conflicts: 34,615,957
decisions: 101,541,116
propagations: 22,753,179,630
peak RSS: 930,980 KB
swap: 0
```

No SAT witness or UNSAT certificate has been found.  A 9-branch, 1-hour
CaDiCaL portfolio completed with timeout on every branch.  The best branch by
conflicts was `preprocess1_optimize1` with 3,942,942 conflicts in one hour;
memory stayed safe, with each branch below about 762MB RSS and swap at 0.

Kissat 4.0.4 was then installed from the official Linux amd64 release binary.
On the same `E_1` CNF, a 10-minute smoke run also timed out, but reached
4,860,049 conflicts with about 222MB reported RSS.  A follow-up 2-hour Kissat
run also timed out:

```text
conflicts: 57,070,395
decisions: 880,874,492
propagations: 48,143,111,456
peak RSS: 229,012 KB
swap: 0
```

Kissat is the best tested solver on this CNF so far, but it still did not
decide `E_1`.  The current best next step is strategic review rather than
another blind rerun: compare encodings, symmetry breaking, redundant
constraints, and whether to move from `E_1` to another staged target.

The next implemented experiment is the residual-orbit split proposed by the
Pro-model audit.  The CNF generator now accepts extra branch units via
`--force-d-block`, covering:

```text
Branch A: D:0,1,3,6,8
Branch B: D:0,1,3,6,9
```

The ladder OPB generator now also supports `--add-g4-counts`, enabling E1
branch OPBs with both D lower-count equalities and G4 equalities.

The two residual-orbit Kissat branch CNFs both reached timeout:

```text
Branch A D:0,1,3,6,8: 48,117,911 conflicts, peak RSS 265,716 KB
Branch B D:0,1,3,6,9: 47,834,751 conflicts, peak RSS 250,580 KB
```

No SAT witness or UNSAT certificate was produced, so the Pro-recommended
Experiment 2 was run next: the G4-strengthened branch OPBs with RoundingSat
`--lp=0`.

The G4-strengthened branch OPBs also reached timeout:

```text
Branch A D:0,1,3,6,8: TIMELIMIT, 4,760,000 conflicts, peak RSS 397,556 KB
Branch B D:0,1,3,6,9: TIMELIMIT, 4,658,000 conflicts, peak RSS 411,556 KB
```

No SAT witness or UNSAT certificate was produced.  Memory use stayed low, so
this is a search-complexity result rather than a hardware/RAM failure.

Experiment 3 has now been launched: `E_2` pairwise CNFs under the same two
residual-orbit D branches.  Each branch has 128,877 variables and 6,449,846
clauses:

```text
Branch A D:0,1,3,6,8 sha256: 13746f89cbaa424bd88654d45d66bb978821e263eaad6d10cb8a08d61596a10e
Branch B D:0,1,3,6,9 sha256: 56080d1ad72bb002bd462bb062494233a7b90a990e1d0a1a864795b95277ad58
```

The active logs are `artifacts/solver_logs/e2_kissat_branch_a_2h.log` and
`artifacts/solver_logs/e2_kissat_branch_b_2h.log`.

Both active `E_2` branch logs reached timeout:

```text
Branch A D:0,1,3,6,8: UNKNOWN / timeout, 49,546,914 conflicts, peak RSS 462,444 KB
Branch B D:0,1,3,6,9: UNKNOWN / timeout, 49,379,546 conflicts, peak RSS 436,164 KB
```

No SAT witness or UNSAT certificate was produced.  The next useful engineering
target is to strengthen the branch-local CNF with selected redundant
cardinality constraints, not to repeat the same unstrengthened `E_1` or `E_2`
runs.  The Pro-model recommendation is to start with D3 <= 9 and G4 <= 8,
using a bounded sequential-counter or totalizer encoding if the generated CNF
size remains manageable.

The sequential-counter CNF strengthening has been implemented for the staged
ladder generator.  For each branch:

```text
E1 + D3/G4 CNF:  8,357,853 variables, 21,071,999 clauses
E2 + D3/G4 CNF: 14,875,917 variables, 37,559,876 clauses
```

The active run is the smaller decisive E1 D3/G4 branch split:

```text
Branch A D:0,1,3,6,8 sha256: 2206e3b78ce1e885c2c5592f34d07d9017d223cbac610673ab8c3ae1de02f9b0
Branch B D:0,1,3,6,9 sha256: f9f3807a7ab9078050b1ab61abbb8536f5c6760277b39fa3a8ed5c30348254fc
```

The active logs are
`artifacts/solver_logs/e1_d3_g4_kissat_branch_a_2h.log` and
`artifacts/solver_logs/e1_d3_g4_kissat_branch_b_2h.log`.

The first D-only OPB has been generated with the triple-matching symmetry break
and redundant D lower-count constraints:

```text
variables: 20349
constraints: 7556
file size: 5.8M
```

A 10-minute RoundingSat `--lp=0` smoke run on this D-only instance reached
`s TIMELIMIT` after about 1.486M conflicts with peak RSS about 220MB.  This did
not prove anything mathematically, but it confirms the smaller target is
lightweight enough for stronger symmetry-breaking and encoding experiments.

## One-colour exact-cover formulation

Let \(V\) have 21 points.  The Boolean variables are:

- \(d_S\), for \(S\in {V\choose 5}\);
- \(x_{j,U}\), for \(j=1,\ldots,11\) and \(U\in {V\choose 6}\).

The constraints are:

```text
For each 4-set T:
    sum_{S superset T, |S|=5} d_S = 1

For each j and each 5-set S:
    d_S + sum_{v notin S} x_{j,S union {v}} = 1

For each 6-set U:
    sum_j x_{j,U} + sum_{S subset U, |S|=5} d_S = 1
```

These are exact-one constraints.  In the generated OPB instance, each selected
row is a candidate \(D\)-block or candidate \(G_j\)-block; each column is one of
the exact-one constraints above.

## Instance size

The target parameters are:

```text
v = 21
t = 4
extension_count = 11
```

The exact-cover matrix has:

```text
D rows: 20349
x rows: 596904
total rows: 617253

t-subset columns: 5985
(j,S) columns: 223839
U-shadow columns: 54264
total columns: 284088

D row incidences: 651168
x row incidences: 4178328
total incidences: 4829496

constraint lengths: (17, 17, 17)
```

The full OPB export generated locally is about 56MB.  The file is small enough
to move easily, but a solver may use many GB of memory because propagation,
branching, conflict learning, cutting planes, and proof logging are much larger
than the plain input file.

## Why the computation is large

The size comes from the combinatorics, not from implementation overhead:

```text
number of 5-sets = C(21,5) = 20349
number of 6-sets = C(21,6) = 54264
number of extension layers = 11
```

Thus the \(x\)-side alone has

```text
11 * C(21,6) = 596904
```

Boolean candidates.  The formulation is already the one-colour shadow, so it
is much smaller than a direct seventeen-colour global model.

## Machine assessment

Current Mac environment:

- 8 logical ARM64 processors;
- 16GB memory;
- about 16GiB free disk at the time of inspection.

This machine is suitable for development, tests, statistics, small examples,
and OPB export.  It is not a good target for long raw SAT/PB runs.

Windows PC:

- Intel i5-13400;
- 32GB memory.

This PC is a reasonable first execution target for the one-colour OPB instance,
especially under WSL2 Ubuntu.  It is not large enough to treat the full
seventeen-colour problem as a first attempt.

## Expected runtime

Approximate expectations on the 32GB i5-13400 PC:

```text
Smoke tests: seconds
Full OPB export: tens of seconds to a few minutes
Solver read/preprocess: minutes
Shallow contradiction, if present: 10 minutes to 2 hours
Hard but tractable raw one-colour run: 2 to 12 hours
Deep UNSAT proof: 1 to 3 days or longer
Heavy swap: stop the run
```

Recommended first budget:

```text
time limit: 2-6 hours
memory soft limit: 24-28GB
```

If there is no useful progress within that range, switch to smaller derived
subsystems instead of letting the raw run consume days.

Observed on the Windows PC with RoundingSat:

```text
raw 2-hour run: UNKNOWN / timeout
peak RSS: about 1.6GB
LP total time: 2747.5s
short benchmark: --lp=0 gives far more conflicts/decisions per minute
```

Those observations led to the strengthened OPB and `--lp=0` portfolio runs.
The strengthened portfolio also timed out, so the next solver experiments
should move to smaller D-only and fixed-D conditional targets before returning
to the full one-colour shadow.
The revised plan is more specific: move first through the `E_m` ladder, using
D-only and fixed-D runs for diagnostics and symmetry-breaking evidence.

## Current repository status

Implemented:

- parameter model and exact-cover statistics;
- staged \(E_m\) extension-ladder stats and OPB export;
- D-only OPB export and D-only verifier;
- fixed-\(D_a\) conditional one-colour stats and OPB export;
- sparse exact-cover row generator;
- OPB export;
- candidate verifier for one-colour solutions;
- toy instance tests;
- LaTeX working note;
- Pro-model next-round prompt;
- WSL/PC execution notes.

Verified locally:

- unit tests pass;
- smoke script passes;
- full OPB export succeeds;
- LaTeX note compilation was not re-verified on this Windows/WSL setup because
  `pdflatex` is not installed.

Not done:

- no SAT witness or UNSAT certificate from the strengthened one-colour runs;
- no SAT witness;
- no UNSAT certificate;
- no public claim of solution.
- no combined 17-colour first-layer CNF yet; this is documented as a later,
  much larger target.
