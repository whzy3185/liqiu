# Purity Contamination Theory Collision Audit

The audit distinguishes the fixed-geometry/pruning object from adaptive GBC
generation, classifier risk, and standard marked-tree combinatorics.  It uses
method/theory material rather than title-only screening, but does not claim an
exhaustive review of every decision-tree or robust-clustering result.

| claim | closest result | collision | mathematical object | novelty risk | action |
| --- | --- | --- | --- | --- | --- |
| C1 purity threshold is label-noise sensitive | GBC, GBS, VPGB, GBCRS noisy-label methods | direct | purity/majority aggregation and accuracy under label noise | high | do not claim |
| C2 one error can create a small/singleton ball at high purity | GBC overview and GBS discussion | direct motivation, not fixed-tree formula | recursive generation with purity 1 | high for qualitative statement | retain only as lemma context |
| C3 terminal-ball amplification under m errors | no direct fixed-tree purity-frontier theorem located | partial | terminal frontier of a label-independent tree | medium | formalize and test |
| C4 balanced-tree m scaling | ancestor unions / tries / Steiner subtrees are standard combinatorics | likely standard tool | marked leaves in a complete binary tree | high if merely renamed | reformulate around exact purity-frontier characterization |
| C5 global threshold fidelity/noise incompatibility | existing repository Proposition 1; noisy-label GB papers motivate it | direct local incompatibility | single-node purity threshold | high | not standalone |
| C6 compression/robustness tradeoff | GBS/VPGB/GBCRS assess accuracy and/or reduction empirically | partial | terminal count versus label contamination | medium | require recursive structural cost |
| C7 fixed geometry + label-dependent pruning sensitivity | no direct systematic theorem located in scoped sources | partial | a fixed hierarchical partition with purity stopping | medium | retain as combined object |
| C8 adaptive topology amplifies fixed-tree effect | adaptive GB methods have topology + stop coupling, but no decomposition theorem located | partial | rebuilt geometry versus frozen pruning | medium | outside initial theorem; never infer automatically |

## Gate

Decision: `REFORMULATE_ONCE`.

The standard marked-leaf/ancestor-union bound cannot be the novelty claim.
The one allowed reformulation is to seek an exact correspondence between
purity-pruning frontiers and monochromatic terminal subtrees, then separate
what is standard combinatorics from any new multi-threshold
fidelity--robustness--compression consequence.  If that correspondence yields
only the known ancestor-union lemma plus local threshold algebra, Prompt 3 must
issue `KILL_PURITY_CONTAMINATION_THEORY` before any controlled or real-data
experiment.
