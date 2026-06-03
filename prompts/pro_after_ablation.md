# Prompt for Pro-model strategy review after E1 ablations

Do not browse the web.  Work only from the reductions and computational data
below.  The goal is to decide the next computational step, not to write a
forum announcement.

We are studying the k=16 case of Erdos problem 835 through a necessary
first-layer obstruction.  The decisive one-colour shadow has variables

```text
d_S            for S in C(21,5)
x_{j,U}        for j=1..11 and U in C(21,6)
```

with exact-one constraints

```text
sum_{S superset T} d_S = 1
d_S + sum_{v notin S} x_{j,S union {v}} = 1
sum_j x_{j,U} + sum_{S subset U, |S|=5} d_S = 1
```

An UNSAT certificate for the full one-colour shadow would rule out the k=16
first-layer object.  We are not there yet.  We have been using staged necessary
instances E_m.  If any decisive E_m is UNSAT with checked certificates for both
residual branches, then the full first-layer object is impossible.  A timeout
is only a timeout.

Current branch split:

```text
Common symmetry:
  triple matching through {0,1,2}
  off-triple block D:{0,1,3,5,7}

Branch A:
  force D:{0,1,3,6,8}

Branch B:
  force D:{0,1,3,6,9}
```

Experiment table on the 32GB i5-13400 PC:

```text
1. E1 baseline branch CNF
   per branch: 74,613 variables, 3,607,769 clauses
   Kissat 2h:
     A timeout, 48,117,911 conflicts, RSS 265,716 KB
     B timeout, 47,834,751 conflicts, RSS 250,580 KB

2. E1 G4 OPB branch model
   per branch: 74,613 variables, 33,892 OPB constraints
   RoundingSat --lp=0 1h:
     A timeout, 4,760,000 conflicts, RSS 397,556 KB
     B timeout, 4,658,000 conflicts, RSS 411,556 KB

3. E2 baseline branch CNF
   per branch: 128,877 variables, 6,449,846 clauses
   Kissat 2h:
     A timeout, 49,546,914 conflicts, RSS 462,444 KB
     B timeout, 49,379,546 conflicts, RSS 436,164 KB

4. E1 D3+G4 branch CNF
   constraints encoded with sequential-counter upper bounds:
     D3 <= 9 for each 3-set
     G4 <= 8 for each 4-set
   per branch: 8,357,853 variables, 21,071,999 clauses
   Kissat 2h:
     A timeout, 8,661,819 conflicts, RSS 2,523,444 KB
     B timeout, 9,229,109 conflicts, RSS 2,579,572 KB

5. E1 D3-only branch CNF
   per branch: 1,894,053 variables, 7,426,199 clauses
   Kissat 2h:
     A timeout, 14,632,438 conflicts, RSS 705,784 KB
     B timeout, 15,048,223 conflicts, RSS 695,268 KB

6. E1 G4-only branch CNF
   per branch: 6,538,413 variables, 17,253,569 clauses
   Kissat 2h:
     A timeout, 6,745,483 conflicts, RSS 2,041,276 KB
     B timeout, 6,984,877 conflicts, RSS 2,030,716 KB
```

No SAT witness and no UNSAT certificate were produced.  Mathematical status is
unchanged.

Current engineering interpretation:

```text
- D3-only is the cheapest strengthened CNF.
- G4-only and D3+G4 use much more memory and reduce conflict throughput.
- Baseline E2 is not harder than E1 by memory, but it also timed out.
- Blindly escalating to E2 D3+G4 may be wasteful.
```

Please audit this next-step decision:

1. Should we run E2 D3-only branch CNFs next, because D3-only was the best
   strengthened E1 variant?
2. Or should we stop local solver runs and derive a stronger branch split or
   a different redundant constraint first?
3. Is there a safe residual-orbit split after Branch A/B that is easy to
   justify and likely stronger than adding cardinality encodings?
4. Are there CNF redundancies better than D3 <= 9 and G4 <= 8 for Kissat, with
   manageable size on a 32GB machine?
5. Should OPB/RoundingSat still be used, or have the results made CDCL CNF the
   better route for now?

Output a concrete next plan with no more than three experiments.  For each
experiment, specify expected size, solver, time limit, and what outcome would
change the strategy.  Be strict about not treating timeouts as mathematical
evidence.
