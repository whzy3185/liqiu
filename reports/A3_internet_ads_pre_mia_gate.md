# A3 Internet Advertisements Pre-MIA Gate

The official UCI archive passed an archive test and reproducibly parses to
3,279 rows, 1,558 documented numeric fields, and a binary target (459 ad,
2,820 non-ad).  The official documentation specifies that the three continuous
fields can use `?` for unknown; the parser retains all fields and represents
only those unknown entries as missing, for the frozen per-scope median
imputation protocol.  No group identifier is documented by UCI.

The frozen structural profile has low local-label disagreement (0.041 at k=10)
and low mean geometry-label conflict (0.047), but a GB probe produces a sharp
purity trajectory: one ball at 0.70 and 50 balls at 0.99 (50x), with 22.0% of
0.99 balls of size at most two.  These are descriptive, separate metrics; no
aggregate score or membership result was used.

Decision: `ADMIT_A3_INTERNET_ADS_DISCOVERY_V1` as a high-fragmentation,
low-conflict near-boundary control.  It is sufficiently large for the existing
strict independent reference/shadow/target protocol.  It cannot be used to
retroactively redefine a positive-regime filter.
