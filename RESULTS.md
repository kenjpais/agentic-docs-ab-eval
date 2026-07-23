# A/B Evaluation Results: Agentic Documentation Impact

**Campaign:** agentic-docs-ab-eval · **Date:** 2026-07 · **Runs:** 15 (5 baseline + 5 treatment-v1 + 5 treatment-v2)

---

## Question

Do generated agentic docs (AGENTS.md + agentic/ tree) improve AI coding agent performance on
Kubernetes operator tasks beyond a CLAUDE.md-only baseline?

---

## Verdict: Null result — H₀ not rejected

No statistically significant improvement was detected across any primary metric for either
treatment condition. Agentic docs as generated and deployed in this campaign did not reliably
lift agent performance. The treatment-v2 condition showed directionally better pairwise
preference (40.7% win rate), but this did not reach the pre-registered 55% threshold and
no metric passed the Wilcoxon p < 0.05 gate.

---

## Primary Metrics

All scores on a 1–5 scale. Delta = Treatment-v2 minus Baseline.

| Metric | Baseline (n=55) | Treatment-v1 (n=55) | Treatment-v2 (n=55) | Delta (v2) | Wilcoxon p | Cohen's d |
|--------|-----------------|---------------------|---------------------|------------|------------|-----------|
| task_success | 3.982 ± 0.850 | 3.855 ± 0.780 | 3.909 ± 0.800 | −0.073 | 0.668 | −0.092 |
| code_correctness | 3.873 ± 0.747 | 3.818 ± 0.696 | 3.855 ± 0.780 | −0.018 | 0.563 | −0.025 |
| convention_adherence | 3.727 ± 0.932 | 3.618 ± 0.892 | 3.818 ± 0.964 | **+0.091** | 0.656 | +0.100 |
| hallucination_check | 3.182 ± 0.841 | 3.109 ± 0.737 | 3.164 ± 0.714 | −0.018 | 0.500 | −0.026 |

*Statistical tests: Wilcoxon signed-rank (paired by task, n=11 pairs per run × 5 runs = 55 pairs)*

**Pre-registered thresholds: task_success ≥ 3.0 mean (all met), Wilcoxon p < 0.05 (none met)**

---

## IDV (Incremental Documentation Value)

IDV = mean(OES_treatment) − mean(OES_baseline), where OES is a weighted composite score:

```
OES = 0.30 × (task_success − 1)/4
    + 0.25 × (code_correctness − 1)/4
    + 0.20 × (convention_adherence − 1)/4
    + 0.15 × hallucination_check (0/1)
    + 0.10 × efficiency (0/1)
```

| Condition | IDV | Threshold | Meets? |
|-----------|-----|-----------|--------|
| Treatment-v1 vs Baseline | −0.031 | > 0.10 | No |
| Treatment-v2 vs Baseline | −0.005 | > 0.10 | No |

Treatment-v1: negative IDV — docs present but not consulted, slight performance drag.
Treatment-v2: effectively zero IDV — guided discovery partially mitigated the drag.

---

## Pairwise Comparisons (LLM judge, head-to-head per case)

| Condition | Treatment wins | Baseline wins | Ties | Win rate (all) | Win rate (excl. ties) |
|-----------|---------------|---------------|------|----------------|-----------------------|
| Treatment-v1 | 5 | 7 | 43 | 9.1% | 41.7% |
| Treatment-v2 | 22 | 3 | 29 | **40.7%** | **88.0%** |

**Pre-registered threshold: ≥ 55% overall win rate. Neither condition met it.**

The jump from v1 (9.1%) to v2 (40.7%) is primarily attributable to the explicit AGENTS.md
read instruction in the treatment-v2 system prompt, not to the docs themselves being better.

---

## Secondary Findings

### Doc Consultation Rate

| Condition | consulted_docs pass rate (≥50% expected docs) |
|-----------|-----------------------------------------------|
| Baseline | 100% (reading non-agentic docs in repo) |
| Treatment-v1 | 0% — agent never opened agentic docs without prompting |
| Treatment-v2 | 45.5% — guided discovery, below 50% threshold |

Treatment-v1 failed entirely because the agent had no incentive to discover AGENTS.md.
Treatment-v2 improved this to 45.5% through an explicit system prompt instruction,
just below the pre-registered 50% minimum.

### Per-Repository (task_success, Treatment-v2 vs Baseline)

| Repository | Baseline | Treatment-v2 | Delta |
|------------|----------|--------------|-------|
| cert-manager-operator | 4.080 ± 0.862 | 3.840 ± 0.688 | −0.240 |
| multiarch-tuning-operator | 3.900 ± 0.845 | 3.967 ± 0.890 | +0.067 |

cert-manager tasks saw regression under treatment. Likely confound: cert-manager
has no CLAUDE.md in upstream, making the baseline arguably harder, while the treatment
agent spent time reading agentic docs that partially overlapped with what the baseline
would have reasoned from code inspection. Also note the treatment system prompt added
friction for already-clear tasks.

### Per-Complexity (task_success, Treatment-v2 vs Baseline)

| Complexity | Baseline | Treatment-v2 | Delta | n tasks |
|------------|----------|--------------|-------|---------|
| Low | 5.000 | 4.000 | −1.000 | 1 |
| Medium | 3.960 | 3.800 | −0.160 | 5 |
| High | 3.800 | 4.000 | **+0.200** | 5 |

The hypothesis that docs help more for high-complexity tasks receives directional
support: only high-complexity tasks showed a positive delta. However, n=5 tasks × 5 runs
= 25 pairs — insufficient for a reliable Wilcoxon test (requires n ≥ 8–10 with detectable effect).

