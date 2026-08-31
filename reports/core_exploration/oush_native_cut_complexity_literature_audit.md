# Phase 2 — Audit: native nearest-surface GBC cut complexity

Branch: `oush`  
Date audited: 2026-08-31  
Phase-1 artifact: `oush_native_cut_complexity_phase1.md`  
Status: **KILL — nonadditivity is real, but no construction-respecting hardness result or reduction survives**

## Literature audit

The search covered hierarchical prototype selection, nearest-neighbor prototype
subsets, Apollonius/additively weighted Voronoi site updates, and optimal tree
cuts with nonlocal loss. It finds a sharp boundary:

| Source | What it proves / studies | Why it does not prove `NATIVE-GBC-CUT` |
| --- | --- | --- |
| Carrizosa et al. (2007) | Selecting a cardinality-constrained, globally optimal nearest-neighbor prototype subset is NP-hard, even in a binary/metric setting. | Candidates are freely selected prototypes; there is no laminar tree-cut constraint and no requirement that selected sites/radii arise as means of descendant members. |
| Zukhba (2010) | Prototype selection for nearest-neighbor learning-quality criteria is NP-complete. | Again, it chooses a free subset of the learning sample rather than a valid hierarchy terminal cover with member-derived radius. |
| Biniaz et al. (2020) | Minimum consistent nearest-neighbor subsets are NP-hard and admits approximation/coreset analysis. | The selected points are free members of a point set; no hierarchical mean/radius coupling. |
| Karavelas & Yvinec (2002); CGAL Apollonius documentation | Additively weighted Voronoi/Apollonius diagrams support dynamic insertion/deletion and global cell changes. | They update a geometric diagram, not minimize labelled query error over a hierarchy-constrained cut. |
| CART / Chou et al. / Bohanec--Bratko / Lin et al. | Fixed-tree pruning with node-additive error/distortion and leaf cost has classical dynamic programs or pruning paths. | These are the correct comparator when routing is hierarchical/local; they do not establish hardness under global native routing. |

No source located in this bounded audit proves hardness or an exact algorithm for
the conjunction of all five required properties: (i) a valid rooted-tree cut,
(ii) global `||x-c||-r` routing, (iii) finite labelled query error, (iv)
centres and radii determined from actual descendant member multisets, and (v)
majority labels.

The free-prototype results are important **adjacent** evidence, but using them as
a hardness proof would commit the Phase-1 free-prototype fallacy.

## Construction-respecting nonadditivity witness

The following one-dimensional hierarchy uses singleton leaf members, so every
leaf has radius zero and every internal centre/radius is exactly the arithmetic
mean/mean absolute distance required by the clean-room definition.

| Leaf | Member position | Member label |
| --- | ---: | ---: |
| `A1` | -4 | 0 |
| `A2` | -2 | 0 |
| `B1` | -3 | 1 |
| `B2` | -1 | 0 |

`A` is the parent of `A1,A2`, hence `(c_A,r_A,label_A)=(-3,1,0)`.
`B` is the parent of `B1,B2`, hence `(c_B,r_B,label_B)=(-2,1,0)`, with the
declared smallest-label tie rule. Consider query `x=-3` with true label `0`,
conditional on the root already being split into `A,B`.

| Cut | Native prediction at `x` | Error |
| --- | ---: | ---: |
| `C00={A,B}` | 0 | 0 |
| `C10={A1,A2,B}` | 0 | 0 |
| `C01={A,B1,B2}` | 0 | 0 |
| `C11={A1,A2,B1,B2}` | 1 | 1 |

Therefore

\[
L(C11)-L(C10)-L(C01)+L(C00)=1,
\]

which is impossible if the validation loss is a sum of immutable
per-cut-node contributions. The witness verifies the structural difference from
ordinary pruning, but it proves neither NP-hardness nor intractability.

## Why the proof gate fails

1. **No valid reduction.** The nearest-neighbor hardness sources require free
   prototype selection. No polynomial map was found that realizes their arbitrary
   candidate subsets as valid terminal cuts while preserving every ancestor's
   mean centre, mean radius and majority label.
2. **Verifier model remains unresolved.** For unrestricted rational member
   coordinates, comparing native scores involves sums of square roots through
   mean radii. The Phase-1 formulation did not supply a polynomial exact
   certificate verifier under the ordinary Turing model. A one-dimensional
   rational restriction could avoid this issue, but no corresponding
   construction-respecting reduction was obtained.
3. **No direct collision is not positive evidence.** The absence of a located
   matching theorem does not establish novelty or hardness. The only confirmed
   residual fact is the nonadditivity witness above, which the protocol marks as
   insufficient by itself.

## Gate decision

```text
Global native-routing nonadditivity: VERIFIED.
Free-prototype nearest-neighbor hardness: VERIFIED but not transferable.
Hierarchy/member-derived-radius hardness proof: NOT ESTABLISHED.
Exact verifier and valid reduction: NOT ESTABLISHED.
Further proof search, simulation or algorithm design: DO NOT RUN.
Candidate status: KILL_NATIVE_CUT_COMPLEXITY.
```

The nonadditivity witness may be retained as an implementation caveat: CART and
node-additive pruning results cannot be imported automatically for arbitrary
native GBC cuts. It cannot support a standalone complexity or algorithm paper.

## Verified sources

1. Carrizosa, E., Martín-Barragán, B., Plastria, F., & Romero Morales, D.
   (2007). [On the selection of the globally optimal prototype subset for
   nearest-neighbor classification](https://doi.org/10.1287/ijoc.1060.0183).
   *INFORMS Journal on Computing*. The cardinality-constrained free-prototype
   problem is NP-hard.
2. Zukhba, A. V. (2010). [NP-completeness of the problem of prototype selection
   in the nearest neighbor method](https://doi.org/10.1134/S1054661810040097).
   *Pattern Recognition and Image Analysis, 20*(4), 484–494.
3. Biniaz, A., Cabello, S., Carmi, P., De Carufel, J.-L., Maheshwari, A.,
   Mehrabi, S., & Smid, M. (2020). [Coresets for the nearest-neighbor
   rule](https://doi.org/10.4230/LIPIcs.ESA.2020.47). *ESA 2020*.
4. Karavelas, M. I., & Yvinec, M. (2002). [Dynamic additively weighted Voronoi
   diagrams in 2D](https://doi.org/10.1007/3-540-45749-6_52). *ESA 2002*.
5. Lin, J., Storer, J. A., & Cohn, M. (1992). [Optimal pruning for
   tree-structured vector quantization](https://doi.org/10.1016/0306-4573(92)90064-7).
   *Information Processing & Management, 28*(6), 723–733.

## Integrity note

The nonadditivity calculation is an exact finite arithmetic check on a synthetic
four-leaf hierarchy; it is not an empirical result. No user data, external code
or new algorithm was used.
