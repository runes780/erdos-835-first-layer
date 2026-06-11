# Full Pro-Model Information Package: Erdos 835, k=16 First-Layer Strategy Review

Do not browse the web.  Work only from the mathematical reductions, repository
state, and computational evidence below.  The purpose of this prompt is not to
write a public announcement; it is to audit the current strategy and recommend
the next technically defensible step.

## 1. Executive Context

We are studying the k=16 case of Erdos problem 835.  The direct 17-colour
Johnson-graph formulation is far too large, so the current attack uses a
necessary first-layer obstruction.

Current mathematical status:

```text
Complete proof excluding k=16: no
SAT witness for the relevant shadow: no
UNSAT certificate for any decisive model: no
Mathematical conclusion changed by solver runs: no
```

The useful achievement so far is a substantial reduction:

```text
k=16 colouring
  -> first-layer object on 21 points over F_17
  -> one-colour exact-cover shadow
  -> staged E_m necessary ladder
```

An UNSAT certificate for a decisive stage, with the branch coverage checked,
would rule out the k=16 first-layer object.  A timeout is not mathematical
evidence.

## 2. Mathematical Reduction Summary

Let V be a 21-point set.  The first-layer object consists of:

```text
D: C(V,5) -> F_17
g_1, ..., g_11: C(V,6) -> F_17
```

where D is an LS(4,5,21) colouring, and for every j and every 5-set S:

```text
{ D(S) } union { g_j(S union {v}) : v in V \ S } = F_17.
```

For every 6-set U:

```text
{ g_1(U), ..., g_11(U) }
  = F_17 \ { D(U \ {u}) : u in U }.
```

The six D-facet colours are distinct because each colour class of D is an
S(4,5,21): two equal-colour 5-facets of the same 6-set would share a 4-set,
contradicting uniqueness through 4-sets.

This first-layer object is a necessary condition for a k=16 solution.  It is
not known to be sufficient.

## 3. Fixed-Colour One-Colour Shadow

Fix one colour a in F_17.  Define:

```text
D_a = { S in C(V,5) : D(S) = a }
G_{j,a} = { U in C(V,6) : g_j(U) = a }
```

Then D_a must be an S(4,5,21).  For each j:

```text
U in G_{j,a} implies U contains no D_a block.

For every 5-set S:
  if S in D_a, then S is covered by no G_{j,a} block;
  if S not in D_a, then S is covered by exactly one G_{j,a} block.

The eleven G_{j,a} partition the allowed 6-sets, where "allowed" means
containing no D_a block.
```

Parameters:

```text
|D_a| = C(21,4) / C(5,4) = 1197
total 6-sets = C(21,6) = 54264
forbidden 6-sets = 1197 * 16 = 19152
allowed 6-sets = 35112
|G_{j,a}| = 35112 / 11 = 3192
```

Each G_{j,a} is a relative 4-(21,6,8) design with:

```text
lambda_t(G) for t=0..4:
  3192, 912, 228, 48, 8
```

The t=5 value is not constant:

```text
0 if the 5-set is in D_a
1 otherwise
```

No contradiction has been found from fixed-colour parameters, fixed-block
neighbourhoods, fixed-4-set neighbourhoods, or intersection numbers.

## 4. Decisive One-Colour Exact-Cover Core

The full one-colour shadow uses Boolean variables:

```text
d_S      for S in C(V,5)
x_{j,U}  for j=1..11 and U in C(V,6)
```

with exact-one constraints:

```text
For every 4-set T:
  sum_{S superset T, |S|=5} d_S = 1

For every j and every 5-set S:
  d_S + sum_{v in V \ S} x_{j, S union {v}} = 1

For every 6-set U:
  sum_{j=1..11} x_{j,U}
  + sum_{S subset U, |S|=5} d_S = 1
```

Size:

```text
d variables: C(21,5) = 20,349
x variables: 11 * C(21,6) = 596,904
total Boolean variables / exact-cover rows: 617,253

4-set columns: C(21,4) = 5,985
(j,S) columns: 11 * C(21,5) = 223,839
6-set columns: C(21,6) = 54,264
total exact-cover columns: 284,088

total incidences: 4,829,496
all exact-one lengths: 17
```

An UNSAT certificate for this full one-colour shadow would rule out the k=16
first-layer object.  A SAT solution would only be a one-colour shadow, not a
full k=16 colouring.

## 5. Staged E_m Ladder

To avoid immediately solving all 11 extension families, we introduced a
necessary staged ladder E_m:

```text
E_m keeps D_a and m extension families G_1, ..., G_m.
```

If E_m is UNSAT for some m, then the full one-colour shadow is impossible.
If E_m is SAT, it only means the weaker stage is consistent.  If E_m times
out, no mathematical conclusion follows.

The experiments below use E1 and E2 with residual branch splitting.

## 6. Symmetry and Branch Splitting