### Per-Category (task_success, Treatment-v2 vs Baseline)

| Category | Baseline | Treatment-v2 | Delta | n tasks |
|----------|----------|--------------|-------|---------|
| api-change | 3.933 | 4.000 | +0.067 | 3 |
| architecture | 4.050 | 4.050 | 0.000 | 4 |
| observability | 4.900 | 4.500 | −0.400 | 2 |
| security | 3.000 | 3.000 | 0.000 | 1 |
| test-writing | 3.000 | 2.800 | −0.200 | 1 |

Observability tasks showed the largest regression. These tasks (PrometheusRule YAML,
Prometheus counter addition) are relatively self-contained — the agent benefited less
from architectural docs and the overhead of reading them hurt more than it helped.

---

## Efficiency Judge

All 15 runs × all 11 cases scored 0 (False) on efficiency.

- Treatment-v1 threshold: > 40 turns or > $3 per run → failed (128 turns, $8.98 per run)
- Treatment-v2 threshold: > 200 turns or > $15 per run → still failed (same underlying data)

The efficiency judge as configured measures total run cost, not per-case cost. All conditions
failed because the eval harness ran all 11 cases in a single session. This judge produced
zero signal and zero contribution to OES for all conditions. It should be redesigned
(per-case budget) before being used in future campaigns.

---

## Interpretation

### What the data says

1. **Agentic docs alone are not enough**: With no explicit instruction to read them (v1),
   agents ignored the agentic/ directory entirely. The docs might as well not exist.

2. **Guided discovery closes some of the gap**: Telling the agent to read AGENTS.md first
   (v2) raised the pairwise win rate from 9.1% to 40.7%, but still didn't lift absolute
   scores. The agent read the docs but the information didn't translate to meaningfully
   better code.

3. **High-complexity tasks are the best candidate**: +0.200 delta on high-complexity tasks
   is the only positive signal that aligns with the hypothesis. These are the tasks (adding
   a fifth execution mode, wiring an optional informer) where architectural knowledge matters
   most and where the agent would otherwise have to infer conventions from code inspection.

4. **cert-manager may not be a good eval target without CLAUDE.md**: The asymmetry
   (cert-manager has no CLAUDE.md; multiarch does) inflated baseline performance for
   cert-manager tasks. Future campaigns should either add a CLAUDE.md stub to cert-manager
   baseline or limit to repos with consistent baselines.

### What the data does not say

- This is not evidence that agentic docs are *worse* than no docs. The effect sizes are
  negligible (d < 0.2) and not statistically distinguishable from noise.
- This is not a test of human-authored docs. All agentic docs were generated by
  /create-agentic-docs. Higher-quality or more targeted docs might behave differently.
- This is not a test of docs in production use. The harness ran the agent with a
  constrained prompt and read-only permissions; real developer workflows differ.

---

## Decision vs Thresholds

| Metric | Pre-registered threshold | Actual (v2) | Pass? |
|--------|--------------------------|-------------|-------|
| IDV | > 0.10 | −0.005 | **No** |
| Pairwise win rate | ≥ 0.55 | 0.407 | **No** |
| Wilcoxon p (task_success) | < 0.05 | 0.668 | **No** |
| task_success mean | ≥ 3.0 | 3.909 | Yes (trivially) |
| convention_adherence mean | ≥ 3.0 | 3.818 | Yes (trivially) |
| hallucination_check mean | ≥ 3.0 | 3.164 | Yes (trivially) |
| consulted_docs pass rate | ≥ 0.50 | 0.455 | **No** |

**Recommendation: Do not ship agentic docs as a primary quality intervention on this evidence.**
A targeted follow-up focused on high-complexity tasks with explicit agent workflows and
human-authored docs is warranted before a shipping decision.

---

## Recommended Next Steps

1. **Redesign the doc discovery mechanism**: Treatment-v2's system prompt instruction is
   a patch. A better design integrates AGENTS.md reading into the agent's task loop
   (e.g., via CLAUDE.md `always_read` directives or a skill that pre-populates context).

2. **Focus on high-complexity tasks**: Run a dedicated campaign on high-complexity tasks
   only (n ≥ 15 tasks, 5 runs) to get reliable power at the observed effect size (+0.20).

3. **Fix the efficiency judge**: Replace per-run cost check with per-case budget tracking.
   Currently produces zero signal for all conditions.

4. **Align baseline conditions**: Add a CLAUDE.md stub to cert-manager-operator baseline
   or remove it from the evaluation set until upstream adds one.

5. **Ablation studies**: Test the six ablation conditions from EVAL_PLAN.md Phase 6
   (design-only, testing-only, ops-only) to identify which doc categories add the most
   value for specific task types.

---

## Caveats

- LLM judges (claude-opus-4-6) evaluated outputs from the same model family. Self-assessment
  bias may suppress signal (judge may give similar scores to similar models regardless of quality).
- Sample size: 11 tasks × 5 runs = 55 pairs. Designed for 80% power at d=0.5 (medium effect).
  Observed effects (d ≈ 0.10) would require n ≈ 800 pairs for 80% power.
- Tasks are synthetic. Real PRs involve upstream review, CI failures, and iterative changes
  not captured here.
- Generated docs, not human-authored. Quality scores (84–85/100) are self-assessed by
  the same model that generated the docs.
- The CLAUDE.md asymmetry between repos is a confound. Results for cert-manager-operator
  should be interpreted separately from multiarch-tuning-operator.
- All efficiency checks failed (design flaw in judge, not agent regression).

---

*Full data: metrics.csv · Environment: REPRO_MANIFEST.yaml · Statistical detail: eval/runs/agentic-docs-ab-eval/phase7_v2_results.json*
