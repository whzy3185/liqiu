# Granular-Ball Application Map

Updated: 2026-08-25.

This map tracks accepted or formally published granular-ball machine-learning
applications. `ARXIV_ONLY` records are kept separate and do not close novelty by
themselves. Fields not verified from a primary source are marked `UNKNOWN`.

## Status legend

- `PUBLISHED`: proceedings/journal metadata and paper page are public.
- `ACCEPTED`: official accepted-paper evidence or official author artifact is
  public, but a final proceedings page may still be pending.
- `ARXIV_ONLY`: no accepted/published evidence was verified.

## 2026 accepted and published map

### MSRGC-Net - `ACCEPTED`, IJCAI 2026

- **Application:** univariate and multivariate time-series clustering.
- **GB role:** compact anchors and an anchor graph over multiscale reservoir
  representations.
- **Generation:** density-consistent adaptive granular regions.
- **Radius/membership:** abstract confirms regions/anchors; exact radius rule is
  not yet coded from a final full text.
- **Downstream:** training-free multiscale reservoir computing plus consensus
  anchor-graph optimization.
- **Claimed advantage:** avoids quadratic pairwise similarity and iterative deep
  training while improving clustering.
- **Datasets/baselines:** standard univariate/multivariate time-series suites;
  exact table remains `UNKNOWN` pending proceedings/full-text coding.
- **Code:** `UNKNOWN`.
- **Limitation/open edge:** static clustering only; online retrieval/indexing and
  streaming anchor maintenance are not established by the abstract.
