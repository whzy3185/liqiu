# A3 Musk1 Group-Aware Targeted Experiment

Musk1 contains multiple conformations for each molecule. Its release/membership
experiment therefore uses `molecule_name` as a non-overlapping entity group;
neither molecule nor conformation identifiers enter the numeric feature matrix.

The test is exploratory but pre-result frozen. It evaluates natural labels,
then controlled member-training label noise of 5% and 10%, each over new seeds
2, 13, 73, 314, and 808. It uses the complete A3 release trajectory, logistic
and random-forest attacks, and matched-k KMeans. The two noise levels are
explicit semi-synthetic interventions, not claims about natural Musk1 labels.

The output may provide targeted support, a boundary case, or negative evidence;
none of the three conditions or five seeds will be removed after inspection.
