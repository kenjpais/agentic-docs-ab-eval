#!/usr/bin/env python3
"""
Phase 7 Analysis — EVAL_PLAN.md
Paired mean comparison by case_id across conditions. Per-category and per-complexity breakdowns.
"""

import yaml
import json
import numpy as np
from pathlib import Path
from collections import defaultdict

RUNS_DIR = Path("eval/runs/agentic-docs-ab-eval")
DATASET_DIR = Path("eval/dataset")
METRICS = ["task_success", "code_correctness", "convention_adherence", "hallucination_check"]

BASELINE_RUNS = [f"baseline-run-{i}" for i in range(1, 6)]
TREATMENT_RUNS = [f"treatment-run-{i}" for i in range(1, 6)]
TREATMENT_V2_RUNS = [f"treatment-v2-run-{i}" for i in range(1, 6)]


def load_summary(run_id):
    path = RUNS_DIR / run_id / "summary.yaml"
    with open(path) as f:
        return yaml.safe_load(f)


def extract_per_case_scores(run_id, metric):
    s = load_summary(run_id)
    per_case = s.get("per_case", {})
    scores = {}
    for case_id, judges in per_case.items():
        if metric in judges:
            v = judges[metric]
            val = v.get("value") if isinstance(v, dict) else v
            if val is not None and isinstance(val, (int, float)):
                scores[case_id] = float(val)
    return scores


def load_annotations():
    annotations = {}
    for variant in ["baseline-flat", "treatment-flat"]:
        d = DATASET_DIR / variant
        if not d.exists():
            continue
        for case_dir in d.iterdir():
            if not case_dir.is_dir():
                continue
            ann_file = case_dir / "annotations.yaml"
            if ann_file.exists():
                with open(ann_file) as f:
                    ann = yaml.safe_load(f)
                annotations[case_dir.name] = ann
    return annotations


def aggregate_scores(runs, metric):
    """Return per-case mean across runs, plus flat list for overall stats."""
    all_case_scores = defaultdict(list)
    for run_id in runs:
        try:
            per_case = extract_per_case_scores(run_id, metric)
            for case_id, score in per_case.items():
                all_case_scores[case_id].append(score)
        except Exception as e:
            print(f"  Warning: could not load {run_id}/{metric}: {e}")
    case_means = {cid: np.mean(scores) for cid, scores in all_case_scores.items() if scores}
    flat = list(case_means.values())
    return case_means, flat


def compare(baseline_vals, treatment_vals):
    b = np.array(baseline_vals)
    t = np.array(treatment_vals)
    min_len = min(len(b), len(t))
    b, t = b[:min_len], t[:min_len]
    return {
        "baseline_mean": float(np.mean(b)),
        "baseline_sd": float(np.std(b, ddof=1)),
        "treatment_mean": float(np.mean(t)),
        "treatment_sd": float(np.std(t, ddof=1)),
        "delta": float(np.mean(t) - np.mean(b)),
    }


def per_category_analysis(annotations, baseline_runs, treatment_runs):
    categories = defaultdict(lambda: defaultdict(list))
    complexities = defaultdict(lambda: defaultdict(list))

    for metric in METRICS:
        b_case_means, _ = aggregate_scores(baseline_runs, metric)
        t_case_means, _ = aggregate_scores(treatment_runs, metric)

        for case_id, ann in annotations.items():
            cat = ann.get("category", "unknown")
            cplx = ann.get("complexity", "unknown")
            b_score = b_case_means.get(case_id)
            t_score = t_case_means.get(case_id)
            if b_score is not None and t_score is not None:
                categories[cat][metric].append((b_score, t_score))
                complexities[cplx][metric].append((b_score, t_score))

    results = {"by_category": {}, "by_complexity": {}}
    for cat, metric_data in categories.items():
        results["by_category"][cat] = {}
        for metric, pairs in metric_data.items():
            b_vals = [p[0] for p in pairs]
            t_vals = [p[1] for p in pairs]
            results["by_category"][cat][metric] = {
                "baseline_mean": float(np.mean(b_vals)),
                "treatment_mean": float(np.mean(t_vals)),
                "delta": float(np.mean(t_vals) - np.mean(b_vals)),
                "n": len(pairs),
            }

    for cplx, metric_data in complexities.items():
        results["by_complexity"][cplx] = {}
        for metric, pairs in metric_data.items():
            b_vals = [p[0] for p in pairs]
            t_vals = [p[1] for p in pairs]
            results["by_complexity"][cplx][metric] = {
                "baseline_mean": float(np.mean(b_vals)),
                "treatment_mean": float(np.mean(t_vals)),
                "delta": float(np.mean(t_vals) - np.mean(b_vals)),
                "n": len(pairs),
            }

    return results


def consulted_docs_summary(runs):
    """Return mean consulted_docs pass_rate across runs (0–1 scale)."""
    rates = []
    for run_id in runs:
        try:
            s = load_summary(run_id)
            cd = s.get("judges", {}).get("consulted_docs", {})
            if "pass_rate" in cd:
                rates.append(cd["pass_rate"])
        except Exception:
            pass
    return float(np.mean(rates)) if rates else None


