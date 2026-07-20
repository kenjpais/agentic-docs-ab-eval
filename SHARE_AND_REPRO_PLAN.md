# Share Findings and Reproduce Results

Plan for packaging the agentic-docs A/B eval so the organization can trust the
numbers and others can re-analyze or re-run the experiment.

Campaign = one frozen experiment (same dataset, configs, models, repo SHAs,
docs, and named runs). Change any of those → start a new campaign.


## Current state (verify before starting)

- Runs present: baseline-run-1..5, treatment-run-1 (11 cases each)
- Missing for a fair headline claim: treatment-run-2..5
- Smoke runs exist (smoke-baseline, smoke-baseline-v2) — exclude from published
  aggregates
- mlflow.db has experiment agentic-docs-ab-eval but 0 logged runs
- Dataset input.yaml uses absolute /Users/kpais/... paths (blocks other machines)
- Project is not a git repo; no README; no frozen docs package
- Pinned SHAs today:
  - cert-manager-operator: 849995ea92d1a795c72fb1ea2f266ee147ded275
  - multiarch-tuning-operator: 21943765a028587358bcec768bb81fd9979c9a83
- Models: skill/judge claude-opus-4-6; Claude Code ~2.1.210
- Docs quality (treatment config): cm=85, mto=84
- Caveat: multiarch has CLAUDE.md; cert-manager does not


## Phase 0 — Make the campaign reliable

1. Finish treatment repeats
   - Run treatment-run-2..5 paired to baseline-run-2..5
   - Command pattern: /eval-run --config eval-treatment.yaml
     --run-id treatment-run-N --baseline baseline-run-N

2. Do not publish IDV or "80% power" claims until both arms have 5 runs
   - IDV = mean(OES_treatment) - mean(OES_baseline)
   - Power claim in EVAL_PLAN assumes 5 runs per condition

3. Export results without an org MLflow server
   - Treat eval/runs/**/summary.yaml as source of truth
   - Export metrics.csv: one row per case x run x condition
     (judge scores, cost_usd, num_turns, consulted_docs, tags)
   - Zip results pack: metrics.csv + summary.yaml trees + run_result.json
   - Optional: re-sync mlflow.db later; do not block sharing on empty sqlite

4. Write REPRO_MANIFEST.yaml (pin the environment)
   - campaign name/date
   - harness version, Claude Code version, model IDs
   - repo SHAs, docs quality scores
   - run IDs included in the published set
   - total cost if known

5. Document the CLAUDE.md asymmetry in RESULTS.md (or align and re-run)

6. Human review
   - Spot-check at least 3 wins, 3 losses, 3 ties via /eval-review
   - Attach short notes to the results pack


## Phase 1 — Make the project reproducible

1. Put a_b_evals under version control
   - Track: configs, dataset, judges, scripts, EVAL_PLAN.md, analysis.ipynb,
     REPRO_MANIFEST.yaml, RESULTS.md, SHARE_AND_REPRO_PLAN.md
   - Do not commit full repos/ vendor trees

2. Replace absolute repo_path values with workspace-relative paths
   - Example: repos/cert-manager-operator-baseline
   - Update baseline-flat and treatment-flat (and nested copies if used)

