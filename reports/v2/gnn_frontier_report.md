# V2 GNN frontier report

## Claim

Existing granular graph coarsening might waste nodes relative to the empirical
downstream GCN risk-compression frontier.

## Evidence

Full Graph, random, heavy-edge, clean-room adaptive GBGC and disclosed
fixed-ratio GBGC were tested on Cora, Citeseer and PubMed with seeds 1/7/21 and
the same sparse CPU GCN. The corrected valid set has 99 runs. Thirty-three old
Citeseer runs with an in-place extended-matrix reorder bug remain in JSONL but
are excluded and replaced by `v2gnnfix-*` records.

Clean-room adaptive GBGC is node-risk Pareto-nondominated in all nine
dataset×seed cases:

- Cora: mean retained ratio 0.327, Accuracy 0.630; full graph 0.798.
- Citeseer: ratio 0.422, Accuracy 0.680; full graph 0.657.
- PubMed: ratio 0.432, Accuracy 0.768; full graph 0.780.

## Negative evidence

GBGC is a clean-room paper-spec implementation because the public artifact has
no code or license. Fixed-ratio Algorithm 4 is under-specified and every record
lists deviations. GBGC preprocessing takes roughly 0.2–0.5 s on Cora/Citeseer
and 2–5 s on PubMed, much slower than heavy-edge matching. Cora results are
seed-sensitive.

## Closest literature

GBGC (arXiv:2506.19224) directly implements adaptive region-dependent graph
granularity. See `gbgc_code_audit.md`.

## Collision risk

HIGH. Existing adaptive GBGC already lies on the observed risk-node frontier.

## Decision

`REJECT_NONUNIFORM_GNN_PROTOTYPE`. Do not implement GNN-3, heterophily tests,
large-graph scaling, GAT or GraphSAGE in this round.

## Next kill test

None. Reopen only with an independent preprocessing-time/memory mechanism that
can beat both adaptive GBGC and heavy-edge.
