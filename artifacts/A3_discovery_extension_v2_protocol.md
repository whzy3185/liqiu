# A3 Discovery Metadata Extension v2

The initial real Discovery pool produced no material positive GB-minus-KMeans
effect and no selection rule. Before reading any new A3 outcome, metadata scope
is extended with one additional source-complete candidate: UCI MicroMass.

MicroMass is a CC-BY MALDI-TOF dataset with a 571-spectrum pure reference panel
covering 20 bacterial species from 213 strains. It has 1,300 numeric features
and explicit strain metadata, so the A3 task must use a strain-group-disjoint
reference/shadow/target protocol. The pure-spectra species task is the only task
eligible for this extension; mixture spectra are not silently added.

The extension sequence is fixed: official archive download, metadata parser,
pre-MIA v1 structural profile, GB structure probe, then a go/no-go hard filter.
No membership attack or selection rule is computed before those steps finish.
