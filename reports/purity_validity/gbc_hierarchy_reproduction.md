# Instrumented GBC Hierarchy Reproduction

`InstrumentedGranularBallClassifier` was compared to the unchanged clean-room
`GranularBallClassifier` at tau 0.90, seed 1 on null-label, smooth-moderate,
and piecewise smoke instances. Terminal ball count, construction memberships,
centers, radii, purity, majority labels, class counts, and native predictions
match exactly within strict numeric tolerance: `GBC_REPRODUCTION = PASS`.

Construction-hierarchical self-routing is 1.000 in all three cases. Native
boundary-distance self-routing is 0.9975, 0.9600, and 0.9725 respectively.
The latter is a defined construction-to-decision region mismatch, not an
instrumentation failure. All later GBC results must retain separate construction
and native routing fields plus their reliability transfer difference.
