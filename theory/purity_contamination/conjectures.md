# Contamination Amplification Conjectures

All statements below are `CONJECTURE` until promoted in `theorems.md`.  They
are intentionally restricted to frozen geometry and top-down pruning.

## C-T0 — local threshold identity

For a homogeneous binary node of support \(s\), \(k\le s/2\) same-target
flips give purity \(1-k/s\).  Under stop-on-equality, the node splits iff
\(k>(1-\tau)s\).  This is a tool, not a main result.

## C-T1 — single-flip exact frontier

At \(\tau=1\), homogeneous labels, and one flipped leaf \(x\), the terminal
frontier has \(h_x+1\) nodes, where \(h_x\) is the root-to-leaf depth.  Hence
the ball-count amplification is exactly \(h_x\).

## C-T2 — complete balanced-tree maximum

For a complete binary tree with \(n=2^h\) leaves, homogeneous clean labels,
\(\tau=1\), and \(1\le m\le n/2\) leaves flipped to the same alternative
class, the maximum amplification is

\[
\max_{|M|=m}A_B=\sum_{d=0}^{h-1}\min\{2^d,m\}.
\]

Writing \(r=\lceil\log_2m\rceil\), this is
\(2^r-1+m(h-r)\), hence
\(\Theta(m\log_2(n/m)+m)\).  The construction must make marked leaves
occupy all shallow prefixes and distinct deep prefixes; clustered marks are
not generally extremal.

## C-T3 — general-tree characterization

At \(\tau=1\) under homogeneous clean labels and one alternative target
class, the activated internal nodes are exactly the nodes whose support meets
both the marked leaf set \(M\) and its complement.  Thus

\[
A_B=|\{v\text{ internal}:S_v\cap M\ne\varnothing,
 S_v\setminus M\ne\varnothing\}|.
\]

In particular \(A_B\le\sum_{x\in M}\operatorname{depth}(x)\le mH\).

## C-T4 — non-unit threshold warning

There is no unconditional single-flip cascade for \(\tau<1\).  At a
homogeneous node of size \(s\), one flip cannot activate it whenever
\(\tau\le1-1/s\).  A useful theorem here would require a budgeted
activation-cascade characterization; no closed-form claim is retained yet.

## C-T5 — multi-scale incompatibility

The single-node fidelity/noise threshold condition is already known in the
repository.  A new recursive fidelity--robustness--compression theorem is
retained only if it implies more than C-T3's standard marked-ancestor count.
No such statement is currently established.