- **Evidence:** [arXiv record with IJCAI-2026 acceptance](https://arxiv.org/abs/2606.12077),
  [IJCAI accepted papers](https://2026.ijcai.org/accepted-papers/).

### AD-GBC - `ACCEPTED`, CVPR 2026

- **Application:** medical image segmentation.
- **GB role:** differentiable anisotropic region module in UNet skip refinement.
- **Generation:** learnable centers and vector scales; not recursive classical
  purity splitting.
- **Radius/membership:** anisotropic scale controls feature-to-region aggregation
  and region-to-pixel redistribution through differentiable softmax membership;
  Wasserstein diversity and scale-consistency losses regularize geometry.
- **Downstream:** Rolling-UNet and U-KAN.
- **Claimed advantage:** region-level semantics with anisotropic geometry and
  end-to-end differentiation.
- **Datasets:** BUSI, GlaS, CVC-ClinicDB, ISIC17.
- **Baselines:** two strong segmentation backbones plus prototype/region modules;
  exact paper table is not yet fully coded.
- **Code:** [official MIT repository](https://github.com/SiaShen-dot/AD-GBC).
- **Limitation/open edge:** supervised binary medical segmentation; the module's
  value for lightweight non-medical dense prediction is open.

### SegGBC - `PUBLISHED`, CVPR 2026

- **Application:** clustering-based image segmentation.
- **GB role:** coarse-to-fine segmentation front-end and standalone clustering
  representation.
- **Generation:** fuzzy semantic compactness controls split/merge; stable regions
  avoid redundant reassignment.
- **Radius/membership:** intuitionistic membership, non-membership and hesitation
  augment geometric centers/radii.
- **Downstream:** pixel- and cluster-level unsupervised segmentation methods.
- **Claimed advantage:** plug-in gains above 3.25% SA and 3.92% mIoU with low
  segmentation cost.
- **Datasets:** BSD500/natural images, DUST, LoveDA imagery, COCO-Stuff variants.
- **Baselines:** fuzzy/clustering segmentation, Ball k-means, MGNR and deep
  clustering segmentation.
- **Code:** supplementary material reported; stable standalone repository not
  verified.
- **Limitation/open edge:** image segmentation is occupied; spatial sensor cells,
  superpixel-free remote-sensing change summarization and lightweight deployment
  require distinct mechanisms.
- **Evidence:** [CVF paper page](https://openaccess.thecvf.com/content/CVPR2026/html/Chong_SegGBC_Justifiable_Coarse-to-Fine_Granular-Ball_Computing_for_Enhancing_Clustering_Image_Segmentation_CVPR_2026_paper.html).

### GBOC / GVDD - `PUBLISHED`, AAAI 2026

- **Application:** time-series anomaly detection.
- **GB role:** latent prototypes of compact high-density normal behavior.
- **Generation:** density-guided hierarchical splitting and noisy-structure
  removal.
- **Radius/membership:** anomaly inference uses distance to the nearest GB;
  center alignment compacts learned representations.
- **Downstream:** one-class reconstruction/representation network.
- **Claimed advantage:** robustness under drift/noise with fewer prototypes.
- **Datasets/baselines:** univariate and multivariate time-series anomaly suites;
  classical, nearest-neighbor, clustering and deep anomaly baselines.
- **Code:** public code not verified from the proceedings page.
- **Limitation/open edge:** generic/time-series anomaly is occupied.
- **Evidence:** [AAAI proceedings](https://doi.org/10.1609/aaai.v40i30.39722).

### GFSAF - `PUBLISHED`, AAAI 2026

- **Application:** multi-view clustering.
- **GB role:** fuzzy granular representation for splitting mutual and
  complementary cross-view information.
- **Generation:** GB fuzzy contrastive split in a two-stage representation
  learner.
- **Radius/membership:** fuzzy representation is used; exact radius use remains
  `UNKNOWN` in abstract coding.
- **Downstream:** contrastive representation extraction, cross-view attention
  fusion and clustering.
- **Claimed advantage:** reduces representation degeneration and noise leakage.
- **Datasets:** abstract says eight databases, while the paper table lists nine
  (WebKB, Multi-COIL-10/20, Caltech101-7, Prokaryotic, NUSWIDE, Reuters, DHA,
  UCI-Digits); retain this source discrepancy rather than silently choosing one.
- **Baselines:** recent multi-view clustering/contrastive methods.
- **Code:** `UNKNOWN`.
- **Limitation/open edge:** generic multi-view clustering is occupied.
- **Evidence:** [AAAI proceedings](https://doi.org/10.1609/aaai.v40i28.39556).

### HOARD - `PUBLISHED`, AAAI 2026

- **Application:** multi-view representation alignment and clustering.
- **GB role:** granular-ball contrastive alignment of shared features.
- **Generation:** learned representation is decoupled into shared/specific
  components; exact GB generation remains `UNKNOWN` in abstract coding.
- **Radius/membership:** not identified as the main contribution.
- **Downstream:** prototype collaborative alignment, information distillation and
  attention fusion.
- **Claimed advantage:** adaptive hierarchical cross-view knowledge transfer.
- **Datasets/baselines/code:** benchmark multi-view datasets and recent MVC
  baselines; code `UNKNOWN`.
- **Limitation/open edge:** another direct occupation of multi-view clustering;
  cross-source sensor fusion outside clustering remains a possible adjacent task.
- **Evidence:** [AAAI proceedings](https://doi.org/10.1609/aaai.v40i34.40136).

### FedOC-GB - `PUBLISHED`, Neural Networks 2026

- **Application:** federated open-intent classification.
- **GB role:** client knowledge base and server aggregation unit.
- **Generation:** local intent representations are compressed into GB knowledge.
- **Radius/membership:** geometric region knowledge participates in open-class
  representation; exact rule is pending full-text component coding.
- **Downstream:** federated open-intent recognition.
- **Claimed advantage:** transferable knowledge under privacy and unknown intents.
- **Datasets/baselines:** intent benchmarks and federated open-world baselines.
- **Code:** [reported public repository](https://github.com/jiezhang64/FedOC-GB).
- **Limitation/open edge:** generic federated GB caching/open-intent is occupied.
- **Evidence:** [PubMed record](https://pubmed.ncbi.nlm.nih.gov/41830873/).

### Beneficial Noise OIC - `PUBLISHED`, Pattern Recognition 2026

- **Application:** noisy open-intent learning.
- **GB role:** separate clean, in-distribution-noise and OOD-noise regions and
  convert some OOD noise into representation signal.
- **Generation:** unsupervised GB clustering of training features.
- **Radius/membership:** ball relations, purity/consistency and local evidence;
  radius is not the sole contribution.
- **Downstream:** open-intent representation learning.
- **Claimed advantage:** robust recognition under mixed IND/OOD label noise.
- **Datasets/baselines:** open-intent benchmarks and noise-robust OIC methods.
- **Code:** [official repository](https://github.com/Liyanhuaa/BNO_GB).
- **Limitation/open edge:** open intent plus noisy labels is occupied.
- **Evidence:** [publisher DOI](https://doi.org/10.1016/j.patcog.2026.113283).

### GBNAD / Granular-ball Guided Coulomb Force - `PUBLISHED`, Pattern Recognition 2026

- **Application:** anomaly detection.
- **GB role:** global/local structural units for Coulomb-force anomaly scoring.
- **Generation/radius/membership:** full component coding pending.
- **Downstream:** unsupervised anomaly score.
- **Claimed advantage/datasets/baselines:** publisher reports robust anomaly
  structure; exact tables remain `UNKNOWN`.
- **Code:** [official repository](https://github.com/Caspar-lab/GBNAD).
- **Limitation/open edge:** generic anomaly detection is occupied.
- **Evidence:** [publisher DOI](https://doi.org/10.1016/j.patcog.2026.113785).

### TWD-BDGB - `PUBLISHED`, Information Sciences 2026

- **Application:** supervised classification.
- **GB role:** boundary-driven bottom-up regions with three-way uncertainty.
- **Generation:** medium-granularity expansion, adaptive radii, homogeneous merge
  and heterogeneous overlap removal.
- **Radius/membership:** adaptive boundary blocking and cooperative multi-ball
  decision.
- **Downstream:** standalone classifier.
- **Claimed advantage:** robust, parameter-light boundary representation.
- **Datasets/baselines:** public classification datasets and GB classifiers.
- **Code:** [reported repository](https://github.com/sw380957-create/TWD-BDGB).
- **Limitation/open edge:** another classifier or split/merge variant is high
  collision.
- **Evidence:** [publisher DOI](https://doi.org/10.1016/j.ins.2026.123780).

### ScOrGBC - `PUBLISHED`, Applied Soft Computing 2026

- **Application:** robust classification under noise.
- **GB role:** stable-center, optimized-radius classifier units.
- **Generation:** controlled ball count, K-means++ centers, iterative de-overlap,
  justifiable-granularity radius optimization.
- **Radius/membership:** radius is explicitly optimized and used by classifier.
- **Downstream:** ScOrGBC classifier.
- **Claimed advantage:** fewer/stabler balls and accuracy gains under 20-40%
  noise.
- **Datasets:** 20 public datasets.
- **Baselines/code:** four GB classifiers; code `UNKNOWN`.
- **Limitation/open edge:** robust GB classification and radius optimization are
  occupied.
- **Evidence:** [publisher DOI](https://doi.org/10.1016/j.asoc.2026.114852).

### 3W-GBSVM++ - `PUBLISHED`, Applied Soft Computing 2026

- **Application:** risk-aware classification with an explicit uncertain region.
- **GB role:** optimized-granularity inputs to GBSVM and three-way decisions.
- **Generation:** justifiable-granularity coverage/specificity optimization.
- **Radius/membership:** shadowed/fuzzy transformation supports certain versus
  uncertain decisions; radius is part of GB construction, not the sole value.
- **Downstream:** GBSVM++ and 3W-GBSVM++.
- **Claimed advantage:** robust classification and reduced decision risk under
  noise/ambiguity.
- **Datasets/baselines:** 16 public benchmarks and eight GB classifiers (the
  publisher highlights and abstract disagree on a 12/16 count, so retain 16 from
  the abstract/full experiment statement).
- **Code:** `UNKNOWN`.
- **Limitation/open edge:** three-way GB-SVM/classification is directly occupied.
- **Evidence:** [publisher DOI](https://doi.org/10.1016/j.asoc.2026.114593).

### CMGBIFSC - `PUBLISHED`, Applied Soft Computing 2026

- **Application:** large-scale and imbalanced classification.
- **GB role:** class-mapped region representation with intuitionistic fuzzy
  uncertainty.
- **Generation:** logarithmic ball-count scaling, power-based per-class
  allocation and class mapping.
- **Radius/membership:** intuitionistic membership/non-membership/hesitation and
  fuzzy distance.
- **Downstream:** CMGBIFSC and CMGBKNN.
- **Claimed advantage:** fewer redundant partitions, faster generation and
  improved large-scale accuracy.
- **Datasets:** 12 public large-scale datasets, nine imbalanced.
- **Baselines/code:** GBKNN variants and KNN; data/code on request.
- **Limitation/open edge:** class-aware allocation and large-scale imbalance are
  occupied.
- **Evidence:** [publisher DOI](https://doi.org/10.1016/j.asoc.2026.116020).

### GBRSR / GB robust representation for social recommendation - `PUBLISHED`, EAAI 2026

- **Application:** social recommendation.
- **GB role:** cross-granularity representation distillation and structural
  denoising of user/item graphs.
- **Generation/radius/membership:** user/item points are adaptively partitioned
  into multigranularity balls; radius-specific behavior is not the main abstract
  claim.
- **Downstream:** social recommender with diffusion representation denoising.
- **Datasets:** three real-world recommendation datasets; exact names/baselines
  await full-table coding.
- **Code:** `UNKNOWN`.
- **Limitation/open edge:** generic social recommendation is occupied, but
  low-memory session retrieval or cold-start indexing may be distinct.
- **Evidence:** [publisher DOI](https://doi.org/10.1016/j.engappai.2026.114979).

### GBDiff - `PUBLISHED`, Expert Systems with Applications 2026

- **Application:** multimodal recommendation.
- **GB role:** capture coarse global user interests to complement fine-grained
  interaction propagation.
- **Generation/radius/membership:** GB representation over the interaction graph;
  exact geometry remains `UNKNOWN` in abstract coding.
- **Downstream:** conditional graph diffusion recommender.
- **Claimed advantage:** denoise interactions and representations while using
  multimodal guidance.
- **Datasets:** three recommendation datasets.
- **Code:** `UNKNOWN`.
- **Limitation/open edge:** generic multimodal recommendation with GB
  representation is occupied.
- **Evidence:** [publisher DOI](https://doi.org/10.1016/j.eswa.2026.132124).

## 2025 published application anchors

| Work | Venue | Application | GB role | Code / limitation |
|---|---|---|---|---|
| SGBGC | AAAI 2025 | scalable GNN training | supervised graph coarsening / supernodes | Direct graph-coarsening occupation; [paper](https://doi.org/10.1609/aaai.v39i11.33404) |
| GBGC | IJCAI 2025 | graph coarsening | adaptive coarse-to-fine GB supernodes | Public artifact lacks author code; graph coarsening occupied; [paper](https://doi.org/10.24963/ijcai.2025/388) |
| GRICP | AAAI 2025 | point-cloud fine registration | robust correspondence/registration units | Registration occupied; [paper](https://doi.org/10.1609/aaai.v39i4.32164) |
| MOGB | AAAI 2025 | open-intent classification | multigranularity centroid/radius boundaries | Open intent occupied; [paper](https://doi.org/10.1609/aaai.v39i23.34630) |
| GBRIP | AAAI 2025 | imbalanced partial-label learning | coarse regions and multicenter label disambiguation | Weak supervision/PLL occupied; [paper](https://doi.org/10.1609/aaai.v39i16.33916) |
| MGBCC | AAAI 2025 | multi-view clustering | mesoscopic cross-view contrastive units | MVC occupied; [paper](https://doi.org/10.1609/aaai.v39i19.34274) |
| GB-MKKM | IJCAI 2025 | multiple-kernel clustering | GB-induced kernel units | Kernel clustering occupied; [paper](https://www.ijcai.org/proceedings/2025/738) |
| GB-QkNN | IJCAI 2025 | approximate kNN acceleration | GB compression feeding HNSW/quantized retrieval; despite the title, this is not a generic quantum-computing result | Fast/approximate kNN occupied; [paper](https://www.ijcai.org/proceedings/2025/739) |
| CS-GBSBF | IJCAI 2025 | facial expression recognition | visual-spatial GB representation fusion | FER occupied; [paper](https://www.ijcai.org/proceedings/2025/178) |
| GBRAD | Pattern Recognition 2025 | anomaly detection | GB state-transition graph for random walk | Generic anomaly occupied; [paper](https://doi.org/10.1016/j.patcog.2025.111588) |
| LDGBG | Information Sciences 2025 | classification / GB generation | local-density generation | New generation alone is high collision; [paper](https://www.sciencedirect.com/science/article/pii/S002002552500427X) |

## Role-to-application frontier

| Successful GB role | Already occupied | Adjacent low-compute frontier |
|---|---|---|
| Anchor graph | time-series clustering, graph coarsening | vector indexing, retrieval shortlist, spatial search |
| Differentiable anisotropic region | medical segmentation | lightweight dense prediction, sensor maps, small-data vision |
| Fuzzy multigranularity representation | multi-view clustering, image segmentation | heterogeneous sensor fusion, semi-supervised consistency |
| Knowledge representation | federated/open intent | local knowledge routing outside intent, constrained edge lookup |
| Compressed prototype | anomaly, kNN, clustering | approximate search latency/recall, cache admission, cold-start retrieval |
| Robust structural prior | noisy labels, anomaly, registration | industrial fault localization, spatial missingness, structured corruption |

## Map policy

1. Accepted/published sources close exact application-role combinations.
2. `ARXIV_ONLY` sources raise collision risk but do not close a candidate alone.
3. A new candidate need not prove radius-specific value. It must show stable
   application value not explained by matched KMeans/prototype/tree/coreset
   controls and must differ materially from an occupied role-task pair.

## ArXiv-only watchlist

- **3DGBGS** (`ARXIV_ONLY`, 2026): partitions SfM point clouds into 3D granular
  balls for compact Gaussian Splatting / novel-view synthesis. It raises
  collision risk for point-cloud compression but does not count as accepted
  occupation. [arXiv](https://arxiv.org/abs/2607.26578)
- **SCGNN** (`ARXIV_ONLY`, 2026): GB semantic anchors and pseudo-label
  consistency for GNNs. [arXiv](https://arxiv.org/abs/2605.02617)
- **MDL-GBC** (`ARXIV_ONLY`, 2026): local description-length model selection for
  boundary-aware GB classification. [arXiv](https://arxiv.org/abs/2605.11406)
