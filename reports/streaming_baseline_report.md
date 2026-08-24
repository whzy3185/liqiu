# Streaming baseline report

Seventy-two prequential runs cover six deterministic drift types, four frozen
strategies and three seeds. Every batch is predicted before update.

Main observations:

- Concept drift: full-history rebuild GBC ≈0.63 Accuracy, 3-batch sliding rebuild
  ≈0.77, online SGD ≈0.87. Accumulating stale concepts is harmful.
- Covariate shift: sliding GBC and SGD ≈0.99, full rebuild ≈0.90, no-update ≈0.72.
- Prior shift: both rebuild GBC strategies ≈0.96; SGD reaches 1.00; no-update
  collapses to ≈0.47.
- Emerging class: sliding GBC ≈0.98 and SGD ≈1.00; full rebuild ≈0.98;
  no-update cannot represent the new class and averages ≈0.87.
- Density and disappearing-class streams are too easy for this generator:
  no-update is already competitive/perfect, so they do not support adaptation.

These controls establish the required rebuild/window/online baselines but provide
no unique streaming-GBC advantage. A future incremental granular method must
beat sliding rebuild in update cost while matching SGD risk/recovery. Candidate
10 remains outside survivors.
