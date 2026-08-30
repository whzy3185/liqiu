# Adaptive Purity Validity Audit — OUSH Branch

Date: 2026-08-30
Branch: `oush`
Status: `KILL_GB_SPECIFIC_CLAIM / RETAIN_GENERIC_NEGATIVE_RESULT`

## Question

For a final granular ball \(B_j\), compare the construction-set majority
proportion

\[
\hat p_j^{\mathrm{train}}
\]

against fresh test correctness conditional on the classifier's actual native
terminal routing

\[
p_j^{\mathrm{fresh}}=P(Y=\hat y_j\mid R_{\mathrm{native}}(X)=j).
\]

The target gap is \(\Delta_j=\hat p_j^{\mathrm{train}}-p_j^{\mathrm{fresh}}\).
The question is not whether a train--fresh gap can occur. The question is
whether purity-driven adaptive GB generation amplifies it beyond matched generic
adaptive supervised partitions.

## Prior-work collision

The restricted literature audit finds a **B-level residual empirical question**,
not a new theoretical problem.

- Adaptive GBC uses label purity in recursive split/stopping decisions; this is
  established in Xia et al., *IEEE TNNLS* (2024),
  [doi:10.1109/TNNLS.2022.3203381](https://doi.org/10.1109/TNNLS.2022.3203381).
- Split-selection bias in recursive partitions is established in Loh and Shih,
  *Statistica Sinica* (1997),
  [paper](https://www3.stat.sinica.edu.tw/statistica/j7n815/j7n815.htm), and
  in Hothorn, Hornik, and Zeileis, *JCGS* (2006),
  [doi:10.1198/106186006X133933](https://doi.org/10.1198/106186006X133933).
- Honest estimation after adaptive partition selection is established for tree
  leaves in Athey and Imbens, *PNAS* (2016),
  [doi:10.1073/pnas.1510489113](https://doi.org/10.1073/pnas.1510489113).
- Held-out/conformal selective risk control is established by Angelopoulos et
  al., *ICLR* (2024),
  [Conformal Risk Control](https://openreview.net/forum?id=33XGfHLtZg), and
  selective conformal methods already address selection-aware coverage.

No screened GB paper directly evaluated the full chain

\[
\text{selected training-ball purity}
\rightarrow
\text{fresh native-routing reliability}
\rightarrow
\text{honest correction},
\]

but that absence alone is insufficient for a paper. A GB-specific residual had
to survive CART and matched KMeans controls.

## Frozen real-data audit

Five real datasets were used: Iris, Wine, Breast Cancer, Digits, and Dry Bean.
Each used three fixed seeds (1, 7, 21), a stratified 60/20/20
structure/calibration/test split, structure-only standardization, and native
routing on calibration/test data.

Methods:

1. Fixed-purity clean-room GBC at \(\tau=0.90\).
2. Parameter-free adaptive GBC control, following the public adaptive generator's
   heterogeneous-label seeding, weighted-purity acceptance, de-overlap, and
   final global reassignment. It is a clean-room control, not author-verified
   code.
3. Unsupervised KMeans with the same number of final cells as fixed GBC.
4. CART with the same maximum leaf count as fixed GBC.
5. Unsupervised KMeans and CART separately matched to parameter-free adaptive
   GBC's final cell count.

For GB, native routing minimizes \(\|x-c_j\|-r_j\). Construction membership
and native routing were recorded separately. The adaptive GB construction/native
overlap was high (median 0.92--1.00 by dataset), so the main result is not an
artifact of silently substituting construction membership for deployment routing.

## Results

Adaptive GB had positive weighted train-purity optimism on all five datasets,
but it did **not** exceed the matched CART control. The median adaptive-minus-CART
weighted-optimism differences were:

| Dataset | Adaptive GB optimism | Adaptive minus matched CART |
| --- | ---: | ---: |
| Iris | 6.67 pp | 0.00 pp |
| Wine | 2.78 pp | -5.56 pp |
| Breast Cancer | 3.06 pp | -5.14 pp |
| Digits | 7.08 pp | -7.36 pp |
| Dry Bean | 9.50 pp | -0.56 pp |

The pre-registered GB-specific gate required adaptive GB to exceed CART by at
least 2 pp for all seeds on at least four of five datasets. It passed on **0/5**.

The high-purity/small-support slice (training purity at least 0.90, support at
most 5) reached a median gap of at least 5 pp on only 3/5 datasets. This is
compatible with known small-cell and adaptive-leaf behavior, not a GB-specific
mechanism.

Parameter-free adaptive GBC also hit the explicit depth/overlap safety cap for
Breast Cancer, Digits, and Dry Bean. These capped cases are not used as evidence
for a special GB effect.

Calibration-only scoring sometimes reduced test selective risk relative to raw
training purity, particularly on Digits and Dry Bean, but results were not
uniform across methods and coverage targets. Since honest/calibrated estimation
is already a generic method and the GB-specific gate failed, no conformal or
correction-development stage is warranted.

## Decision

### KILL: GB-specific adaptive purity validity claim

The data support a generic statement only:

> Training majority purity of adaptively selected local regions can overstate
> fresh routed correctness; generic adaptive supervised partitions can exhibit
> the same or larger effect.

They do not support:

- a claim that GB purity-driven generation has a distinctive reliability failure;
- a new calibration or conformal method for GB purity;
- a claim that held-out purity is a GB-specific contribution.

No correction/confirmation experiment should be used to rescue the direction.

## Reproducibility and artifacts

The full audit was independently re-run. The gate decision and the
adaptive-versus-CART table were byte-identical:

```json
{
  "verification_status": "VERIFIED",
  "verdict": "KILL_OR_DOWNGRADE_GB_SPECIFIC_CLAIM"
}
```

Tracked scripts:

- `studies/purity_validity/adaptive_gbc.py`
- `scripts/run_purity_validity_real_audit.py`
- `scripts/analyze_purity_validity_real_audit.py`

Generated artifacts:

- `results/oush_adaptive_purity_v1/ball_level.csv`
- `results/oush_adaptive_purity_v1/selective.csv`
- `results/oush_adaptive_purity_v1/analysis/gate_decision.json`
- `results/oush_adaptive_purity_v1/analysis/adaptive_vs_cart.csv`
- `results/oush_adaptive_purity_v1/analysis/reproduction_validation.json`

## Failure log

The first run failed before model execution because SciPy's ARFF reader received
bytes rather than a text stream. The loader was corrected to use `TextIOWrapper`;
the subsequent full run and independent rerun completed. This failure produced
no scientific data and is retained here for traceability.
