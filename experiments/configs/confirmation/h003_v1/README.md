# H-003 confirmation protocol (pre-result registration)

Frozen before any model result was inspected for OpenML 44, 1494 or 1479.

Datasets: Spambase, QSAR biodegradation and Hill-Valley. All are Public binary
OpenML datasets and were not used in exploration. Methods: clean-room original
GBC (author-verified) and author accelerated GBG. Conditions: purity 0.70, 0.85,
1.00; seeds 1/7/21/42/2026. No threshold is selected or tuned.

Primary confirmation criterion:

1. At least one dataset benefits by at least 0.02 mean Accuracy when moving from
   p=.70 to a higher tested purity; and
2. at least one different dataset either loses mean Accuracy or gains at most
   0.01 while mean granules increase by at least 5×; and
3. the incompatible-regime pattern appears for both generation methods, though
   the responsible dataset may differ.

Secondary outputs: ECE, Macro-F1, runtime and granule count. Failure of any
primary item weakens H-003 and prevents P0 survivor status. These data remain in
the confirmation pool and must not be used for mechanism tuning.
