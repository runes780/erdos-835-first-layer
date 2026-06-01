# Prompt for the next Pro-model round

Do not browse the web.  Work only from the reductions and computational data
below.

We are studying Erdős problem 835, first serious remaining case \(k=16\).  The
current route is:

```text
k=16 coloring
  -> first-layer object on 21 points over F_17
  -> one-colour exact-cover shadow
  -> staged extension ladder E_m
```

The decisive one-colour shadow uses variables

\[
d_S\quad(S\in {V\choose 5}),\qquad
x_{j,U}\quad(j=1,\ldots,11,\ U\in {V\choose 6}),
\]

with constraints

\[
\sum_{S\supset T} d_S=1
\quad(T\in {V\choose 4}),
\]

\[
d_S+\sum_{v\in V\setminus S}x_{j,S\cup\{v\}}=1
\quad(j=1,\ldots,11,\ S\in {V\choose 5}),
\]

\[
\sum_{j=1}^{11}x_{j,U}+
\sum_{\substack{S\subset U\\ |S|=5}}d_S=1
\quad(U\in {V\choose 6}).
\]

Full one-colour size:

```text
Boolean variables / rows: 617,253
exact-cover columns: 284,088
incidences: 4,829,496
all exact-one lengths: 17
```

An UNSAT certificate for the full one-colour shadow would rule out the \(k=16\)
first-layer object.

We then introduced a staged necessary ladder.  \(E_1\) keeps \(D_a\) plus one
point-extension family.  If \(E_1\) is UNSAT, then the full first-layer object
is impossible.  If \(E_1\) is SAT or unknown, it only means this weaker stage is
consistent or undecided.

Current `E_1` CNF:

```text
variables: 74,613
clauses: 3,607,768
encoding: pairwise exact-one DIMACS
symmetry:
  - triple matching through {0,1,2}
  - off-triple block D:{0,1,3,5,7}
  - redundant D lower-count constraints for subset sizes 0,1,2,3
CNF sha256: 690112c309acc78a7dd58fee800f5f8097f479bab6177b6179980f6a51b4269f
```

Solver evidence so far:

```text
RoundingSat OPB E_1 5m:
  timeout, 755k-875k conflicts range depending on strengthening

RoundingSat stronger E_1 10-way 2h portfolio:
  all timeout
  best branch: 5,250,782 conflicts
  peak RSS about 231MB

CaDiCaL 10m CNF:
  timeout
  conflicts: 2,980,586
  RSS: 696,880 KB

CaDiCaL default 2h CNF:
  timeout
  conflicts: 34,615,957
  decisions: 101,541,116
  propagations: 22,753,179,630
  peak RSS: 930,980 KB

CaDiCaL 9-branch 1h parameter portfolio:
  all timeout
  best branch: -P1 -O1
  best conflicts: 3,942,942
  per-branch RSS below about 762MB

Kissat 4.0.4 10m CNF:
  timeout
  conflicts: 4,860,049
  decisions: 75,808,300
  propagations: 4,219,292,529
  RSS: 222 MB

Kissat 4.0.4 2h CNF:
  timeout
  conflicts: 57,070,395
  decisions: 880,874,492
  propagations: 48,143,111,456
  peak RSS: 229,012 KB
  swap: 0
```

No SAT witness and no UNSAT certificate have been found.

Task:

Give a strategic recommendation for the next round.  Do not re-explain the
original problem.  Focus on the `E_1`/one-colour computational attack.

Please answer these directly:

1. Is `E_1` still the right target, or should we move to `E_2`, D-only,
   fixed-\(D_a\), or the full one-colour shadow?
2. Is pairwise DIMACS exact-one still a reasonable encoding, or should we try
   another encoding such as sequential counters, cardinality networks,
   commander variables, XOR/rank constraints, or exact-cover/DLX-style search?
3. What additional safe symmetry breaking is mathematically justified beyond
   the current triple matching plus off-triple block?
4. What redundant constraints are likely to help CDCL propagation without
   changing satisfiability?
5. Would you spend more CPU on Kissat, run a Kissat portfolio, try another
   solver, or stop solver runs until the formulation is strengthened?
6. Give the next concrete 3 experiments, with expected file sizes, time limits,
   and what result would change the plan.

Be strict: a timeout is not evidence of satisfiability or unsatisfiability.
Prefer a smaller certifiable obstruction or stronger symmetry/redundancy over
blindly increasing runtime.
