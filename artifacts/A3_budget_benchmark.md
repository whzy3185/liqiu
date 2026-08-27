# A3 Budget Benchmark

The first complete pipeline benchmark used Breast Cancer, seed 1, all five
predeclared refinement thresholds, three release levels, matched-k KMeans, and
both attack models. It produced 60 aggregate result rows and 498 ball metadata
records in about 15 seconds with one outer worker.

The benchmark establishes that the current CPU budget can support the frozen
six-dataset, five-seed discovery roster. It is not an effect-based inclusion
decision and it is retained separately from the later resumable A3 results.

Two output revisions are retained: the initial budget CSV and a formal A3
revision with parent-ball and refinement-depth fields. The former has valid
attack rows but incomplete ball lineage, so only the latter contributes ball
mechanism analysis.
