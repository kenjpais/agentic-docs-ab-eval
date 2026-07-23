# Agentic Documentation A/B Evaluation

Does adding generated agentic documentation (AGENTS.md + `agentic/` tree) improve AI coding agent performance on Kubernetes operator tasks?

**Result: No clear improvement detected across 165 invocations (11 tasks × 5 runs × 3 conditions).**

## Conditions

| Condition | Description |
|-----------|-------------|
| Baseline | CLAUDE.md only, no agentic docs |
| Treatment-v1 | Agentic docs present, no explicit read instruction |
| Treatment-v2 | Agentic docs present + AGENTS.md read instruction in system prompt |

## Scores (task_success, 1–5)

| Condition | Mean |
|-----------|------|
| Baseline | 3.98 |
| Treatment-v1 | 3.86 |
| Treatment-v2 | 3.91 |

High-complexity tasks showed the only directional improvement (+0.20 for v2). Full breakdown in [RESULTS.md](RESULTS.md).

## Reproduce

```bash
mlflow ui --backend-store-uri sqlite:///mlflow.db --port 5000
# /eval-run --config eval-baseline.yaml
# /eval-run --config eval-treatment-v2.yaml
```

See [REPRO_MANIFEST.yaml](REPRO_MANIFEST.yaml) for environment details and pinned repo SHAs.
