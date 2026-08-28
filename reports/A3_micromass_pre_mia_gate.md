# A3 MicroMass Pre-MIA Gate

The UCI MicroMass extension passes its pre-MIA admission gate.  The official
archive parses to the frozen pure-reference species task only: 571 spectra,
1,300 numeric features, 20 species, and 213 bacterial strains.  Its mixture
panel is excluded.  All 20 species have at least seven strains (range 7--20),
which permits a deterministic species-preserving allocation to external
reference, shadow, target, and group-disjoint member/nonmember subsets.

The frozen v1 structural profile is unusual relative to the first real pool:
the k=10 local-label disagreement is 0.571, boundary-sample fraction is 0.907,
minority-island proxy is 0.805, and mean geometry-label conflict is 0.146.
At the same time, the GB probe has only 51 balls at purity 0.70 and 57 at 0.99
(1.12x fragmentation), with 77.2% of 0.99 balls of size at most two.  These
are retained as separate descriptive facts; no composite score or inferred
privacy ranking was created.

Decision: `ADMIT_A3_MICROMASS_GROUP_DISCOVERY_V1`.  Admission is based solely
on official provenance, parser/group feasibility, and frozen pre-MIA structure.
The next result must use the strain-disjoint protocol recorded in
`artifacts/A3_micromass_group_discovery_protocol.json`; it cannot establish a
general selection rule by itself.
