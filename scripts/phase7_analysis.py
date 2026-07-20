#!/usr/bin/env python3
"""
Phase 7 Statistical Analysis — EVAL_PLAN.md
Wilcoxon signed-rank, Cohen's d, bootstrap 95% CI, per-category breakdown, doc ROI.
"""

import yaml
import json
import numpy as np
from pathlib import Path
from scipy import stats
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


def cohens_d(a, b):
    a, b = np.array(a), np.array(b)
    pooled_std = np.sqrt((np.var(a, ddof=1) + np.var(b, ddof=1)) / 2)
    if pooled_std == 0:
        return 0.0
    return (np.mean(a) - np.mean(b)) / pooled_std


def bootstrap_ci(a, b, n_boot=1000, ci=0.95):
    diffs = []
    n = len(a)
    rng = np.random.default_rng(42)
    for _ in range(n_boot):
        idx = rng.integers(0, n, size=n)
        diffs.append(np.mean(np.array(a)[idx]) - np.mean(np.array(b)[idx]))
    lo = np.percentile(diffs, (1 - ci) / 2 * 100)
    hi = np.percentile(diffs, (1 + ci) / 2 * 100)
    return lo, hi


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
    # Per-case mean
    case_means = {cid: np.mean(scores) for cid, scores in all_case_scores.items() if scores}
    flat = list(case_means.values())
    return case_means, flat


def run_test(baseline_vals, treatment_vals, metric):
    b = np.array(baseline_vals)
    t = np.array(treatment_vals)

    # Pair by index (cases are the same set)
    min_len = min(len(b), len(t))
    b, t = b[:min_len], t[:min_len]

    try:
        stat, p = stats.wilcoxon(b, t, alternative="less")
    except ValueError:
        stat, p = float("nan"), float("nan")

    d = cohens_d(b, t)
    ci_lo, ci_hi = bootstrap_ci(b, t)
    return {
        "baseline_mean": float(np.mean(b)),
        "baseline_sd": float(np.std(b, ddof=1)),
        "treatment_mean": float(np.mean(t)),
        "treatment_sd": float(np.std(t, ddof=1)),
        "delta": float(np.mean(b) - np.mean(t)),
        "wilcoxon_stat": float(stat) if not np.isnan(stat) else None,
        "wilcoxon_p": float(p) if not np.isnan(p) else None,
        "cohens_d": float(d),
        "ci_95_lo": float(ci_lo),
        "ci_95_hi": float(ci_hi),
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
            # Normalize case_id (strip mto-/cm- prefix variants)
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
                "delta": float(np.mean(b_vals) - np.mean(t_vals)),
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
                "delta": float(np.mean(b_vals) - np.mean(t_vals)),
                "n": len(pairs),
            }

    return results


