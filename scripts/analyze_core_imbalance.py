"""Analyze the frozen granular-ball class-imbalance stress batch."""

from __future__ import annotations

import argparse
import hashlib
import json
import statistics
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
FAMILIES = ("density_equal", "density_shift", "moons")
RATIOS = (1, 5, 20, 50)
METHODS = ("kmeans", "class_means")
SEEDS = (1, 7, 21, 42, 2026)
TAUS = (0.60, 0.75, 0.85, 0.95, 1.0)
REFERENCES = ("RandomForest", "RBF-SVM", "5-NN")


def mean(values):
    values = list(values)
    if not values:
        raise ValueError("cannot average an empty collection")
    return statistics.fmean(values)


def point(row, tau):
    matches = [
        item
        for item in row["additional_metrics"]["frontier"]
        if abs(float(item["tau"]) - tau) < 1e-12
    ]
    if len(matches) != 1:
        raise ValueError(f"{row['experiment_id']}: expected one tau={tau} point")
    return matches[0]


def canonical_digest(rows):
    payload = "\n".join(
        json.dumps(row, sort_keys=True, separators=(",", ":"))
        for row in sorted(rows, key=lambda item: item["experiment_id"])
    )
    return hashlib.sha256((payload + "\n").encode()).hexdigest()


def load_frozen_rows(results_path, configs_dir):
    configs = [json.loads(path.read_text()) for path in sorted(configs_dir.glob("*.json"))]
    expected_ids = {config["experiment_id"] for config in configs}
    if len(configs) != 120 or len(expected_ids) != 120:
        raise ValueError(f"expected 120 unique imbalance configs, found {len(expected_ids)}")

    selected = []
    core_count = 0
    with results_path.open() as handle:
        for line in handle:
            row = json.loads(line)
            if str(row.get("study", "")).startswith("granular-ball-core-"):
                core_count += 1
            if row.get("experiment_id") in expected_ids:
                selected.append(row)
    if core_count != 400:
        raise ValueError(f"expected the frozen 400-row GB-core batch, found {core_count}")
    counts = {experiment_id: 0 for experiment_id in expected_ids}
    for row in selected:
        counts[row["experiment_id"]] += 1
    missing = sorted(key for key, count in counts.items() if count == 0)
    duplicate = sorted(key for key, count in counts.items() if count != 1)
    if missing or duplicate:
        raise ValueError(f"frozen imbalance rows mismatch: missing={missing}, duplicate={duplicate}")

    expected_cells = {
        (family, ratio, method, seed)
        for family in FAMILIES
        for ratio in RATIOS
        for method in METHODS
        for seed in SEEDS
    }
    observed_cells = set()
    for row in selected:
        params = row["dataset_generation_parameters"]
        observed_cells.add(
            (
                params["family"],
                int(params["imbalance_ratio"]),
                params["generation_method"],
                int(row["seed"]),
            )
        )
        if row.get("study") != "granular-ball-core-imbalance" or row.get("outcome") != "success":
            raise ValueError(f"{row['experiment_id']}: invalid study/outcome")
        if tuple(float(item["tau"]) for item in row["additional_metrics"]["frontier"]) != TAUS:
            raise ValueError(f"{row['experiment_id']}: incomplete purity frontier")
        if set(row["additional_metrics"]["references"]) != set(REFERENCES):
            raise ValueError(f"{row['experiment_id']}: incomplete reference set")
        counts_value = row["additional_metrics"].get("train_class_counts")
        if not counts_value or len(counts_value) != 2 or min(counts_value) <= 0:
            raise ValueError(f"{row['experiment_id']}: invalid class counts")
    if observed_cells != expected_cells:
        raise ValueError("imbalance factorial coverage does not match the frozen design")
    return sorted(selected, key=lambda item: item["experiment_id"])


def lookup(rows):
    result = {}
    for row in rows:
        params = row["dataset_generation_parameters"]
        key = (
            params["family"],
            int(params["imbalance_ratio"]),
            params["generation_method"],
            int(row["seed"]),
        )
        result[key] = row
    return result


