"""Aggregate campaign v1 without promoting observations to hypotheses."""

import collections, csv, json, statistics
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]

def main():
    records=[json.loads(line) for line in (ROOT/"experiments/results/experiments.jsonl").read_text().splitlines() if '"fsv1-' in line]
    if len(records)!=72: raise SystemExit(f"expected 72 campaign records, found {len(records)}")
    grouped=collections.defaultdict(list)
    for r in records:
        trial=int(r["experiment_id"].split("-")[1][1:]); method="adaptive" if "adaptive" in r["algorithm"] else "original"
        grouped[trial,method].append(r)
    rows=[]
    for trial in range(12):
        config=json.loads(next((ROOT/"experiments/configs/failure_search/campaign_v1").glob(f"fsv1-t{trial:03d}-*.json")).read_text())
        p=config["dataset_generation_parameters"]
        for method in ("original","adaptive"):
            rs=grouped[trial,method]
            rows.append({"trial":trial,"family":p["family"],"method":method,"ambient_dimension":p["ambient_dimension"],
                         "label_noise":p["label_noise"],"noise_rate":p["noise_rate"],"outlier_rate":p["outlier_rate"],
                         "mean_accuracy":statistics.mean(r["accuracy"] for r in rs),
                         "std_accuracy":statistics.pstdev(r["accuracy"] for r in rs),
                         "mean_reference_accuracy":statistics.mean(r["additional_metrics"]["reference_accuracy"] for r in rs),
                         "mean_accuracy_gap":statistics.mean(r["additional_metrics"]["accuracy_gap"] for r in rs),
                         "mean_failure_score":statistics.mean(r["additional_metrics"]["failure_score"] for r in rs),
                         "std_failure_score":statistics.pstdev(r["additional_metrics"]["failure_score"] for r in rs),
                         "mean_granules":statistics.mean(r["granule_count"] for r in rs),
                         "mean_uncertain_ratio":statistics.mean(r["uncertain_sample_ratio"] for r in rs)})
    out=ROOT/"counterexamples/discovered_cases/campaign_v1_summary.csv"
    with out.open("w",encoding="utf-8",newline="") as h:
        w=csv.DictWriter(h,fieldnames=list(rows[0])); w.writeheader(); w.writerows(rows)
    by={(r['trial'],r['method']):r for r in rows}
    report=["# Counterexample report","","## Campaign v1","",
            "The first bounded random search completed 72/72 runs: 12 parameter regions × two author GBC generators × seeds 1/7/21. Random forest used the identical train/test split and scaling. This is exploration-pool evidence only.","",
            "| Trial | Family | d | Original gap | Adaptive gap | Original failure ratio | Adaptive failure ratio |","|---:|---|---:|---:|---:|---:|---:|"]
    for t in range(12):
        o,a=by[t,'original'],by[t,'adaptive']; report.append(f"| {t:03d} | {o['family']} | {o['ambient_dimension']} | {o['mean_accuracy_gap']:+.3f} | {a['mean_accuracy_gap']:+.3f} | {o['mean_failure_score']:.2f} | {a['mean_failure_score']:.2f} |")
    report += ["","## Observations, not hypotheses","",
               "1. **Common high-dimensional XOR weakness (replication candidate).** At d=100, both original and adaptive GBC trail the reference across the three-seed aggregate: gaps −0.069 and −0.050; failure ratios 1.46 and 1.33. This is the clearest common signal in v1, but it still needs new XOR generators and more seeds.",
               "2. **Original-specific high-dimensional moons weakness.** Original trails by −0.047 with failure ratio 2.07, while adaptive leads by +0.019. This argues against calling curved manifolds a family-wide failure from this campaign.",
               "3. **Adaptive-specific imbalanced-density weakness.** Adaptive trails by −0.086 while original is roughly tied (+0.006). Random-center/overlap behavior is a candidate explanation, not yet evidence.",
               "4. **Spirals and varying density show smaller common gaps.** Both methods trail on these trials, but failure ratios are only 1.13–1.25 and one parameter draw is insufficient.",
               "5. **The ratio objective is unstable near a perfect reference.** Multimodal trial 009 produces an original mean failure ratio 3.17 even though mean accuracy is 0.997 and mean gap is positive. Future ranking must combine absolute gap and a denominator floor; ratio alone can manufacture a dramatic 'failure'.","",
               "## Promotion decision","",
               "No entry is promoted to a research hypothesis. High-dimensional XOR advances to targeted replication. Moons and imbalanced-density signals advance as method-specific red-team cases. Trial 009 is primarily a metric counterexample.","",
               "## Next experiment","",
               "Run a targeted grid over XOR ambient dimension {2,5,10,20,50,100,500}, overlap, rotation/projection, and five required seeds; add SVM/KNN and the S3WD structure where applicable. Rank by absolute accuracy gap first and use loss ratio only when reference loss exceeds a declared floor."]
    (ROOT/"reports/counterexample_report.md").write_text("\n".join(report)+"\n",encoding="utf-8")
    catalog=["# Failure catalog","","Status levels: `observation`, `replicated`, `cross-method`, `research-hypothesis`.","",
             "## O-001 — High-dimensional XOR common weakness","","- Status: `observation` (cross-method within one generator/parameter draw; not yet `cross-method` catalog status)","- Evidence: campaign v1 trial 003, experiments `fsv1-t003-*`, seeds 1/7/21.","- Result: original gap −0.069; adaptive gap −0.050 versus random forest.","- Alternative explanations: axis/projection interaction, reference inductive bias, hyperparameter mismatch, single generator draw.","- Required replication: dimension/overlap grid, rotated XOR, five seeds, additional references.","",
             "## O-002 — Method-specific split between moons and imbalanced density","","- Status: `observation`.","- Evidence: trials 001 and 011.","- Result: adaptive repairs the original moons gap, but adaptive alone degrades on imbalanced density.","- Interpretation: fixed and adaptive rules move failure regions rather than uniformly shrinking them; causal mechanism unverified.","",
             "## M-001 — FailureScore denominator pathology","","- Status: `replicated` as an arithmetic property; scientific consequence requires policy change.","- Evidence: trial 009 has near-perfect reference accuracy, causing ratios up to 9.33 while absolute GBC accuracy remains near 1.","- Action: require absolute-gap reporting and a minimum reference-loss floor before ratio ranking."]
    (ROOT/"counterexamples/failure_catalog.md").write_text("\n".join(catalog)+"\n",encoding="utf-8")
    print(f"Wrote {len(rows)} aggregate rows; XOR promoted only to targeted replication.")

if __name__=="__main__": main()