3. Freeze treatment docs used in this campaign
   - Save exact AGENTS.md + agentic/** for both treatment clones
   - Commit them under docs-frozen/ OR tarball with checksum in the manifest
   - Why: /create-agentic-docs is not bit-stable across time; regenerate = new campaign

4. Pin upstream checkouts in setup-repos.sh
   - After clone: git checkout <PINNED_SHA> for each repo
   - Same SHA for baseline and treatment of that repo

5. Add README.md and REPRODUCE.md
   - README: what the eval is, where results live
   - REPRODUCE: exact steps, cost estimate, expected artifacts

6. Tag the release
   - Example: campaign-2026-07-agentic-docs-v1


## Phase 2 — Share findings with the organization

Deliver three text/artifact packages from the tagged campaign.

### A. Decision brief (RESULTS.md, 1–2 pages)

- Question: do generated agentic docs improve agent performance beyond baseline?
- Primary metrics: task_success, convention_adherence, IDV/OES, pairwise win rate
- Secondary: code_correctness, hallucination_check, efficiency, consulted_docs
- Breakdown: by repo, category, complexity
- Decision vs thresholds (from analysis.ipynb):
  - IDV > 0.10 meaningful; IDV > 0.20 strong
  - pairwise win rate >= 0.55
- Caveats: LLM judges, text-only agent (no file write/apply/test), synthetic
  tasks, generated (not human) docs, CLAUDE.md gap, sample size

### B. Evidence pack

- metrics.csv + eval/runs summaries for published run IDs
- Executed analysis outputs (tables; charts if generated — OES box/strip,
  forest plot of mean differences)
- 6–10 annotated case notes from human review
- Link or path to REPRO_MANIFEST.yaml

### C. Walkthrough (live meeting or recorded screen video)

- ~30 minutes: claim → one chart/table → one win and one loss trace →
  where the pack lives
- Recorded option: screen+voice clip (e.g. Loom) for async viewers


## Phase 3 — Let others reproduce

### Tier 1 — Re-analyze frozen scores (cheap, must match)

1. Clone tagged release / unpack results pack
2. Load metrics.csv (or synced MLflow if available)
3. Run analysis.ipynb with RNG_SEED=42
4. Confirm IDV, Wilcoxon, CIs match RESULTS.md within rounding

Proves: published math is correct.

### Tier 2 — Re-run the experiment (expensive, not bit-identical)

1. Install same harness + Claude Code versions from the manifest
2. Set ANTHROPIC_API_KEY
3. setup-repos.sh → checkout pinned SHAs
4. Apply frozen treatment docs (do not regenerate)
5. Verify relative repo_path values
6. Smoke: 1 case x both conditions
7. Full: 5x baseline + 5x treatment with matching --baseline
8. Log under a new experiment name (…-replication-YYYYMMDD)
9. Compare direction/magnitude to original; expect similar, not identical scores

Proves: effect still appears under agent noise.


## Phase 4 — Keep results trustworthy over time

1. Immutable campaign rule: no silent edits to judges/dataset/docs after publish
2. Pre-register primary metrics in RESULTS.md
3. Keep traces internal if repos are private
4. Exclude smoke-* runs from headline aggregates
5. Ablations = separate campaign, not mixed into the first headline


## Smoke runs (definition)

- Tiny preflight (e.g. 1 case) before a full campaign
- Name comes from "smoke test": check for wiring fires before a large spend
- Use them; do not include them in published statistics


## Definition of done

Sharing done when:
- [ ] Tagged release exists
- [ ] RESULTS.md circulated
- [ ] metrics.csv / results pack matches published tables
- [ ] Peer Tier 1 re-analysis matches headline numbers
- [ ] REPRODUCE.md lists SHAs, models, harness version, frozen docs location
- [ ] Caveats are explicit

Repro done when:
- [ ] Someone else completes Tier 1
- [ ] Tier 2 smoke works on another machine with relative paths


## Suggested order of work

Week 0
1. Finish treatment-run-2..5
2. Export metrics.csv + results zip
3. Write REPRO_MANIFEST.yaml
4. Human review sample
5. Write RESULTS.md draft (mark incomplete until step 1 done)

Week 0–1
6. Init git; relative paths; freeze docs; pin SHAs in setup script
7. README.md + REPRODUCE.md
8. Tag campaign release

Week 1
9. Circulate RESULTS.md + evidence pack
10. Walkthrough (live or recorded)
11. Invite one peer to Tier 1 re-analysis


## Optional later: DocOps loop (not required for first share)

1. Log consulted_docs + scores on every eval (already supported)
2. Track per-doc consultation_rate and correlation with success
3. Propose doc edits from failure clusters
4. Mini A/B old docs vs proposed docs before promoting
5. Human approve merges; do not auto-promote on vibes


## Highest-priority blockers

1. Empty MLflow / analysis not fed by eval/runs — export CSV instead
2. Only one full treatment run
3. Absolute paths in dataset
4. No git tag / no README
5. Treatment docs not frozen as an artifact
6. cert-manager missing CLAUDE.md vs stated design
