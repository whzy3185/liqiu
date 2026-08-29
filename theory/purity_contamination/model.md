# Fixed-Geometry Purity-Pruning Model

## Object and convention

Let (T=(V,E)) be a finite rooted full binary partition tree.  Its leaves are
in bijection with sample indices ([n]).  Each node (v) has support
(S_v\subseteq[n]), the leaves below it.  Geometry is fixed: the tree is
constructed without labels and is unchanged under every label contamination in
this theory.

For labels (y\in\mathcal C^n), let

\[
N_c(v;y)=|\{i\in S_v:y_i=c\}|,\qquad
p_y(v)=\max_{c\in\mathcal C}\frac{N_c(v;y)}{|S_v|}.
\]

For threshold \(\tau\in[1/2,1]\), pruning is top-down: a node is terminal if
it is a leaf or its purity satisfies \(p_y(v)\ge\tau\); otherwise it splits
into its two children.  Thus
\(F_\tau(T,y)\) is the terminal frontier and
\(B_\tau(T,y)=|F_\tau(T,y)|\) is the terminal-ball count.  Equality is a
stop, not a split.  A minimum-support variant forces a node terminal below the
specified support; it is excluded from the initial theorems.

For Hamming label contamination \(d_H(y,y')\le m\), define

\[
A_B(T,y,y';\tau)=B_\tau(T,y')-B_\tau(T,y).
\]

We also distinguish the number of activated internal nodes
\(I_\tau(T,y')\), namely nodes visited and split under the contaminated labels,
from absolute structural sensitivity \(|A_B|\).  In a full binary expansion
from a one-ball clean frontier, \(B=I+1\), so these coincide numerically for
the homogeneous \(\tau=1\) setting.

## Scope boundary

This is **frozen geometry sensitivity**.  It makes no claim about adaptive
KMeans topology, a classifier decision rule, risk, or a real-data benchmark.
Those mechanisms may amplify, offset, or mask the pruning effect and cannot be
deduced from this model.

## Immediate threshold identity

For a binary homogeneous node of support \(s\), flipping \(k\le s/2\) labels
to the other class gives \(p=1-k/s\).  With the stop-on-equality convention it
splits exactly when \(1-k/s<\tau\), equivalently
\(k>(1-\tau)s\).  This is a basic local identity, not a target theorem.