def main():
    print("=" * 60)
    print("PHASE 7: ANALYSIS")
    print("=" * 60)

    annotations = load_annotations()
    print(f"\nLoaded annotations for {len(annotations)} cases")

    # Primary metrics — treatment-v1 vs baseline
    print("\n--- PRIMARY METRICS: Treatment-v1 vs Baseline ---")
    results_v1 = {}
    for metric in METRICS:
        b_case_means, _ = aggregate_scores(BASELINE_RUNS, metric)
        t_case_means, _ = aggregate_scores(TREATMENT_RUNS, metric)

        shared = sorted(set(b_case_means) & set(t_case_means))
        b_paired = [b_case_means[c] for c in shared]
        t_paired = [t_case_means[c] for c in shared]

        r = compare(b_paired, t_paired)
        results_v1[metric] = r

        direction = "treatment > baseline" if r["delta"] > 0 else "baseline > treatment"
        print(f"\n{metric}:")
        print(f"  baseline:    {r['baseline_mean']:.3f} ± {r['baseline_sd']:.3f}")
        print(f"  treatment:   {r['treatment_mean']:.3f} ± {r['treatment_sd']:.3f}")
        print(f"  delta:       {r['delta']:+.3f}  [{direction}]")
        print(f"  n cases:     {len(shared)}")

    # Primary metrics — treatment-v2 vs baseline
    print("\n" + "=" * 60)
    print("Treatment-v2 vs Baseline (guided AGENTS.md discovery)")
    print("=" * 60)
    results_v2 = {}
    for metric in METRICS:
        b_case_means, _ = aggregate_scores(BASELINE_RUNS, metric)
        t2_case_means, _ = aggregate_scores(TREATMENT_V2_RUNS, metric)

        shared = sorted(set(b_case_means) & set(t2_case_means))
        b_paired = [b_case_means[c] for c in shared]
        t2_paired = [t2_case_means[c] for c in shared]

        r = compare(b_paired, t2_paired)
        results_v2[metric] = r

        direction = "treatment-v2 > baseline" if r["delta"] > 0 else "baseline > treatment-v2"
        print(f"\n{metric}:")
        print(f"  baseline:     {r['baseline_mean']:.3f} ± {r['baseline_sd']:.3f}")
        print(f"  treatment-v2: {r['treatment_mean']:.3f} ± {r['treatment_sd']:.3f}")
        print(f"  delta:        {r['delta']:+.3f}  [{direction}]")
        print(f"  n cases:      {len(shared)}")

    # Per-category
    print("\n--- PER-CATEGORY BREAKDOWN ---")
    cat_results = per_category_analysis(annotations, BASELINE_RUNS, TREATMENT_V2_RUNS)
    for cat, metrics in sorted(cat_results["by_category"].items()):
        print(f"\n  {cat}:")
        for metric, v in metrics.items():
            print(f"    {metric}: baseline={v['baseline_mean']:.2f}, "
                  f"treatment-v2={v['treatment_mean']:.2f}, "
                  f"Δ={v['delta']:+.2f} (n={v['n']})")

    print("\n--- PER-COMPLEXITY BREAKDOWN ---")
    for cplx, metrics in sorted(cat_results["by_complexity"].items()):
        print(f"\n  {cplx}:")
        for metric, v in metrics.items():
            print(f"    {metric}: baseline={v['baseline_mean']:.2f}, "
                  f"treatment-v2={v['treatment_mean']:.2f}, "
                  f"Δ={v['delta']:+.2f} (n={v['n']})")

    # Verdict
    print("\n--- VERDICT ---")
    ts_delta = results_v2["task_success"]["delta"]
    if ts_delta > 0.05:
        print(f"Directional improvement: task_success delta = {ts_delta:+.3f} (treatment-v2 > baseline)")
    else:
        print(f"No clear improvement: task_success delta = {ts_delta:+.3f}")

    # Consulted docs
    print("\n--- CONSULTED_DOCS COVERAGE ---")
    cd_baseline = consulted_docs_summary(BASELINE_RUNS)
    cd_t1 = consulted_docs_summary(TREATMENT_RUNS)
    cd_t2 = consulted_docs_summary(TREATMENT_V2_RUNS)
    for label, rate in [("baseline", cd_baseline), ("treatment-v1", cd_t1), ("treatment-v2", cd_t2)]:
        rate_str = f"{rate:.1%}" if rate is not None else "N/A"
        print(f"  {label}: consulted_docs pass_rate = {rate_str}")
    if cd_t1 is not None and cd_t1 < 0.1:
        print("\n  Key finding: Treatment-v1 agents read near-zero agentic docs.")
        if cd_t2 is not None and cd_t2 > cd_t1:
            print(f"  Treatment-v2 (guided discovery) achieved {cd_t2:.1%} doc coverage.")

    # Save results
    out = {
        "primary_metrics_v1": results_v1,
        "primary_metrics_v2": results_v2,
        "per_category": cat_results["by_category"],
        "per_complexity": cat_results["by_complexity"],
        "consulted_docs": {
            "baseline": cd_baseline,
            "treatment_v1": cd_t1,
            "treatment_v2": cd_t2,
        },
    }
    out_path = Path("eval/runs/agentic-docs-ab-eval/phase7_results.json")
    with open(out_path, "w") as f:
        json.dump(out, f, indent=2)
    print(f"\nResults saved to {out_path}")


if __name__ == "__main__":
    main()
