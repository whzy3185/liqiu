# Granular-ball application exploration round

Date: 2026-08-25.

## Explored

This tranche searched low-compute applications and executed 69 new successful
CPU experiments across four granular-ball roles:

| Application | Runs | GB role | Decision |
|---|---:|---|---|
| Edge distribution monitoring | 20 | fixed-memory reference sketch | `REJECT` |
| Numeric cell-error cleaning | 15 | cross-fitted multiscale local context | `REJECT` |
| Online/continual classification | 9 | hard-budget local state | `REJECT` |
| Batch active learning | 25 | annotation/query unit | `REJECT` |

The literature scan separately closed generic anomaly detection, time-series
anomaly detection, continual replay/prototype memory, federated GB caches and
open-world/emerging-class GB memory because direct 2024-2026 GB methods already
occupy those roles.

## New failures and opportunities

- Prototype sketches can reduce drift-monitoring memory by 96.4% and query time
  by roughly 60x versus full MMD, but KMeans gets the same resource benefit and
  higher AUROC. The opportunity is generic compression, not GB.
- Cross-fitted local context detects plausible cell errors, but kNN/tree context
  is much stronger. Removing radius from the same GB partition improves AUPRC.
- Hard-budget local states nearly match SGD on concept/emerging streams with
  sub-millisecond updates. Center-only prediction is consistently as good or
  better, so this is a generic online prototype result.
- Radius-aware active batches help Iris but fail to transfer to four other
  datasets. Same-partition entropy-only selection is stronger overall.

## Ideas killed

- GB center/radius/occupancy as a generic distribution sketch.
- GB multiscale neighborhoods as numeric cell-repair contexts.
- Dynamic GB split/merge/expire state as a unique online advantage.
- GB radius-weighted batch active learning.
- New generic GB anomaly/time-series anomaly method.
- GB replay memory, federated knowledge cache, and open-world memory.

## Current P0

None.

## Current P1

No new application P1 survives. The earlier core C1 purity/noise
risk-resource failure remains a diagnostic `P1`, but direct 2026 fragmentation
work and the absence of a repair prevent promotion.

## Strongest three signals

1. `P1`: purity/noise risk-resource reversal from the previous core campaign;
   stable failure, unresolved mechanism, high collision.
2. `REJECT`: generic hard-budget online prototypes; useful engineering signal,
   but radius/GB attribution is negative.
3. `REJECT`: Iris batch-active-learning signal; one small dataset only and no
   cross-dataset radius advantage.

## Pause reason

This tranche meets the requested pause condition: several low-compute
application fields are either directly occupied by current GB literature or
fail strong matched non-GB and same-partition controls. Continuing immediately
would mean post-hoc score tuning or renaming generic prototype behavior.

The next cycle must start from a genuinely new application pain point and first
state how radius, multi-granularity or ball membership creates an advantage that
cannot be reproduced by the same partition with centers only.
