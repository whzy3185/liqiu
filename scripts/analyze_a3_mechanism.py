"""Generate reproducible A3 small-ball and boundary audit artifacts."""

from pathlib import Path

from studies.privacy_refinement.a3_mechanism import candidate_rows, regressions, subgroup_metrics


def main() -> None:
    candidates = candidate_rows()
    candidates.to_csv("results/A3_mechanism_candidates.csv", index=False)
    subgroup_metrics(candidates).to_csv("results/A3_small_ball_metrics.csv", index=False)
    regressions(candidates).to_csv("results/A3_mechanism_regression.csv", index=False)
    print({"candidates": len(candidates)})


if __name__ == "__main__":
    main()