The current safe symmetry normalisation is:

```text
triple matching through {0,1,2}
off-triple block D:{0,1,3,5,7}
```

After this normalisation, we split on the D-block through:

```text
Q = {0,1,3,6}
```

The fifth point cannot be 2, 4, 5, or 7.  The remaining possibilities fall into
two residual orbits under the stabiliser of the current forced structure and Q:

```text
Branch A:
  force D:{0,1,3,6,8}

Branch B:
  force D:{0,1,3,6,9}
```

Both branches must be covered before claiming a global result.

Please audit whether this branch split is correct, complete, and worth
extending.  If there is a stronger safe residual-orbit split after A/B, we need
it explicitly stated and justified.

## 7. Encodings and Redundant Constraints Tested

Base CNF:

```text
pairwise exact-one encoding for length-17 exact-one constraints
branch symmetry unit clauses
cross-family disjointness clauses for E_m where relevant
```

Redundant constraints tested:

```text
D3 <= 9:
  For each 3-set A, sum_{S superset A, |S|=5} d_S <= 9

G4 <= 8:
  For each extension family j and each 4-set T,
  sum_{U superset T, |U|=6} x_{j,U} <= 8
```

These were encoded in CNF using sequential-counter upper-bound encodings.

OPB/PB runs:

```text
RoundingSat --lp=0 was tested on strengthened E1 OPB variants.
```

The observed pattern is that D3-only is relatively cheap, while G4-only and
D3+G4 increase memory and propagation cost substantially.

## 8. Hardware and Solver Environment

Primary run machine:

```text
Windows PC
CPU: Intel i5-13400
RAM: 32GB
Execution: WSL2 Ubuntu
Main SAT solver: Kissat
PB solver tested: RoundingSat --lp=0
```

Practical resource observation:

```text
No run below exhausted memory.
No swap pressure in the completed branch runs.
Large G4 CNF variants remain memory-safe but become much more expensive per
conflict.
```

The machine is suitable for development and moderate branch probes.  It is not
large enough to justify blind escalation to the full 17-colour problem or huge
unstructured proof-producing runs.

## 9. Completed Solver Evidence

All entries below are time-limited exploratory runs.  No SAT witness and no
UNSAT certificate have been produced.

```text
1. E1 baseline branch CNF
   per branch: 74,613 variables, 3,607,769 clauses
   solver: Kissat
   time limit: 2h per branch

   Branch A:
     result: UNKNOWN / timeout
     conflicts: 48,117,911
     decisions: 839,688,559
     propagations: 40,541,872,067
     peak RSS: 265,716 KB

   Branch B:
     result: UNKNOWN / timeout
     conflicts: 47,834,751
     decisions: 826,186,962
     propagations: 39,861,209,252
     peak RSS: 250,580 KB

2. E1 G4 OPB branch model
   per branch: 74,613 variables, 33,892 OPB constraints
   solver: RoundingSat --lp=0
   time limit: 1h per branch

   Branch A:
     result: UNKNOWN / timeout
     conflicts: 4,760,000
     peak RSS: 397,556 KB

   Branch B:
     result: UNKNOWN / timeout
     conflicts: 4,658,000
     peak RSS: 411,556 KB

3. E2 baseline branch CNF
   per branch: 128,877 variables, 6,449,846 clauses
   solver: Kissat
   time limit: 2h per branch

   Branch A:
     result: UNKNOWN / timeout
     conflicts: 49,546,914
     decisions: 861,193,401
     propagations: 52,637,830,321
     peak RSS: 462,444 KB

   Branch B:
     result: UNKNOWN / timeout
     conflicts: 49,379,546
     decisions: 875,123,339
     propagations: 52,847,136,458
     peak RSS: 436,164 KB

4. E1 D3+G4 branch CNF
   per branch: 8,357,853 variables, 21,071,999 clauses
   solver: Kissat
   time limit: 2h per branch

   Branch A:
     result: UNKNOWN / timeout
     conflicts: 8,661,819
     decisions: 188,431,927
     propagations: 35,270,234,849
     peak RSS: 2,523,444 KB

   Branch B:
     result: UNKNOWN / timeout
     conflicts: 9,229,109
     decisions: 204,214,127
     propagations: 34,332,244,642
     peak RSS: 2,579,572 KB

5. E1 D3-only branch CNF
   per branch: 1,894,053 variables, 7,426,199 clauses
   solver: Kissat
   time limit: 2h per branch

   Branch A:
     result: UNKNOWN / timeout
     conflicts: 14,632,438
     decisions: 226,973,196
     propagations: 34,916,178,228
     peak RSS: 705,784 KB

   Branch B:
     result: UNKNOWN / timeout
     conflicts: 15,048,223
     decisions: 240,088,533
     propagations: 34,810,059,155
     peak RSS: 695,268 KB

6. E1 G4-only branch CNF
   per branch: 6,538,413 variables, 17,253,569 clauses
   solver: Kissat
   time limit: 2h per branch

   Branch A:
     result: UNKNOWN / timeout
     conflicts: 6,745,483
     decisions: 142,181,388
     propagations: 25,364,158,886
     peak RSS: 2,041,276 KB

   Branch B:
     result: UNKNOWN / timeout
     conflicts: 6,984,877
     decisions: 144,429,852
     propagations: 25,165,348,806
     peak RSS: 2,030,716 KB

7. E2 D3-only branch CNF
   per branch: 1,948,317 variables, 10,268,276 clauses
   solver: Kissat
   time limit: 2h per branch

   Branch A:
     result: UNKNOWN / timeout
     conflicts: 19,782,418
     decisions: 336,235,411
     propagations: 51,087,948,652
     peak RSS: 832,744 KB

   Branch B:
     result: UNKNOWN / timeout
     conflicts: 19,235,813
     decisions: 327,144,169
     propagations: 50,588,260,574
     peak RSS: 857,116 KB
```

