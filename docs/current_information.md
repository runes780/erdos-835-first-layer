# Current information summary

Date: 2026-05-31

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

The one-colour exact-cover system is the current computational target.  If it
is UNSAT, then the \(k=16\) first-layer object cannot exist.  If it is SAT, the
one-colour shadow alone is not enough; the next task is to understand whether
seventeen compatible colours can be assembled.

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

## Current repository status

Implemented:

- parameter model and exact-cover statistics;
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
- LaTeX note compiles.

Not done:

- no solver result yet;
- no SAT witness;
- no UNSAT certificate;
- no public claim of solution.

