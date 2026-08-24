# V2 semantic codebook report

## Claim

A hierarchical granular latent codebook might improve the task-utility/bit-rate
frontier over k-means, VQ and supervised prototypes.

## Evidence

No experiment was run in this analysis round.

## Negative evidence

The round already found that generic allocation estimators fail in FED and that
existing adaptive GBGC is on the GNN frontier. Progressive/hierarchical semantic
communication is also an occupied mechanism space. Running a codebook probe now
would add another under-motivated application rather than test the two surviving
P1 questions.

## Closest literature

Task-aware quantization, classification-aware quantization, rate-distortion and
progressive semantic communication are mandatory baselines.

## Collision risk

HIGH.

## Decision

`REJECT_THIS_ROUND / NOT_RUN`. No score is interpreted as empirical evidence.

## Next kill test

Only reopen after a predeclared granular hierarchy differs mathematically from
hierarchical k-means/VQ and can be evaluated with frozen encoder/features.
