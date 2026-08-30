# Phase 2 — Literature audit: local split / nonlocal native-routing interference

Branch: `oush`  
Date searched: 2026-08-30  
Phase-1 artifact: `oush_nonlocal_routing_phase1.md`  
Status: **KILL — direct mechanism collision**

## Question and review boundary

The narrow Phase-1 question was whether replacing a construction-local
granular-ball node with its children has an *additional*, harmful influence on
fresh points outside that node's construction-routing region when deployment
uses

\[
  D_B(x)=\lVert x-c_B\rVert-r_B.
\]

This audit does **not** ask whether such a change can be measured in the
repository.  It asks whether that mechanism can support a GB-specific novelty
claim.  The decisive test is whether this score and its site-update behaviour
already have a named, established geometric formulation.

## Search protocol

### Sources searched

- CGAL's maintained Apollonius-graph manual and its cited primary literature.
- Publisher/author records for additively weighted Voronoi (Apollonius) dynamic
  algorithms and predicates.
- Publisher records for original granular-ball classification and recent radius
  / overlap refinement methods.
- Repository's earlier collision audit, used only to locate its existing source
  register; its conclusions were not treated as external evidence.

### Queries executed

1. `additively weighted Voronoi diagram site insertion deletion Apollonius diagram paper`
2. `site:doc.cgal.org Apollonius graph additively weighted Voronoi diagram circles insertion removal`
3. `granular-ball classifier radius distance decision rule`
4. `granular ball classifier center radius classification`
5. `granular-ball classifier GBkNN distance radius test sample`
6. `granular ball generation radius overlap de-overlap classification`

The web interface does not expose database-wide hit counts, so no fabricated
PRISMA totals are reported.  Screening retained sources only when their
publisher, author-hosted manuscript, DOI record, or maintained technical manual
directly exposed the relevant mechanism.

### Inclusion / exclusion criteria

| Criterion | Include | Exclude |
| --- | --- | --- |
| Decision geometry | Defines `||x-c||-r`, additively weighted sites/circles, or dynamic site update | Point-only or power-distance-only work without this score |
| Update behaviour | Establishes insertion/deletion or the destruction/update of diagram features | Static visual illustrations without update semantics |
| GB relevance | Establishes GB nearest-ball/radius classification or radius/overlap refinement | Application papers that only use the name “granular” |
| Source quality | Peer-reviewed paper, DOI record, author-hosted paper, or maintained project documentation | Unverified summaries and search snippets |

## Verified source matrix

| Source | Verified mechanism | Relation to the Phase-1 candidate | Quality / limitation |
| --- | --- | --- | --- |
| Karavelas & Yvinec (2002) | Dynamic additively weighted Voronoi diagrams support site insertion and deletion. | Replacing `P` by `children(P)` is exactly deletion of one weighted site and insertion of several weighted sites. | Peer-reviewed ESA paper; directly establishes the update class, but is 2-D geometry rather than a GB classifier. |
| Emiris & Karavelas (2006) | An Apollonius diagram is an additively weighted Voronoi diagram; its dynamic predicates are analyzed and implemented. | Confirms this is a mature computational-geometry mechanism, not a new “global interference” operation. | Peer-reviewed computational-geometry paper; no GB labels/purity. |
| CGAL Apollonius Graph manual | Defines `delta(x,(c,w)) = ||x-c||-w`; with nonnegative weights, sites are circles of radius `w`.  It explicitly describes online insertions/deletions and a new circle destroying portions of existing diagram edges. | This is an exact score-level isomorphism with the repository's native rule when `w=r_B`.  It is the direct collision. | Maintained authoritative implementation documentation, not a classification experiment. |
| Xia et al. (2019) | Introduces granular-ball classifiers and GBkNN, based on granular-ball labels and inter-ball distance. | Establishes that nearest-ball GB classification is existing GB methodology; it does not make weighted-site updates a new GB mechanism. | Peer-reviewed *Information Sciences* article; it does not analyze construction-local versus decision-global routing. |
| Pan et al. (2025) | Identifies average/max-radius overlap/coverage issues, then performs de-overlap and radius refinement for classification. | Independent GB-side evidence that radius-induced interactions are already an explicit modeling target. | Peer-reviewed *Applied Intelligence* article; not a direct proof about our parent-to-children intervention. |
| Wang et al. (2026) | Uses local boundary refinement, overlap removal and a different cooperative decision rule. | Shows active recent work already treats ball-boundary interactions as a design target; it does not exactly duplicate our score. | Peer-reviewed *Information Sciences* article; adjacent, not decisive. |

## Why the collision is direct

For a terminal granular ball `B=(c_B,r_B)`, the repository's native classifier
selects the minimum of `||x-c_B||-r_B`.  CGAL defines the cell of a weighted
site `(c,w)` by the same distance and states that nonnegative `w` can be read as
the radius of a circle.  Thus, on the 2-D geometry used by the proposed
Gaussian-blobs, moons and spirals tests, the native terminal partition is an
Apollonius/additively weighted Voronoi diagram after the substitution `w=r_B`.
The claimed local split is simply a weighted-site deletion plus multiple
weighted-site insertions.  Dynamic Apollonius work treats the resulting change
of diagram cells/edges as the expected object of study, including the case where
an inserted circle destroys an existing portion of the diagram.

The construction hierarchy is *not* part of this geometry.  It supplies a
separate provenance partition `R(P)`, while deployment reassigns globally by the
weighted-site lower envelope.  Therefore the proposed result would be a valid
diagnostic of a **mismatch in this particular GBC implementation**, but it would
not establish a new geometric mechanism or a GB-specific update principle.