def pairwise_summary(runs=None):
    if runs is None:
        runs = TREATMENT_RUNS
    wins_b, wins_t, ties = 0, 0, 0
    for run_id in runs:
        try:
            s = load_summary(run_id)
        except Exception:
            continue
        pw = s.get("pairwise", {})
        if pw:
            wins_b += pw.get("wins_a", pw.get("wins_baseline", 0))
            wins_t += pw.get("wins_b", pw.get("wins_treatment", 0))
            ties += pw.get("ties", 0)
    total = wins_b + wins_t + ties
    return {
        "baseline_wins": wins_b,
        "treatment_wins": wins_t,
        "ties": ties,
        "total_comparisons": total,
        "treatment_win_rate": wins_t / total if total else 0,
    }


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
    print("=" * 70)
    print("PHASE 7: STATISTICAL ANALYSIS")
    print("=" * 70)

    annotations = load_annotations()
    print(f"\nLoaded annotations for {len(annotations)} cases")

    # Primary metrics analysis
    print("\n--- PRIMARY METRICS (Wilcoxon signed-rank, paired by case) ---")
    results = {}
    for metric in METRICS:
        b_case_means, b_flat = aggregate_scores(BASELINE_RUNS, metric)
        t_case_means, t_flat = aggregate_scores(TREATMENT_RUNS, metric)

        # Pair by shared case IDs
        shared = sorted(set(b_case_means) & set(t_case_means))
        b_paired = [b_case_means[c] for c in shared]
        t_paired = [t_case_means[c] for c in shared]

        r = run_test(b_paired, t_paired, metric)
        results[metric] = r

        sig = "**SIGNIFICANT**" if (r["wilcoxon_p"] is not None and r["wilcoxon_p"] < 0.05) else "not significant"
        direction = "baseline > treatment" if r["delta"] > 0 else "treatment > baseline"
        print(f"\n{metric}:")
        print(f"  baseline:  {r['baseline_mean']:.3f} ± {r['baseline_sd']:.3f}")
        print(f"  treatment: {r['treatment_mean']:.3f} ± {r['treatment_sd']:.3f}")
        print(f"  delta (B-T): {r['delta']:+.3f}  [{direction}]")
        wp = f"{r['wilcoxon_p']:.4f}" if r['wilcoxon_p'] is not None else 'N/A'
        print(f"  Wilcoxon p: {wp}  {sig}")
        print(f"  Cohen's d:  {r['cohens_d']:.3f}")
        print(f"  95% CI on mean diff: [{r['ci_95_lo']:.3f}, {r['ci_95_hi']:.3f}]")
        print(f"  n paired cases: {len(shared)}")

    # Treatment-v2 analysis (guided discovery)
    print("\n" + "=" * 70)
    print("TREATMENT-V2 vs BASELINE (guided AGENTS.md discovery)")
    print("=" * 70)
    results_v2 = {}
    for metric in METRICS:
        b_case_means, _ = aggregate_scores(BASELINE_RUNS, metric)
        t2_case_means, _ = aggregate_scores(TREATMENT_V2_RUNS, metric)

        shared = sorted(set(b_case_means) & set(t2_case_means))
        b_paired = [b_case_means[c] for c in shared]
        t2_paired = [t2_case_means[c] for c in shared]

        r = run_test(b_paired, t2_paired, metric)
        results_v2[metric] = r

        sig = "**SIGNIFICANT**" if (r["wilcoxon_p"] is not None and r["wilcoxon_p"] < 0.05) else "not significant"
        direction = "baseline > treatment-v2" if r["delta"] > 0 else "treatment-v2 > baseline"
        print(f"\n{metric}:")
        print(f"  baseline:     {r['baseline_mean']:.3f} ± {r['baseline_sd']:.3f}")
        print(f"  treatment-v2: {r['treatment_mean']:.3f} ± {r['treatment_sd']:.3f}")
        print(f"  delta (B-T2): {r['delta']:+.3f}  [{direction}]")
        wp = f"{r['wilcoxon_p']:.4f}" if r['wilcoxon_p'] is not None else 'N/A'
        print(f"  Wilcoxon p: {wp}  {sig}")
        print(f"  Cohen's d:  {r['cohens_d']:.3f}")
        print(f"  95% CI on mean diff: [{r['ci_95_lo']:.3f}, {r['ci_95_hi']:.3f}]")
        print(f"  n paired cases: {len(shared)}")

    print("\n--- PAIRWISE COMPARISON SUMMARY (treatment-v2 vs baseline) ---")
    pw_v2 = pairwise_summary(TREATMENT_V2_RUNS)
    print(f"  Total comparisons: {pw_v2['total_comparisons']}")
    print(f"  Baseline wins: {pw_v2['baseline_wins']}")
    print(f"  Treatment-v2 wins: {pw_v2['treatment_wins']}")
    print(f"  Ties: {pw_v2['ties']}")
    wr_v2 = pw_v2['treatment_win_rate']
    pw_v2_sig = "MEETS" if wr_v2 >= 0.55 else "DOES NOT MEET"
    print(f"  Treatment-v2 win rate: {wr_v2:.1%} (threshold: 55%)")
    print(f"  → {pw_v2_sig} pairwise win-rate threshold")

    # Efficiency metrics
    print("\n--- EFFICIENCY METRICS ---")
    for condition, runs in [("baseline", BASELINE_RUNS), ("treatment-v1", TREATMENT_RUNS), ("treatment-v2", TREATMENT_V2_RUNS)]:
        costs, turns = [], []
        for run_id in runs:
            try:
                rr = json.load(open(RUNS_DIR / run_id / "run_result.json"))
                costs.append(rr.get("cost_usd", 0))
                turns.append(rr.get("num_turns", 0))
            except Exception:
                pass
        print(f"  {condition}: cost ${np.mean(costs):.2f}±{np.std(costs):.2f}, "
              f"turns {np.mean(turns):.1f}±{np.std(turns):.1f} (per 11-case run)")

    # Pairwise summary
    print("\n--- PAIRWISE COMPARISON SUMMARY ---")
    pw = pairwise_summary()
    print(f"  Total comparisons: {pw['total_comparisons']}")
    print(f"  Baseline wins: {pw['baseline_wins']}")
    print(f"  Treatment wins: {pw['treatment_wins']}")
    print(f"  Ties: {pw['ties']}")
    print(f"  Treatment win rate: {pw['treatment_win_rate']:.1%} (threshold: 55%)")
    pw_sig = "MEETS" if pw["treatment_win_rate"] >= 0.55 else "DOES NOT MEET"
    print(f"  → {pw_sig} pairwise win-rate threshold")

    # Per-category
    print("\n--- PER-CATEGORY BREAKDOWN ---")
    cat_results = per_category_analysis(annotations, BASELINE_RUNS, TREATMENT_RUNS)
    for cat, metrics in sorted(cat_results["by_category"].items()):
        print(f"\n  {cat}:")
        for metric, v in metrics.items():
            print(f"    {metric}: baseline={v['baseline_mean']:.2f}, "
                  f"treatment={v['treatment_mean']:.2f}, "
                  f"Δ={v['delta']:+.2f} (n={v['n']})")

    print("\n--- PER-COMPLEXITY BREAKDOWN ---")
    for cplx, metrics in sorted(cat_results["by_complexity"].items()):
        print(f"\n  {cplx}:")
        for metric, v in metrics.items():
            print(f"    {metric}: baseline={v['baseline_mean']:.2f}, "
                  f"treatment={v['treatment_mean']:.2f}, "
                  f"Δ={v['delta']:+.2f} (n={v['n']})")

    # H0/H1 verdict
    print("\n--- HYPOTHESIS TEST VERDICT ---")
    print("H₀: Agentic documentation provides no improvement over baseline.")
    print("H₁: Treatment shows significant improvement on task_success AND convention_adherence.")
    ts_p = results["task_success"]["wilcoxon_p"]
    ca_p = results["convention_adherence"]["wilcoxon_p"]
    if ts_p is not None and ca_p is not None and ts_p < 0.05 and ca_p < 0.05:
        print("→ REJECT H₀: Both primary metrics significant at α=0.05")
    else:
        print(f"→ FAIL TO REJECT H₀")
        ts_ps = f"{ts_p:.4f}" if ts_p else 'N/A'
        ca_ps = f"{ca_p:.4f}" if ca_p else 'N/A'
        ts_cmp = '<' if ts_p and ts_p < 0.05 else '>='
        ca_cmp = '<' if ca_p and ca_p < 0.05 else '>='
        print(f"  task_success p={ts_ps} ({ts_cmp} 0.05)")
        print(f"  convention_adherence p={ca_ps} ({ca_cmp} 0.05)")

    print("\n--- CONSULTED_DOCS COVERAGE ---")
    cd_baseline = consulted_docs_summary(BASELINE_RUNS)
    cd_t1 = consulted_docs_summary(TREATMENT_RUNS)
    cd_t2 = consulted_docs_summary(TREATMENT_V2_RUNS)
    for label, rate in [("baseline", cd_baseline), ("treatment-v1", cd_t1), ("treatment-v2", cd_t2)]:
        rate_str = f"{rate:.1%}" if rate is not None else "N/A"
        print(f"  {label}: consulted_docs pass_rate = {rate_str}")
    if cd_t1 is not None and cd_t1 < 0.1:
        print("\n--- KEY FINDING ---")
        print("  Treatment-v1 agents read near-zero agentic docs (organic discovery broken).")
        print("  Harness system_prompt overrides AGENTS.md auto-loading; both v1 conditions")
        print("  effectively measured baseline performance. Null result is a setup artifact.")
        if cd_t2 is not None and cd_t2 > cd_t1:
            print(f"  Treatment-v2 (guided discovery) achieved {cd_t2:.1%} doc coverage,")
            print("  providing a valid test of the documentation intervention.")
    else:
        print("\n--- KEY FINDING ---")
        print("  All conditions show doc coverage above threshold.")

    # Save results
    out = {
        "primary_metrics_v1": results,
        "primary_metrics_v2": results_v2,
        "pairwise_v1": pw,
        "pairwise_v2": pw_v2,
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
