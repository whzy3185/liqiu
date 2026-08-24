# Local annotator competence novelty and data audit

Checked: 2026-08-25.

## Direct granular-ball collision

No direct 2024-2026 work was found for granular-ball regions as the conditioning
variable of annotator-specific competence or confusion matrices. This negative
search result justified one Cheap Test; it is not proof of novelty.

Adjacent GB supervision work is dense:

- GBRIP uses granular-ball multi-center representation for imbalanced partial
  label learning ([AAAI 2025](https://doi.org/10.1609/aaai.v39i16.33916)).
- MOGB constructs multigranularity center/radius decision boundaries for open
  intent classification ([AAAI 2025](https://doi.org/10.1609/aaai.v39i23.34630)).
- BNO-GB uses GB-level and sample-level neighborhood evidence for noisy open
  intent labels ([Pattern Recognition 2026](https://doi.org/10.1016/j.patcog.2026.113283)).

These methods do not model worker-by-region competence, but they raise the bar:
"GB + ambiguous labels" is already occupied and cannot be the contribution.

## Strong non-GB neighbors

- Dawid-Skene remains the essential global worker-confusion baseline.
- NUTMEG models annotator competence while retaining group disagreement. Its
  groups are user-provided annotator subpopulations or behavior clusters, not
  item-feature regions
  ([EMNLP 2025 code](https://github.com/jonathanivey/NUTMEG)).
- Crowd-Kit provides maintained implementations of Majority Vote,
  Dawid-Skene, GLAD and MACE under Apache-2.0
  ([repository](https://github.com/Toloka/crowd-kit)). The original MACE
  repository is not the preferred artifact because its source is all-rights-
  reserved.
- CROWDLAB and ActiveLab cover classifier-informed annotator quality and
  item-level relabel selection under Apache-2.0
  ([cleanlab](https://github.com/cleanlab/cleanlab)).
- Online incomplete-response aggregation models unknown worker reliability and
  reports Duck, RTE and PostSent results
  ([2026 open-access paper](https://doi.org/10.1007/s44443-025-00381-z)).

## Artifact and data availability

- NUTMEG is MIT licensed and exposes a plain Python implementation plus a faster
  package. A terminal clone was attempted but GitHub transport timed out after
  75 seconds in this environment.
- The browsable NUTMEG repository does not vendor its raw response datasets. Its
  `data/` directory contains splits and preprocessing code; Popquorn politeness
  and offensiveness raw CSVs must be supplied externally.
- Classic RTE/Duck crowd matrices are suitable for aggregation, but this
  candidate also requires stable item features or embeddings for region models.
  No licensed, locally runnable package containing both response matrices and
  frozen item features was established during the audit.

Dataset routing from the independent audit:

| Dataset | Aggregation artifact | Local-GB blocker |
|---|---|---|
| Bluebirds | 108 items, 39 workers, 4,212 labels; stable labels/truth files | No item images/features; dataset terms not separately stated |
| RTE | 800 items, 164 workers, 8,000 labels | Source repo has no license and omits text pairs/task mapping |
| Dog | 807 items, 109 workers, 8,070 labels | No images/license; truth rows repeat per annotation and require validation |
| LabelMe | peerannot installer expects images and answer matrix | External archive is Cloudflare-blocked and has no clear data license |
| Music | MTurk answers plus GTZAN content | Kaggle/manual download, data rights and known GTZAN integrity issues |

Bluebirds, RTE and Dog could verify feature-free aggregation only. Constructing
balls from their annotation matrices would leak worker behavior into the item
geometry and would not test feature-local competence.

Therefore the first gate used three semi-real datasets with real geometry/truth
and fully pre-realized synthetic annotators. The report does not claim real crowd
validation. Real datasets were intentionally deferred until the GB attribution
gate passed; it did not.

## Verdict

The application-level novelty risk was `MEDIUM`, not a direct collision. The
tested mechanism is nevertheless `REJECT`: matched local baselines exploit the
same competence heterogeneity more effectively, and removing radius from the
same hierarchy does not reduce performance.
