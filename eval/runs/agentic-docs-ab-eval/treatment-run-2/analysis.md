---
agent: Claude Code
model: claude-sonnet-4-6
date: 2026-07-20T00:00:00Z
---

## Recommendation

**Hold** — do not conclude treatment is harmful based on two runs. The treatment condition is not functioning as designed: agents read 0 of the expected agentic docs in every case, making this effectively a second baseline run. The lower scores (task_success 3.73 vs baseline 3.98 mean) likely reflect model stochasticity rather than a documentation penalty. Run treatment-run-3 through 5 to build statistical power, then re-evaluate. Separately, investigate why AGENTS.md is not auto-loaded — the organic discovery mechanism is broken.

## Summary

- **11 cases**, exit_code 0, $7.92, 952s wall clock
- task_success: 3.73 | code_correctness: 3.73 | convention_adherence: 3.45
- hallucination_check: 3.18 | consulted_docs: 0.0 (pass_rate 0%) | efficiency: 0% pass
- Pairwise vs baseline-run-1: 10 ties, 1 treatment win, 0 baseline wins

## Failure Patterns

- **consulted_docs 0.0** across all 11 cases: agents proceed directly to source files without reading AGENTS.md, agentic/DESIGN.md, or other expected docs. This is structural — the task prompt and system prompt do not guide discovery.
- **efficiency 0%**: all cases exceed cost or turn thresholds (same as all baseline runs — threshold is too tight for this task complexity).
- **hallucination_check 3.18**: several cases had minor invented APIs or paths, consistent with treatment-run-1 and baseline runs.

## Root Causes

1. **AGENTS.md not auto-loaded**: The eval harness system_prompt overrides Claude Code's normal CLAUDE.md/AGENTS.md loading behavior. The treatment CLAUDE.md also does not reference AGENTS.md, so agents never discover agentic docs.
2. **Efficiency threshold miscalibrated**: All 11-case runs exceed the $3/40-turn threshold; the judge is a poor discriminator here.

## Regressions

Compared to baseline-run-1: task_success −0.45, code_correctness −0.27, convention_adherence −0.46. These are within expected variance given only 11 cases and no statistical significance test yet.

## Cost Attribution

- Total: $7.92 for 11 cases = $0.72/case
- 119 turns, $0.0666/turn, 747 output tokens/turn
- 92.6% cache hit rate — highly efficient reuse across runs