## 10. Current Engineering Interpretation

Our current read is:

```text
- The present E1/E2 pairwise branch CNFs are not decisive in 2h.
- D3-only is the cheapest useful strengthened CNF variant so far.
- G4-only and D3+G4 consume much more memory and lower conflict throughput.
- E2 D3-only is memory-safe but still times out.
- Blindly escalating to E2 G4-only or E2 D3+G4 is probably not the best next
  use of the machine.
- More raw runtime on unchanged instances is not a good strategy.
```

Please challenge this interpretation if it is wrong.

## 11. Repository State

Important implemented components:

```text
src/extension_ladder_cnf.py
  E_m CNF generator with D3/G4 sequential-counter upper-bound options.

scripts/export_problem835_e1_branch_cnfs.sh
scripts/run_kissat_e1_branch_2h.sh

scripts/export_problem835_e2_branch_cnfs.sh
scripts/run_kissat_e2_branch_2h.sh

scripts/export_problem835_e1_d3_g4_branch_cnfs.sh
scripts/run_kissat_e1_d3_g4_branch_2h.sh

scripts/export_problem835_e1_ablation_branch_cnfs.sh
scripts/run_kissat_e1_ablation_branch_2h.sh

scripts/export_problem835_e2_d3_branch_cnfs.sh
scripts/run_kissat_e2_d3_branch_2h.sh

docs/progress_log.md
docs/current_information.md
docs/solver_runbook.md
prompts/pro_after_ablation.md
```

Verified locally:

```text
unit tests pass
smoke script passes
CNF/OPB exports succeed
solver logs are preserved
```

Not done:

```text
no SAT witness
no UNSAT certificate
no checked proof
no public mathematical claim
no full 17-colour formulation attempt
```

## 12. What We Need From You

Please produce a rigorous strategy audit with the following deliverables.

### A. Mathematical audit

1. Check whether the one-colour shadow really is a decisive necessary target:
   does UNSAT of the full one-colour shadow rule out the k=16 first-layer
   object?
2. Check whether the E_m ladder implication is valid:
   does UNSAT of E_m for any m rule out the full one-colour shadow?
3. Check whether the residual branch split A/B is valid and complete.
4. Identify any hidden assumption in the D3 <= 9 or G4 <= 8 redundant
   constraints.

### B. Solver-strategy audit

1. Based on the experiment table, should we stop raw local SAT runs for now?
2. Is there a better next CNF/PB model than E2 D3-only?
3. Is there a safe next residual-orbit branch split that is stronger than
   adding G4 or D3+G4?
4. Should we continue with Kissat, return to RoundingSat/OPB, or use a
   different solver style?
5. Is pairwise exact-one still appropriate, or should we test another encoding
   for some subset of constraints?

### C. Concrete next plan

Give at most three next experiments.  For each experiment, specify:

```text
goal
mathematical justification
expected instance size if possible
solver and encoding
time limit
memory expectation
success criterion
failure/timeout interpretation
what result would change the strategy
```

Do not propose "run the same thing longer" unless you can explain exactly why
the existing conflict/progression data justify it.

### D. Proof/certificate guidance

If any experiment returns UNSAT:

```text
What proof format should be generated?
Which checker should be used?
What files/hashes must be preserved?
What exact mathematical statement can be claimed?
```

If any experiment returns SAT:

```text
What witness should be extracted?
What independent verifier should be run?
What mathematical statement, if any, can be claimed?
```

## 13. Output Format Requested

Please answer in the following structure:

```text
1. Verdict
2. Mathematical audit
3. Interpretation of the computational evidence
4. Recommended next experiments, maximum three
5. Things to stop doing
6. Certificate/witness handling
7. Short instruction block we can paste back into Codex
```

Be strict.  Do not treat timeouts as evidence of nonexistence.  Prefer a
smaller auditable next step over a larger impressive-looking run.