## Mechanism-collision decision

| Candidate component | Existing work | Residual GB difference | Decision |
| --- | --- | --- | --- |
| Radius-offset terminal score | Exact Apollonius distance | Radius comes from GB members rather than being externally specified | **Exact score collision** |
| Local parent -> children replacement | Dynamic weighted-site deletion + insertion | Parent/children came from a hierarchy | **Direct update collision** |
| Remote decision-region changes | Destruction/update of Apollonius diagram features when sites are inserted/deleted | GBC calls the sites granular balls | **Direct mechanism collision** |
| Radius overlap handling | Recent GB tuning, de-overlap and boundary refinement | Different generation/decision details | Adjacent collision |
| Construction-vs-native discrepancy audit | No direct same-protocol GB paper located in the bounded search | A reproducibility/diagnostic artifact might remain | Not an algorithmic or theory contribution |

### Gate outcome

```text
GB-specific novelty: KILL
Phase-2B empirical cheap test: DO NOT RUN
Permitted residual statement: implementation-specific diagnostic only
Not permitted: new mechanism, new GB routing theory, or an application paper
based on measured nonlocal reassignment.
```

The Phase-1 centre-only and construction controls remain methodologically
correct, but they cannot rescue the contribution: the primary native effect is
already a named, dynamically maintained weighted Voronoi phenomenon.  A
30-cell experiment could demonstrate its magnitude in this codebase, not make
the phenomenon novel.  In accordance with the frozen kill-first protocol, it is
not run.

## Annotated bibliography and verification record

1. **Karavelas, M. I., & Yvinec, M. (2002). _Dynamic additively weighted
   Voronoi diagrams in 2D_. In *Algorithms — ESA 2002* (pp. 586–598).
   https://doi.org/10.1007/3-540-45749-6_52**
   - Relevance: primary antecedent for the precise delete/insert operation.
   - Verification: author-hosted manuscript and DBLP metadata agree with DOI,
     title, authors, venue and year.
   - Quality: peer-reviewed conference source; direct but limited to 2-D.

2. **Emiris, I. Z., & Karavelas, M. I. (2006). The predicates of the
   Apollonius diagram: Algorithmic analysis and implementation.
   _Computational Geometry, 33_(1–2), 18–57.
   https://doi.org/10.1016/j.comgeo.2004.02.006**
   - Relevance: identifies the Apollonius diagram as the additively weighted
     Voronoi diagram and analyzes a dynamic algorithm.
   - Verification: publisher page exposes title, authors, journal, year, pages
     and DOI.
   - Quality: peer-reviewed primary technical source; no GB-specific claim.

3. **Karavelas, M., & Yvinec, M. (2026). _CGAL 6.2: 2D Apollonius Graphs
   (Delaunay Graphs of Disks): User Manual_. CGAL.**
   - Relevance: directly gives `delta(x,P)=||x-c||-w`, identifies nonnegative
     weights with circle radii, and documents online insertion/deletion and edge
     destruction.
   - Verification: maintained official CGAL documentation, checked 2026-08-30.
   - Quality: authoritative software/theory reference; supporting rather than
     substitute evidence for the peer-reviewed sources above.

4. **Xia, S., Liu, Y., Ding, X., Wang, G., Yu, H., & Luo, Y. (2019).
   Granular ball computing classifiers for efficient, scalable and robust
   learning. _Information Sciences, 483_, 136–152.
   https://doi.org/10.1016/j.ins.2019.01.010**
   - Relevance: original GB classifier/GBkNN framework and nearest-ball
     classification context.
   - Verification: publisher record and DBLP metadata agree with DOI, venue,
     title, authors and pages.
   - Quality: peer-reviewed primary GB source; does not analyze our hierarchy
     mismatch.

5. **Pan, J., Lang, G., Xiao, Q., & Yang, T. (2025). A framework of
   granular-ball generation for classification via granularity tuning.
   _Applied Intelligence, 55_, 63.
   https://doi.org/10.1007/s10489-024-05904-1**
   - Relevance: directly discusses max/mean radii, heterogeneous overlap, and
     radius refinement/de-overlap.
   - Verification: publisher preview metadata and DOI record agree.
   - Quality: peer-reviewed recent GB source; adjacent rather than an exact
     parent-to-children counterexample.

6. **Wang, S., Zhan, J., Xia, S., & Ding, W. (2026). Boundary-driven granular
   ball generation and classification via three-way decision. _Information
   Sciences, 755_, 123780. https://doi.org/10.1016/j.ins.2026.123780**
   - Relevance: current GB work on boundary-driven local refinement, overlap
     removal and changed decision aggregation.
   - Verification: publisher page and DBLP record agree with DOI, authors,
     journal, volume and article number.
   - Quality: peer-reviewed and current; mechanism is adjacent, not the reason
     for the KILL verdict.

## Limitations and integrity

- This was a bounded mechanism audit, not a systematic review.  It establishes
  a negative novelty decision because the exact score and dynamic update class
  collide; it does not prove that every possible GBC hierarchy discrepancy has
  been published.
- The direct diagram documentation and the primary dynamic-geometry papers are
  2-D.  The frozen test geometries are 2-D, so that is sufficient for the
  proposed experiment; no claim about arbitrary high-dimensional Apollonius
  algorithms is needed.
- No externally uploaded private data or cross-model review was used.  AI
  assistance must be disclosed if any report is reused in a manuscript.