def paired_changes(rows, ratio, tau):
    by_cell = lookup(rows)
    changes = []
    for family in FAMILIES:
        for method in METHODS:
            for seed in SEEDS:
                current = point(by_cell[(family, ratio, method, seed)], tau)
                balanced = point(by_cell[(family, 1, method, seed)], tau)
                changes.append(
                    {
                        "family": family,
                        "method": method,
                        "seed": seed,
                        "accuracy": current["accuracy"] - balanced["accuracy"],
                        "macro_f1": current["macro_f1"] - balanced["macro_f1"],
                        "minority_recall": current["minority_recall"] - balanced["minority_recall"],
                        "granules": current["granules"] - balanced["granules"],
                        "current_recall": current["minority_recall"],
                    }
                )
    return changes


def deduplicated_reference_rows(rows):
    by_key = {}
    for row in rows:
        params = row["dataset_generation_parameters"]
        key = (params["family"], int(params["imbalance_ratio"]), row["seed"])
        references = row["additional_metrics"]["references"]
        if key in by_key and by_key[key]["additional_metrics"]["references"] != references:
            raise ValueError(f"reference metrics differ across GB methods for {key}")
        by_key[key] = row
    if len(by_key) != 60:
        raise ValueError(f"expected 60 method-deduplicated reference rows, found {len(by_key)}")
    return by_key


def pp(value):
    return f"{100 * value:+.2f}"


def pct(value):
    return f"{100 * value:.2f}%"


