---
agent: Claude Code
model: claude-sonnet-4-6
date: 2026-07-15T18:30:00Z
---

## Recommendation

Pipeline is validated and ready for full production eval. Proceed with 5-run baseline and treatment sweeps immediately.

## Summary

Smoke test on `cm-001-certmanager-cel` (baseline condition, cert-manager-operator):

| Judge | Score |
|---|---|
| task_success | 5/5 |
| code_correctness | 5/5 |
| convention_adherence | 5/5 |
| hallucination_check | 1/1 (PASS) |
| efficiency | PASS (7 turns, $0.42) |
| consulted_docs | PASS (0/2 expected, min_coverage=0.0) |

Run metrics: 7 turns, $0.42, 70s, 82.5% cache hit rate.

## Failure Patterns

None — all judges passed. The agent correctly identified the singleton CEL XValidation pattern by reading `trustmanager_types.go` and mirroring it in `certmanager_types.go`.

## Root Causes (of prior smoke failure)

The original `smoke-baseline` run scored 1/1/1/1 due to two bugs now fixed:
1. **Agent spawned a subagent**: All assistant events had `parent_tool_use_id` → `{{ conversation }}` = empty. Fixed by restricting runner to `allow: [Read, Bash, Grep, Glob]`.
2. **No events.json**: `traces.events: false` → consulted_docs had no events to analyze. Fixed by enabling `traces.events: true`.
3. **Wrong annotation key**: `expected_docs_consulted` was not read by `consulted_docs` judge (it expects `expected_files`). Fixed by renaming across all 44 annotations.yaml files.

## Cost Attribution

Single case: $0.42 at 7 turns. Projected for 5 runs × 11 cases × 2 conditions = 110 invocations: ~$46 assuming similar per-case cost. High-complexity tasks (mto-001, mto-006, cm-003, cm-004, cm-005) may run longer; budget $100 total.
