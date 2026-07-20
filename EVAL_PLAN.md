# Evaluation Framework: Incremental Impact of Agentic Documentation

## Context

This plan responds to the design brief in `PLAN.md`. The goal is a rigorous A/B evaluation measuring whether agentic documentation (architecture guides, coding standards, runbooks, etc.) improves AI coding agent performance beyond the baseline `CLAUDE.md` alone. The evaluation must be reproducible, statistically sound, and operable against two Kubernetes operator repositories:

- `cert-manager-operator`: [https://github.com/openshift/cert-manager-operator](https://github.com/openshift/cert-manager-operator)
- `multiarch-tuning-operator`: [https://github.com/outrigger-project/multiarch-tuning-operator](https://github.com/outrigger-project/multiarch-tuning-operator)

Both repos will be **cloned fresh** from GitHub. Agentic documentation for treatment clones will be **generated from scratch** via `/create-agentic-docs` — no pre-existing local copies are used.

Tools confirmed available: `agent-eval-harness` v1.13.2 (installed plugin), MLflow 3.14.0, skills `/create-agentic-docs` and `/validate-agentic-docs`.

---



## Workspace Structure to Build

```
a_b_evals/
├── eval-baseline.yaml              # Eval config: baseline condition
├── eval-treatment.yaml             # Eval config: treatment condition
├── eval/
│   ├── dataset/
│   │   ├── multiarch-tuning-operator/    # 6 task case dirs
│   │   │   ├── 001-add-api-field/
│   │   │   │   ├── input.yaml
│   │   │   │   ├── reference.md
│   │   │   │   └── annotations.yaml
│   │   │   ├── 002-write-webhook-test/
│   │   │   ├── 003-add-metric/
│   │   │   ├── 004-webhook-validation/
│   │   │   ├── 005-promql-alert/
│   │   │   └── 006-new-execution-mode/
│   │   └── cert-manager-operator/        # 5 task case dirs
│   │       ├── 001-certmanager-cel/
│   │       ├── 002-validate-manifest/
│   │       ├── 003-optional-informer/
│   │       ├── 004-immutable-field/
│   │       └── 005-hash-triggered-restart/
│   ├── judges/
│   │   ├── task-success.md
│   │   ├── code-correctness.md
│   │   ├── convention-adherence.md
│   │   └── hallucination-check.md
│   └── prompts/
│       └── pairwise-comparison.md
├── repos/
│   ├── multiarch-tuning-operator-baseline/   # Fresh clone, no agentic/
│   ├── multiarch-tuning-operator-treatment/  # Fresh clone + generated agentic/
│   ├── cert-manager-operator-baseline/       # Fresh clone, no agentic/
│   └── cert-manager-operator-treatment/      # Fresh clone + generated agentic/
└── scripts/
    ├── setup-repos.sh              # Clone + configure both conditions
    └── run-ab-eval.sh              # Orchestrate full experiment
```

---



## Phase 1: Repository Setup

**Script:** `scripts/setup-repos.sh`

For each repo:

1. Clone the upstream GitHub repository fresh into `repos/<repo>-baseline/` and `repos/<repo>-treatment/`
  - `cert-manager-operator`: [https://github.com/openshift/cert-manager-operator](https://github.com/openshift/cert-manager-operator)
  - `multiarch-tuning-operator`: [https://github.com/outrigger-project/multiarch-tuning-operator](https://github.com/outrigger-project/multiarch-tuning-operator)
2. Baseline clones: leave as-is from upstream — no agentic docs added
3. Treatment clones: run `/create-agentic-docs` inside each treatment clone to generate full agentic documentation from scratch (AGENTS.md, agentic/DESIGN.md, DEVELOPMENT.md, TESTING.md, RELIABILITY.md, SECURITY.md)
4. Both clones share identical git history, CLAUDE.md, and source files — the only difference is `agentic/` presence
5. Run `/validate-agentic-docs` on each treatment repo to confirm quality ≥ 70/100

**Do NOT use any pre-existing local copies** of either repo. All documentation must be freshly generated via `/create-agentic-docs` to ensure reproducibility and to measure the plugin's actual output quality.

---



## Phase 2: Benchmark Task Dataset



### Task Case Directory Schema

Each case dir contains:

```
input.yaml       # task prompt (field: `task`)
reference.md     # gold-standard implementation notes or expected output description
annotations.yaml # metadata: repo, category, complexity, expected_docs_consulted
```

`annotations.yaml` schema:

```yaml
repo: multiarch-tuning-operator
category: api-change          # api-change | test-writing | observability | security | architecture
complexity: high              # low | medium | high
expected_docs_consulted:      # Which agentic docs should inform this task
  - agentic/DESIGN.md
  - agentic/DEVELOPMENT.md
  - AGENTS.md
```



### multiarch-tuning-operator Tasks (6)


| ID  | Task                                                                                                                                           | Category      | Complexity | Key Agentic Docs                     |
| --- | ---------------------------------------------------------------------------------------------------------------------------------------------- | ------------- | ---------- | ------------------------------------ |
| 001 | Add `maxImageInspectionRetries` field to CPPC spec; wire through CPPC informer; update v1alpha1 conversion; state correct `make` command order | api-change    | high       | AGENTS.md, DEVELOPMENT.md, DESIGN.md |
| 002 | Write Ginkgo unit test verifying system namespace exclusion in webhook using fluent pod builder                                                | test-writing  | medium     | TESTING.md, SECURITY.md              |
| 003 | Add Prometheus counter `mto_ppo_ctrl_image_cache_hits_total` to metrics package; instrument in image facade                                    | observability | medium     | RELIABILITY.md                       |
| 004 | Add webhook validation rejecting duplicate architectures in `NodeAffinityScoring.Platforms`                                                    | security      | medium     | SECURITY.md, DESIGN.md               |
| 005 | Write `PrometheusRule` YAML for `MultiarchImageInspectionFailureRateCritical` alert using documented SLO thresholds                            | observability | low        | RELIABILITY.md                       |
| 006 | Add fifth execution mode `--enable-metrics-aggregator` to `cmd/main.go` following all established conventions                                  | architecture  | high       | DESIGN.md, AGENTS.md, DEVELOPMENT.md |


**Reference docs for each task** capture: which files to modify, what the correct approach is, which conventions must be followed, and what a passing judge would look for. References are written from ground truth (existing code + agentic docs), not generated by the agent being evaluated.

### cert-manager-operator Tasks (5)

> **Note:** `expected_docs_consulted` in annotations.yaml for cert-manager tasks references the standard generated agentic doc structure (AGENTS.md, agentic/DESIGN.md, DEVELOPMENT.md, SECURITY.md) — not ADR files. Reference.md for each task must be authored **after** running `/create-agentic-docs` on the treatment clone, so it reflects the actual generated content.


| ID  | Task                                                                                                                                             | Category     | Complexity | Key Agentic Docs          |
| --- | ------------------------------------------------------------------------------------------------------------------------------------------------ | ------------ | ---------- | ------------------------- |
| 001 | Add CEL `x-kubernetes-validations` singleton enforcement to `CertManager` type (matching TrustManager's existing pattern)                        | api-change   | medium     | AGENTS.md, DESIGN.md      |
| 002 | Add `validateDeploymentManifest` guard to IstioCSR deployment pipeline (mirroring TrustManager's existing pattern)                               | architecture | medium     | DESIGN.md, DEVELOPMENT.md |
| 003 | Wire a new `OptionalInformer` for the OpenShift Proxy API through the TrustManager controller using `InitInformerIfAvailable`                    | architecture | high       | DESIGN.md, DEVELOPMENT.md |
| 004 | Add `tlsMinVersion` immutable field to `IstioCSRConfig` with layered CEL presence+value-immutability rules                                       | api-change   | high       | DESIGN.md, SECURITY.md    |
| 005 | Implement content-hash-triggered rolling restart for a new ConfigMap in IstioCSR controller (replicating TrustManager's hash annotation pattern) | architecture | high       | DESIGN.md, RELIABILITY.md |


---



## Phase 3: Eval Configuration



### `eval-baseline.yaml` and `eval-treatment.yaml` — Shared Fields

```yaml
name: agentic-docs-ab-eval
description: A/B evaluation of agentic documentation impact on Kubernetes operator coding tasks

execution:
  mode: prompt
  prompt: |
    You are a Go engineer working on a Kubernetes operator.
    The repository is located at {{ repo_path }}.
    Change your working directory to that repository before beginning.
    
    Task:
    {{ task }}
    
    Produce a complete implementation. Include all files that must be modified,
    the exact changes to make, and any commands to run (e.g., code generation).

  timeout: 1800
  max_budget_usd: 3.00
  parallelism: 2

runner:
  type: claude-code
  effort: high

models:
  skill: claude-opus-4-8    # Most capable model for the coding tasks
  judge: claude-opus-4-8
  subagent: claude-sonnet-5

mlflow:
  experiment: agentic-docs-ab-eval

traces:
  stdout: true
  stderr: true
  metrics: true
  events: false

dataset:
  path: eval/dataset
  schema: |
    Each case directory contains input.yaml with fields 'repo_path' and 'task',
    reference.md with the gold-standard approach, and annotations.yaml with metadata.
```



### Condition-Specific Fields

`eval-baseline.yaml` adds:

```yaml
mlflow:
  tags:
    condition: baseline
    repos: multiarch-tuning-operator,cert-manager-operator
```

`eval-treatment.yaml` adds:

```yaml
mlflow:
  tags:
    condition: treatment
    repos: multiarch-tuning-operator,cert-manager-operator
```

The `input.yaml` in each case specifies which `repo_path` to use — this is the mechanism for directing each condition to the right clone. Two dataset variants are generated by `scripts/setup-repos.sh`: one with baseline paths, one with treatment paths. The eval.yaml files use `dataset.path: eval/dataset/baseline` and `eval/dataset/treatment` respectively.

---



## Phase 4: Judges



### Judge 1: `task_success` (LLM, 1–5)

**File:** `eval/judges/task-success.md`
Prompt asks: Did the agent produce a complete, runnable implementation that addresses all parts of the task? Score 1 (not attempted) to 5 (fully correct, nothing missing).

### Judge 2: `code_correctness` (LLM, 1–5)

**File:** `eval/judges/code-correctness.md`
Evaluates: type correctness, API usage, correct kubebuilder markers, no invented methods or packages. Compares against reference.md. Score 1 (broken/wrong) to 5 (would pass review with no changes).

### Judge 3: `convention_adherence` (LLM, 1–5)

**File:** `eval/judges/convention-adherence.md`
Evaluates: naming conventions, error handling patterns, test structure (Ginkgo BDD), code generation ordering, builder API usage, make target ordering. Score 1 (ignores conventions) to 5 (idiomatic, matches existing patterns exactly).

### Judge 4: `consulted_docs` (builtin)

```yaml
- name: consulted_docs
  builtin: consulted_docs
  arguments:
    min_coverage: 0.5
    match: suffix
```

Tracks which documentation files the agent read during execution. Used to compute documentation usage rate and correlate doc consultation with task success.

### Judge 5: `efficiency` (inline check)

```yaml
- name: efficiency
  check: |
    turns = outputs.get("num_turns", 999)
    cost = outputs.get("cost_usd", 999)
    if turns > 40 or cost > 3.0:
        return False, f"Excessive: {turns} turns, ${cost:.2f}"
    return True, f"{turns} turns, ${cost:.2f}"
```



### Judge 6: `hallucination_check` (LLM)

**File:** `eval/judges/hallucination-check.md`
Detects: invented package names, non-existent methods, incorrect API signatures, wrong file paths. Score: 0 (hallucinations present) or 1 (grounded in actual codebase).

### Judge 7: `pairwise` (builtin comparison)

Triggered via `--baseline <run-id>` when running the treatment condition. Compares baseline and treatment outputs per case across four dimensions: Completeness, Quality, Accuracy, Relevance. Returns `preferred: A | B | tie`.

### Thresholds

```yaml
thresholds:
  task_success:
    min_mean: 3.0
  code_correctness:
    min_mean: 3.0
  convention_adherence:
    min_mean: 3.0
  hallucination_check:
    min_pass_rate: 0.85
  pairwise:
    min_win_rate: 0.55    # Treatment must win 55%+ of pairwise comparisons
```

---



## Phase 5: Experiment Execution



### Standard Run Sequence

```bash
# 1. Setup and verify environment
/eval-setup

# 2. Clone and configure repos
./scripts/setup-repos.sh

# 3. Validate treatment repos
/validate-agentic-docs repos/multiarch-tuning-operator-treatment
/validate-agentic-docs repos/cert-manager-operator-treatment

# 4. Run baseline (5 times for statistical power)
for i in 1 2 3 4 5; do
  /eval-run --config eval-baseline.yaml --run-id baseline-run-$i
done

# 5. Run treatment, using first baseline run as pairwise reference
/eval-run --config eval-treatment.yaml --run-id treatment-run-1 --baseline baseline-run-1

# 6. Sync all results to MLflow
/eval-mlflow --experiment agentic-docs-ab-eval

# 7. Review results
/eval-review --run-id treatment-run-1
```



### Repeated Runs

5 runs per condition per task = 55 baseline invocations + 55 treatment invocations = **110 total agent invocations**. This sample size provides ~80% power to detect a 0.5-point improvement on a 1–5 scale (medium effect size, α=0.05).

---



## Phase 6: Ablation Studies

Run the following conditions to isolate which documentation categories drive improvement:


| Condition                | Repo State                                                        | Tag                  | Purpose                                             |
| ------------------------ | ----------------------------------------------------------------- | -------------------- | --------------------------------------------------- |
| A — Baseline             | CLAUDE.md only                                                    | `ablation:none`      | Control                                             |
| B — Full Treatment       | CLAUDE.md + all agentic docs                                      | `ablation:full`      | Full treatment                                      |
| C — Design Only          | CLAUDE.md + AGENTS.md + DESIGN.md + component-architecture.md     | `ablation:design`    | Architecture docs only                              |
| D — Testing Only         | CLAUDE.md + TESTING.md                                            | `ablation:testing`   | Test writing guidance only                          |
| E — Ops Only             | CLAUDE.md + RELIABILITY.md + SECURITY.md                          | `ablation:ops`       | Runbooks/SLOs only                                  |
| F — Cross-repo Generated | Both repos use freshly generated docs from `/create-agentic-docs` | `ablation:generated` | Measures how generation quality varies across repos |


Repo variants for ablations C–E are created by selectively copying only the relevant `agentic/` subdirectories from the treatment clone into new repo copies. Ablation F compares the generation quality between the two repos (cert-manager vs multiarch) by cross-referencing `/validate-agentic-docs` scores against task performance — isolating whether doc generation quality differences explain performance gaps.

---



## Phase 7: Statistical Analysis Plan



### Primary Hypothesis

H₀: Agentic documentation provides no improvement over baseline on any metric.
H₁: Treatment condition shows statistically significant improvement (α = 0.05) on at least task_success and convention_adherence.

### Test Selection

- **Wilcoxon signed-rank test** (paired, non-parametric): appropriate for ordinal 1–5 scores, does not assume normality. Apply per-task (paired across condition).
- **Mann-Whitney U test**: for cross-condition unpaired comparison on efficiency metrics.
- **Cohen's d**: effect size for practical significance.
- **Bootstrap 95% CI** (1000 iterations): confidence intervals on mean scores.



### Per-Metric Reporting

For each metric (task_success, code_correctness, convention_adherence, hallucination_rate, num_turns, cost_usd):

- Mean ± SD per condition
- Wilcoxon p-value
- Cohen's d
- 95% bootstrap CI on mean difference



### Per-Category Analysis

Break down results by `annotations.yaml` category (api-change, test-writing, observability, security, architecture) and complexity (low, medium, high) to identify which documentation categories provide the largest gains.

### Documentation ROI Metric

For each agentic document, compute:

```
impact_coefficient = correlation(doc_consulted_in_run, task_success_score)
consultation_rate = count(runs_where_doc_consulted) / total_runs
ROI = impact_coefficient × consultation_rate / estimated_maintenance_pages
```

Documents with high ROI justify the maintenance cost; low-ROI documents are candidates for pruning.

---



## Phase 8: Scoring Framework