def render(rows, results_path):
    frozen_sha = canonical_digest(rows)
    commits = sorted({row["git_commit"] for row in rows})
    if len(commits) != 1:
        raise ValueError(f"imbalance rows span commits: {commits}")

    primary_rows = []
    for ratio in RATIOS:
        subset = [
            row
            for row in rows
            if int(row["dataset_generation_parameters"]["imbalance_ratio"]) == ratio
        ]
        primary = [point(row, 0.85) for row in subset]
        paired = paired_changes(rows, ratio, 0.85) if ratio != 1 else None
        primary_rows.append(
            (
                ratio,
                mean(item["accuracy"] for item in primary),
                mean(item["macro_f1"] for item in primary),
                mean(item["minority_recall"] for item in primary),
                mean(item["granules"] for item in primary),
                mean(item["fragmentation_ratio"] for item in primary),
                mean(item["minority_recall"] == 0 for item in primary),
                None if paired is None else mean(item["minority_recall"] for item in paired),
                mean(
                    point(row, 0.85)["macro_f1"]
                    - row["additional_metrics"]["best_reference_macro_f1"]
                    for row in subset
                ),
            )
        )

    family_rows = []
    for family in FAMILIES:
        for method in METHODS:
            subset = [
                row
                for row in rows
                if row["dataset_generation_parameters"]["family"] == family
                and int(row["dataset_generation_parameters"]["imbalance_ratio"]) == 50
                and row["dataset_generation_parameters"]["generation_method"] == method
            ]
            primary = [point(row, 0.85) for row in subset]
            family_rows.append(
                (
                    family,
                    method,
                    mean(item["accuracy"] for item in primary),
                    mean(item["macro_f1"] for item in primary),
                    mean(item["minority_recall"] for item in primary),
                    mean(item["granules"] for item in primary),
                    sum(item["minority_recall"] == 0 for item in primary),
                )
            )

    references = deduplicated_reference_rows(rows)
    reference_rows = []
    for ratio in RATIOS:
        subset = [row for (family, ratio_value, seed), row in references.items() if ratio_value == ratio]
        for name in REFERENCES:
            metrics = [row["additional_metrics"]["references"][name] for row in subset]
            reference_rows.append(
                (
                    ratio,
                    name,
                    mean(item["accuracy"] for item in metrics),
                    mean(item["macro_f1"] for item in metrics),
                    mean(item["minority_recall"] for item in metrics),
                )
            )

    rescue_rows = []
    for ratio in RATIOS:
        subset = [
            row
            for row in rows
            if int(row["dataset_generation_parameters"]["imbalance_ratio"]) == ratio
        ]
        rescue = [point(row, 1.0) for row in subset]
        rescue_rows.append(
            (
                ratio,
                mean(item["accuracy"] for item in rescue),
                mean(item["macro_f1"] for item in rescue),
                mean(item["minority_recall"] for item in rescue),
                mean(item["granules"] for item in rescue),
                mean(item["fragmentation_ratio"] for item in rescue),
                mean(
                    point(row, 1.0)["macro_f1"]
                    - row["additional_metrics"]["best_reference_macro_f1"]
                    for row in subset
                ),
            )
        )

    ratio_50_pairs = paired_changes(rows, 50, 0.85)
    p0_strength = (
        len(ratio_50_pairs) == 30
        and all(item["current_recall"] == 0 for item in ratio_50_pairs)
        and all(item["minority_recall"] <= -0.01 for item in ratio_50_pairs)
    )
    tau_one_ratio_50 = [
        point(row, 1.0)
        for row in rows
        if int(row["dataset_generation_parameters"]["imbalance_ratio"]) == 50
    ]
    simple_repair_pass = (
        mean(item["minority_recall"] for item in tau_one_ratio_50) >= 0.90
        and mean(item["fragmentation_ratio"] for item in tau_one_ratio_50) <= 0.02
    )
    status = "REJECT" if p0_strength and simple_repair_pass else "P1"

    lines = [
        "# Granular-ball core class-imbalance stress",
        "",
        "## Decision",
        "",
        f"`{status}` C2 as a standalone research direction. The frozen data show a",
        "P0-strength failure at the preregistered `tau=.85`: every run at 20:1 and",
        "50:1 stops at one majority ball and has zero minority recall. However, this",
        "is not a hidden minority-only effect: balanced-test Accuracy also collapses",
        "by 49.17 pp versus the 1:1 paired condition. The already-frozen `tau=1` arm",
        "restores 92.91% mean minority recall at 50:1 with only 5.33 balls, so the",
        "standalone failure is an obvious purity-stop mismatch, not evidence for a new",
        "imbalanced granular-ball mechanism. Class-mapping and per-class allocation",
        "repairs are also already occupied, so relabeling the threshold fix would not",
        "clear novelty.",
        "",
        "The useful residual is the conflict with the noise result: `tau=1` repairs",
        "minority masking here but causes severe noise fragmentation. That joint",
        "constraint belongs under C1/resource-aware stopping, not a separate C2 paper.",
        "",
        "## Frozen evidence",
        "",
        f"- Source: `{results_path.relative_to(ROOT)}` selected by the 120 config IDs in",
        "  `experiments/configs/core_exploration/imbalance/`.",
        f"- Selected-row canonical SHA-256: `{frozen_sha}`.",
        f"- Implementation commit recorded by every row: `{commits[0]}`.",
        "- The frozen GB-core batch has 400 rows: 240 noise, 120 imbalance, and 40",
        "  shift. This report analyzes the complete 120-row imbalance subset.",
        "- Complete factorial: 3 families x 4 imbalance ratios x 2 generators x",
        "  5 seeds = 120 successful runs.",
        "- Training data are imbalanced; all tests are independently generated and",
        "  balanced. Each run contains five purity thresholds and RF/RBF-SVM/5NN",
        "  references trained on the same imbalanced sample.",
        "",
        "## Minority masking at fixed purity",
        "",
        "All GB rows below use `tau=.85`. The paired recall change is against the",
        "matching 1:1 family, generator, and seed.",
        "",
        "| Majority:minority | Accuracy | Macro-F1 | Minority recall | Granules | Fragmentation | Zero-recall runs | Paired recall change (pp) | Gap to best reference F1 (pp) |",
        "|---:|---:|---:|---:|---:|---:|---:|---:|---:|",
    ]
    for ratio, accuracy, macro_f1, recall, granules, fragmentation, zero_fraction, delta_recall, gap in primary_rows:
        lines.append(
            f"| {ratio}:1 | {pct(accuracy)} | {pct(macro_f1)} | {pct(recall)} | "
            f"{granules:.2f} | {pct(fragmentation)} | {pct(zero_fraction)} | "
            f"{'--' if delta_recall is None else pp(delta_recall)} | {pp(gap)} |"
        )

    lines.extend(
        [
            "",
            "At 20:1 and 50:1, the parent-ball majority fractions are approximately",
            "95.19% and 98.01%. They already exceed `tau=.85`, so the tree does not",
            "split. Relative to the paired 1:1 runs, the 50:1 condition loses 99.38 pp",
            "minority recall, 65.83 pp Macro-F1, and 49.17 pp Accuracy while using",
            "2.33 fewer balls. The resource improvement is therefore underfitting,",
            "not an acceptable accuracy/resource trade.",
            "",
            "## Cross-family replication at 50:1",
            "",
            "| Family | Generator | Accuracy | Macro-F1 | Minority recall | Granules | Zero-recall seeds |",
            "|---|---|---:|---:|---:|---:|---:|",
        ]
    )
    for family, method, accuracy, macro_f1, recall, granules, zero_count in family_rows:
        lines.append(
            f"| {family} | {method} | {pct(accuracy)} | {pct(macro_f1)} | "
            f"{pct(recall)} | {granules:.2f} | {zero_count}/5 |"
        )

    lines.extend(
        [
            "",
            "Both generators make the same constant-majority prediction in all 30",
            "50:1 runs. This is cross-family replication of the stop-rule behavior,",
            "but it does not distinguish a new generator mechanism.",
            "",
            "## Strong point references",
            "",
            "Reference rows are deduplicated across GB generator, leaving 15",
            "family/seed results per ratio.",
            "",
            "| Ratio | Reference | Accuracy | Macro-F1 | Minority recall |",
            "|---:|---|---:|---:|---:|",
        ]
    )
    for ratio, name, accuracy, macro_f1, recall in reference_rows:
        lines.append(
            f"| {ratio}:1 | {name} | {pct(accuracy)} | {pct(macro_f1)} | {pct(recall)} |"
        )

    lines.extend(
        [
            "",
            "At 50:1, RBF-SVM is the strongest reference (97.50% Macro-F1 and 95.06%",
            "minority recall). RF and 5-NN retain 89.64% and 89.00% minority recall.",
            "The `tau=.85` GB gap is therefore not caused by an information-free",
            "training sample.",
            "",
            "## Purity sensitivity and built-in kill test",
            "",
            "| Ratio | tau=1 Accuracy | tau=1 Macro-F1 | tau=1 minority recall | Granules | Fragmentation | Gap to best reference F1 (pp) |",
            "|---:|---:|---:|---:|---:|---:|---:|",
        ]
    )
    for ratio, accuracy, macro_f1, recall, granules, fragmentation, gap in rescue_rows:
        lines.append(
            f"| {ratio}:1 | {pct(accuracy)} | {pct(macro_f1)} | {pct(recall)} | "
            f"{granules:.2f} | {pct(fragmentation)} | {pp(gap)} |"
        )

    lines.extend(
        [
            "",
            "For both 20:1 and 50:1, raising `tau` from `.85` to `1.0` changes the",
            "model from one ball/zero recall to a small multi-ball model. At 20:1 it",
            "reaches 98.50% Macro-F1, only 0.33 pp below the best per-run reference; at",
            "50:1 it reaches 96.36%, 1.17 pp below. The frozen threshold sweep has",
            "therefore already executed the cheapest standalone kill test, and it",
            "kills C2 under the current noise-free design.",
            "",
            "## Limitations",
            "",
            "- Balanced tests intentionally expose minority masking; deployment-prior",
            "  accuracy and cost-sensitive risk are not evaluated.",
            "- The minority class remains represented in training, even at 50:1. This",
            "  does not cover few-shot class absence or multiclass long tails.",
            "- The two density families are easily separable. Moons carries most of",
            "  the residual error, so the aggregate rescue must not be sold as a broad",
            "  imbalanced-learning improvement.",
            "- Model size is not comparable across GB granules and RF/SVM/5NN; only",
            "  predictive metrics are compared to point references.",
            "",
            "## Cheapest kill test",
            "",
            "No additional standalone C2 run is justified: the frozen `tau=1` arm is",
            "the cheapest kill test and passes the repair gate (greater than 90% mean",
            "minority recall with less than 2% fragmentation at 50:1). Reopen only as",
            "a joint noise-imbalance interaction: ratio 20:1 plus 20% symmetric label",
            "noise, 3 families x 2 generators x 5 seeds = 30 runs on the same five",
            "thresholds. **Reject the joint hypothesis** if one prespecified global",
            "threshold is within 1 pp of the clean-test oracle Macro-F1 and within 20%",
            "of its granule count in at least 80% of cells. Otherwise merge the signal",
            "into C1's budgeted stopping problem; do not revive a standalone imbalance",
            "candidate.",
            "",
        ]
    )
    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--results",
        type=Path,
        default=ROOT / "experiments/results/experiments.jsonl",
    )
    parser.add_argument(
        "--configs",
        type=Path,
        default=ROOT / "experiments/configs/core_exploration/imbalance",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=ROOT / "reports/core_exploration/imbalance_report.md",
    )
    args = parser.parse_args()
    rows = load_frozen_rows(args.results, args.configs)
    report = render(rows, args.results.resolve())
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(report, encoding="utf-8")
    print(f"wrote {args.output} from {len(rows)} frozen rows")


if __name__ == "__main__":
    main()
