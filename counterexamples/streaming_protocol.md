# Streaming stress protocol

Six generators expose batch index and ground-truth drift parameters: covariate,
concept, class-prior, density, emerging-class and disappearing-class drift.

Evaluation is prequential by batch: predict batch t using state through t−1,
record metrics, then update. Every incremental granular method must compare with:

1. full rebuild on all observed data;
2. rebuild on a frozen sliding window;
3. no-update initial model;
4. an appropriate classical online/reference learner.

Required metrics: current-batch Accuracy/Macro-F1, recovery delay, update runtime,
memory, granule count/churn, created/split/merged/forgotten granules, emerging
class recall, and calibration/selective risk where available. Update actions and
state checkpoints must be logged. No streaming candidate is promoted until an
incremental method beats rebuild in update cost while preserving recovery risk.
