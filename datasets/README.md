# Dataset protocol

Every dataset has a stable identifier, provenance, license note, checksum when
downloaded, and exactly one primary pool assignment.

## Exploration pool

Used for debugging, counterexample search, mechanism design, and limited cheap
tests. Repeated inspection and tuning are permitted and must be logged.

## Confirmation pool

Held back until a candidate and its decision criteria have been frozen. The
runner requires `confirmation_rationale` and rejects configurations with enabled
hyperparameter search. A dataset may not be moved from exploration to
confirmation after its labels/results have influenced method design.

Assignments live in `registry.jsonl`. Generated data record the generator
version and all parameters in the experiment configuration.

