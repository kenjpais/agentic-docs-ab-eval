#!/usr/bin/env bash
# run-ab-eval.sh — Execute the full A/B evaluation experiment.
#
# Prerequisites:
#   - ./scripts/setup-repos.sh completed successfully
#   - /create-agentic-docs run in each treatment repo
#   - /validate-agentic-docs confirms treatment repos >= 70/100
#   - ANTHROPIC_API_KEY set in environment
#   - /eval-setup run to confirm harness environment is ready
#
# Usage:
#   ./scripts/run-ab-eval.sh [--runs N] [--smoke-test]
#
#   --runs N       Number of repeated runs per condition (default: 5)
#   --smoke-test   Run only 1 case per condition to verify configuration before full run

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT="$(dirname "$SCRIPT_DIR")"

RUNS=5
SMOKE_TEST=0

while [[ $# -gt 0 ]]; do
  case "$1" in
    --runs) RUNS="$2"; shift 2 ;;
    --smoke-test) SMOKE_TEST=1; shift ;;
    *) echo "Unknown argument: $1"; exit 1 ;;
  esac
done

echo "=== A/B Eval Experiment Runner ==="
echo "Runs per condition: $RUNS"
echo "Smoke test mode: $SMOKE_TEST"
echo ""

# ---------------------------------------------------------------------------
# Preflight checks
# ---------------------------------------------------------------------------

echo "--- Preflight checks ---"

if [ -z "${ANTHROPIC_API_KEY:-}" ]; then
  echo "[FAIL] ANTHROPIC_API_KEY is not set"
  exit 1
fi
echo "  [ok] ANTHROPIC_API_KEY is set"

for repo in cert-manager-operator-treatment multiarch-tuning-operator-treatment; do
  if [ ! -d "$ROOT/repos/$repo/agentic" ]; then
    echo "[FAIL] $repo is missing agentic/ directory — run /create-agentic-docs first"
    exit 1
  fi
  echo "  [ok] $repo — agentic/ present"
done

for repo in cert-manager-operator-baseline multiarch-tuning-operator-baseline; do
  if [ -d "$ROOT/repos/$repo/agentic" ]; then
    echo "[FAIL] $repo has an agentic/ directory — baseline repos must NOT have agentic docs"
    exit 1
  fi
  echo "  [ok] $repo — no agentic/ (baseline clean)"
done

echo ""

# ---------------------------------------------------------------------------
# Smoke test: run 1 case per condition to verify judge configuration
# ---------------------------------------------------------------------------

if [ "$SMOKE_TEST" -eq 1 ]; then
  echo "--- Smoke test: running 1 case per condition ---"
  echo "  Note: pass/fail of smoke test does not indicate eval quality,"
  echo "  only that the harness configuration is valid."
  echo ""
  echo "  Run in Claude Code:"
  echo "    /eval-run --config eval-baseline.yaml --run-id smoke-baseline --max-cases 1"
  echo "    /eval-run --config eval-treatment.yaml --run-id smoke-treatment --max-cases 1"
  echo ""
  echo "  Verify smoke-treatment run's summary.yaml contains per-case judge scores."
  echo "  If all scores are 0, check judge file paths in eval-treatment.yaml."
  echo ""
  exit 0
fi

# ---------------------------------------------------------------------------
# Main experiment
# ---------------------------------------------------------------------------

echo "--- Experiment execution plan ---"
echo ""
echo "Run the following commands in Claude Code, in order:"
echo ""
echo "Step 1: Run baseline condition ($RUNS times)"
for i in $(seq 1 "$RUNS"); do
  echo "  /eval-run --config eval-baseline.yaml --run-id baseline-run-$i"
done
echo ""
echo "Step 2: Run treatment condition ($RUNS times)"
for i in $(seq 1 "$RUNS"); do
  echo "  /eval-run --config eval-treatment.yaml --run-id treatment-run-$i"
done
echo ""
echo "Step 3: Sync results to MLflow"
echo "  /eval-mlflow --experiment agentic-docs-ab-eval"
echo ""
echo "Step 4: Human review of edge cases"
echo "  /eval-review --run-id treatment-run-1"
echo ""

# ---------------------------------------------------------------------------
# Ablation study plan (NOT YET IMPLEMENTED)
# ---------------------------------------------------------------------------
# The ablation configs (eval-ablation-c.yaml, eval-ablation-d.yaml,
# eval-ablation-e.yaml) and their datasets have not been created.
# Uncomment and complete the steps below when running ablation studies.
#
# echo "--- Ablation study plan (run after main experiment) ---"
# echo ""
# echo "Ablation C (design docs only):"
# echo "  1. Create repos/multiarch-tuning-operator-ablation-design/ with only AGENTS.md + agentic/DESIGN.md"
# echo "  2. Update dataset/ablation-c/ input.yaml files with ablation repo path"
# echo "  3. /eval-run --config eval-ablation-c.yaml --run-id ablation-c-run-1"
# echo ""
# echo "Ablation D (testing docs only):"
# echo "  1. Create repos/multiarch-tuning-operator-ablation-testing/ with only agentic/TESTING.md"
# echo "  2. /eval-run --config eval-ablation-d.yaml --run-id ablation-d-run-1"
# echo ""
# echo "Ablation E (ops docs only):"
# echo "  1. Create repos/multiarch-tuning-operator-ablation-ops/ with only agentic/RELIABILITY.md + SECURITY.md"
# echo "  2. /eval-run --config eval-ablation-e.yaml --run-id ablation-e-run-1"
# echo ""

# ---------------------------------------------------------------------------
# Statistical analysis
# ---------------------------------------------------------------------------

echo "--- Post-experiment analysis ---"
echo ""
echo "After all runs complete:"
echo "  1. Export results: mlflow ui (view at http://localhost:5000)"
echo "  2. Run analysis: python3 scripts/phase7_analysis.py"
echo "     Computes:"
echo "       - Paired mean comparison (treatment-v2 vs baseline, by task_id)"
echo "       - Per-category breakdown (api-change, test-writing, observability, security, architecture)"
echo "       - Per-complexity breakdown (low, medium, high)"
echo "       - Doc consultation rates"
echo "     Output: eval/runs/agentic-docs-ab-eval/phase7_results.json"
echo ""
echo "=== Run the Claude Code commands above to start the experiment ==="
