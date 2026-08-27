# B0 GBFRS Provenance and Baselines

The B0 primary selector is the public `lianxiaoyu724/GBFRS` repository, fixed
at GitHub main commit `0382e0899b0dc5529c89d1b9a11da198464d49ad`. The repository
ships `GBFRS_github(2).rar`; archive SHA-256 is
`5186d7b4be52bf8fae9b64fc7ef080ae8cb5f9033e758bafb07be4cad69b1b3c`.
The extracted `GBFRS.py` runs its official `attribute_reduce(data, pur=1)`
entry point on single-label classification data formatted as
`[features, label, index]`. Its returned selected-feature order is used without
changing its ranking logic.

This is distinct from the MIT-licensed `AldrinLake/GBFRS@25a8bc2` historical
code, which targets multi-label label-distribution learning. The two are not
combined or treated as a replication of each other.

Controls are FRFS from fuzzy-rough-learn 0.2.2, Mutual Information from
scikit-learn, and ReliefF from skrebate 0.8.3. For each shadow run they select
the same number of features as the GBFRS output, so output-size differences do
not create an unfair mask comparison. GBFRS exposes a selected order (partial
ranking); MI and ReliefF expose full rankings; FRFS is evaluated only on releases
it naturally exposes (mask and mask plus count).
