"""Run the strict A3 cross-release attack-validity gate."""

from studies.privacy_refinement.a3_strict import run_validity


def main() -> None:
    result = run_validity()
    result.to_csv("results/A3_attack_validity.csv", index=False)
    print({"rows": len(result)})


if __name__ == "__main__":
    main()
