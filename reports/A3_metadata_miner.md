# A3 Metadata-First Dataset Miner

The miner catalogues sources before any candidate-data download or MIA. It
records source/task hierarchy, original URL, DOI/paper, license, estimated
shape, group requirements, data modality, download burden, provenance state,
and discrete publication/comparability profiles. It deliberately does not
calculate any privacy, membership, or attack-derived value.

Initial coverage includes OpenML, UCI, KEEL, Zenodo, Harvard Dataverse,
Figshare, Mendeley Data, GEO, PhysioNet, Data.gov, re3data, and Papers With
Code. Repositories that supplied no source/target/license-complete candidate
are explicitly marked rather than silently omitted.

Only two candidates are currently `DOWNLOAD_APPROVED`:

- Arcene: public UCI/CC-BY high-dimensional biomedical binary task; official
  labeled train/validation portions are required.
- Madelon: public UCI/CC-BY high-dimensional redundant/probe benchmark; it is
  a planned negative structural control, not expected positive evidence.

The catalog also keeps human-label uncertainty leads (CIFAR-N/H, ANIMAL-10N,
AlleNoise), GEO subtype datasets, KEEL high-dimensional leads, and PhysioNet
signal tasks. They remain discovered or rejected until original license, target,
group, representation, and resource conditions meet the hard filter.

The machine-readable inputs are:

- `artifacts/dataset_catalog.csv`
- `artifacts/dataset_source_coverage.csv`

No A3 attack ran during this phase.
