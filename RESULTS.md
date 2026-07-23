# A/B Evaluation Results: Agentic Documentation Impact

**Campaign:** agentic-docs-ab-eval · **Date:** 2026-07 · **Runs:** 15 (5 baseline + 5 treatment-v1 + 5 treatment-v2)

---

## Question

Do generated agentic docs (AGENTS.md + agentic/ tree) improve AI coding agent performance on
Kubernetes operator tasks beyond a CLAUDE.md-only baseline?

---

## Verdict: No clear improvement detected

Neither treatment condition produced a meaningful lift over baseline. Treatment-v2 (guided
discovery) performed directionally better than treatment-v1, but absolute scores were
essentially unchanged from baseline across all metrics.

---

## Scores

All scores on a 1–5 scale, mean ± std, n=55 per condition (11 tasks × 5 runs).

| Metric | Baseline | Treatment-v1 | Treatment-v2 | Delta (v2) |
|--------|----------|-------------|--------------|------------|
| task_success | 3.982 ± 0.850 | 3.855 ± 0.780 | 3.909 ± 0.800 | −0.073 |
| code_correctness | 3.873 ± 0.747 | 3.818 ± 0.696 | 3.855 ± 0.780 | −0.018 |
| convention_adherence | 3.727 ± 0.932 | 3.618 ± 0.892 | 3.818 ± 0.964 | **+0.091** |
| hallucination_check | 3.182 ± 0.841 | 3.109 ± 0.737 | 3.164 ± 0.714 | −0.018 |

---

## Doc Consultation Rate

| Condition | Pass rate (≥50% expected docs read) |
|-----------|-------------------------------------|
| Baseline | 100% (reading non-agentic docs in repo) |
| Treatment-v1 | 0% — agent never opened agentic docs without prompting |
| Treatment-v2 | 45.5% — guided discovery, just below 50% threshold |

Treatment-v1 failed entirely because the agent had no incentive to discover AGENTS.md.
Treatment-v2 improved consultation to 45.5% via an explicit system prompt instruction.

---

## Breakdowns

### By repository (task_success, Treatment-v2 vs Baseline)

| Repository | Baseline | Treatment-v2 | Delta |
|------------|----------|--------------|-------|
| cert-manager-operator | 4.080 ± 0.862 | 3.840 ± 0.688 | −0.240 |
| multiarch-tuning-operator | 3.900 ± 0.845 | 3.967 ± 0.890 | +0.067 |

cert-manager-operator has no CLAUDE.md in upstream, making the baseline harder to compare
fairly. This asymmetry is a known confound.

### By complexity (task_success, Treatment-v2 vs Baseline)

| Complexity | Baseline | Treatment-v2 | Delta | n tasks |
|------------|----------|--------------|-------|---------|
| Low | 5.000 | 4.000 | −1.000 | 1 |
| Medium | 3.960 | 3.800 | −0.160 | 5 |
| High | 3.800 | 4.000 | **+0.200** | 5 |

High-complexity tasks are the only category with a positive delta — the only signal
that directionally supports the hypothesis.

---

## Key Findings

1. **Docs alone are not enough.** Without an explicit instruction, agents ignored the
   agentic/ directory entirely (treatment-v1, 0% doc consultation).

2. **Guided discovery partially helps.** Telling the agent to read AGENTS.md (v2) raised
   consultation to 45.5% and improved pairwise preference, but did not lift absolute scores.

3. **High-complexity tasks are the best candidate.** The +0.200 delta on high-complexity
   tasks is the only positive signal aligning with the hypothesis. These are tasks where
   architectural knowledge matters most.

4. **cert-manager without CLAUDE.md is a poor baseline.** The repo asymmetry inflated
   baseline performance for cert-manager tasks and should be corrected in future campaigns.

---

## Recommended Next Steps

1. **Fix doc discovery.** Integrate AGENTS.md reading into the agent's task loop via
   CLAUDE.md `always_read` directives rather than patching the system prompt.

2. **Focus on high-complexity tasks.** Run a dedicated campaign (n ≥ 15 tasks, 5 runs)
   to get reliable signal at the +0.20 effect size.

3. **Fix the efficiency judge.** Currently checks per-run cost across all 11 cases
   combined; replace with per-case budget tracking. All 165 invocations scored 0.

4. **Align baseline conditions.** Add a CLAUDE.md stub to cert-manager-operator baseline
   or remove it from the eval set.

---

## Caveats

- LLM judges (claude-opus-4-6) evaluated outputs from the same model family. Self-assessment
  bias may suppress signal.
- Sample size (55 pairs per condition) was designed for a medium effect (d≈0.5); actual
  effects were negligible (d<0.2), so this study is underpowered for the effects observed.
- Tasks are synthetic coding prompts, not real PRs or issues.
- Agentic docs were generated (not human-authored); quality scores are self-assessed.
- All efficiency checks failed due to a judge design flaw, not agent regression.

---

*Full data: metrics.csv · Environment: REPRO_MANIFEST.yaml*
