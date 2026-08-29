# Fixed-Tree Purity Contamination Theorems

All results assume the model in `model.md`: a fixed full binary geometry tree,
top-down stop-on-equality purity pruning, and no forced minimum support.

## Theorem 1 — exact monochromatic-frontier characterization

Let clean labels be homogeneous with class zero, let \(\tau=1\), and let a set
\(M\) of leaves be changed to one common alternative class.  Define

\[
\mathcal I(M)=\{v\text{ internal}:S_v\cap M\ne\varnothing
\text{ and }S_v\setminus M\ne\varnothing\}.
\]

Then the activated internal nodes are exactly \(\mathcal I(M)\), and

\[
B_1(T,y')=1+|\mathcal I(M)|,\qquad A_B(T,y,y';1)=|\mathcal I(M)|.
\]

**Proof.** A non-leaf node expands precisely when it contains both observed
labels. Under the common alternative-label assumption, this is equivalent to
containing at least one marked and one unmarked leaf. That is exactly the
definition of \(\mathcal I(M)\). Each binary expansion replaces one frontier
node by two, increasing frontier size by one. Starting at the root proves both
formulas. \(\square\)

**Necessity.** Multiple alternative labels and forced support stopping each
break the characterization; see `counterexamples.md`.

## Corollary 2 — single-flip amplification

For one marked leaf \(x\), every internal ancestor of \(x\) and no other node
is mixed. If its depth is \(h_x\),

\[
B_1(T,y')=h_x+1,\qquad A_B=h_x.
\]

On a complete tree of \(n=2^h\) leaves this is \(\Theta(\log n)\); on an
unbalanced tree of height \(\Theta(n)\), it is \(\Theta(n)\).

## Theorem 3 — complete-tree maximum

Let \(T_h\) be complete with \(n=2^h\) leaves and \(1\le m\le n/2\). Under
the assumptions of Theorem 1,

\[
\max_{|M|=m} A_B=\sum_{d=0}^{h-1}\min\{2^d,m\}.
\]

Writing \(r=\lceil\log_2m\rceil\), the value is

\[
2^r-1+m(h-r)=\Theta\!\left(m\log_2\frac nm+m\right).
\]

**Proof.** At depth \(d\), every mixed node contains a marked leaf, so there
are at most \(m\) of them, and at most \(2^d\) nodes total. Summing gives the
upper bound. For the lower bound, distribute marks to occupy every shallow
prefix and distinct deep prefixes while leaving an unmarked leaf in each
occupied subtree. This realizes \(\min\{2^d,m\}\) mixed nodes at every depth.
\(\square\)

## Proposition 4 — general-height bound

For any full binary tree of height \(H\),

\[
A_B=|\mathcal I(M)|\le\left|\bigcup_{x\in M}\operatorname{Anc}(x)\right|
\le mH.
\]

The last inequality is tight for one leaf at depth \(H\), and up to overlap
terms for dispersed marks. It is not a new purity-specific bound; it is the
root-to-leaf path-union bound.

## Boundary at \(\tau<1\)

For homogeneous support size \(s\), exact local activation is

\[
k_\tau(s)=\lfloor(1-\tau)s\rfloor+1.
\]

This follows from the local purity identity and strict split inequality. It
does not yield a recursive theorem because continuation depends on how the
budget distributes in children.

## Novelty consequence

Theorem 1 is a monochromatic-frontier restatement and Theorem 3 is the standard
marked-prefix/ancestor-union count in a complete binary tree. Purity pruning
provides interpretation but no additional mathematical difficulty. These facts
do not satisfy the nontrivial recursive-theory gate by themselves.
