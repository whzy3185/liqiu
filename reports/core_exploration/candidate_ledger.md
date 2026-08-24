# GB core candidate ledger

| Candidate | Final status | Frozen evidence | Reason |
|---|---|---|---|
| C1 purity-chasing noise fragmentation | `P1` | 20%/30% noise: 120/120 paired cells use more balls and lose clean accuracy | Stable GB-specific risk/resource reversal, but no repair and direct 2026 collision |
| C2 minority masking | `REJECT` | 20:1/50:1: 60/60 `tau=.85` runs stop at one ball with zero recall | Existing `tau=1` arm restores 92.91% recall at 50:1 with 5.33 balls; occupied repair space |
| C3 shift confidence failure | `REJECT` | 30/40 primary runs have structurally constant confidence; only density drift preserves accuracy while worsening UQ | Independent cross-shift gate failed; prior shift reduces to C2 |

No candidate is P0. C1 may continue only through collision/equivalence and
validation-selection kill tests. C2 may appear only as a joint noise-imbalance
stress condition inside C1, not as a separate imbalanced-learning direction.
C3 is closed unless a preregistered severity sweep establishes confidence
failure before point-risk failure in at least two shifts.

Next GB-core queue: nonlocal routing interference under
`||x-center||-radius`, where a local split may change remote assignments. This
must first survive three geometries, both generators and five seeds; it is not
promoted before that test.
