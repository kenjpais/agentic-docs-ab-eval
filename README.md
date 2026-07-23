# Agentic Documentation A/B Evaluation

A controlled experiment measuring whether generated agentic documentation (AGENTS.md + `agentic/` tree) improves AI coding agent performance on Kubernetes operator tasks.

## Conditions

| Condition | Description | Dataset |
|-----------|-------------|---------|
| Baseline | CLAUDE.md only, no agentic docs | `eval/dataset/baseline-flat` |
| Treatment-v1 | Full agentic docs, no explicit read instruction | `eval/dataset/treatment-flat` |
| Treatment-v2 | Full agentic docs + AGENTS.md read instruction in system prompt | `eval/dataset/treatment-flat` |

11 tasks × 5 runs per condition = 55 scored pairs each. Judges: `task_success`, `code_correctness`, `convention_adherence`, `hallucination_check` (1–5 scale, claude-opus-4-6).

## Result

**Null result — H₀ not rejected.** No statistically significant improvement detected for either treatment. Treatment-v2 showed a directional pairwise preference (40.7% win rate) but did not reach the pre-registered 55% threshold. All Wilcoxon p-values > 0.05. Full analysis: [RESULTS.md](RESULTS.md).

## Repo Layout

```
eval-baseline.yaml          eval config — baseline condition
eval-treatment.yaml         eval config — treatment-v1
eval-treatment-v2.yaml      eval config — treatment-v2
eval/
  dataset/                  test cases (input.yaml, reference.md, annotations.yaml)
  judges/                   LLM judge prompts
  runs/                     raw per-case outputs and summaries
metrics.csv                 aggregated scores across all runs
mlflow.db                   MLflow backend store
RESULTS.md                  full statistical report
REPRO_MANIFEST.yaml         environment and reproduction instructions
```

## Reproduce

```bash
# run baseline (requires eval harness)
/eval-run --config eval-baseline.yaml

# view results in MLflow UI (served from mlflow.db)
mlflow ui --backend-store-uri sqlite:///mlflow.db --port 5000
```

See [REPRO_MANIFEST.yaml](REPRO_MANIFEST.yaml) for exact environment, model versions, and dataset hashes.
