# Counterexamples and Assumption Boundaries

These cases are retained even though they narrow the positive theorem target.

1. **Non-unit threshold blocks a single flip.**  In a homogeneous node of size
   eight with one flip, purity is \(7/8\).  At \(\tau=3/4\) the root stops;
   there is no cascade.  A tau-one path theorem cannot be extrapolated to all
   thresholds.
2. **Clustered contamination can stop early.**  At \(\tau=1\), if every leaf
   of a subtree is flipped to the same alternative class, that subtree is pure
   and terminal.  Counting only the union of marked root-to-leaf paths
   overcounts the actual activated frontier unless fully marked subtrees are
   removed from the mixed-node set.
3. **The m-path sum is not a tight formula.**  On a complete 16-leaf tree with
   \(m=3\), the candidate maximum is nine activated nodes, while the naive
   \(m\log_2n=12\) path sum double-counts shared ancestors.  The exact count
   must be by occupied mixed prefixes.
4. **Alternative labels matter away from the maximization.**  A fully marked
   subtree is pure under one shared alternative label but can remain impure if
   its flipped leaves carry multiple alternative labels.  C-T2 is explicitly a
   same-target maximum statement; multiclass patterns require separate bounds.
5. **Minimum support changes the formula.**  If a forced-leaf rule stops at
   support two or larger, a path may terminate before its contaminated leaf.
   C-T1--C-T3 require no forced minimum support beyond actual leaves.
