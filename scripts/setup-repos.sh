#!/usr/bin/env bash
# setup-repos.sh — Clone repositories and configure baseline/treatment conditions.
#
# Usage: ./scripts/setup-repos.sh
#
# After this script completes:
# 1. Run /create-agentic-docs in Claude Code with each treatment repo as the working directory
# 2. Run /validate-agentic-docs to confirm quality >= 70/100
# 3. Run ./scripts/run-ab-eval.sh to execute the evaluation

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT="$(dirname "$SCRIPT_DIR")"
REPOS_DIR="$ROOT/repos"

CERT_MANAGER_URL="https://github.com/openshift/cert-manager-operator"
MULTIARCH_URL="https://github.com/outrigger-project/multiarch-tuning-operator"

echo "=== A/B Eval Repository Setup ==="
echo "Root: $ROOT"
echo ""

# ---------------------------------------------------------------------------
# Clone repos
# ---------------------------------------------------------------------------

clone_if_missing() {
  local url="$1"
  local dest="$2"
  if [ -d "$dest/.git" ]; then
    echo "  [skip] $dest already exists"
  else
    echo "  Cloning $url -> $dest"
    git clone --depth=1 "$url" "$dest"
  fi
}

echo "--- Cloning repositories ---"
mkdir -p "$REPOS_DIR"

clone_if_missing "$CERT_MANAGER_URL"   "$REPOS_DIR/cert-manager-operator-baseline"
clone_if_missing "$CERT_MANAGER_URL"   "$REPOS_DIR/cert-manager-operator-treatment"
clone_if_missing "$MULTIARCH_URL"      "$REPOS_DIR/multiarch-tuning-operator-baseline"
clone_if_missing "$MULTIARCH_URL"      "$REPOS_DIR/multiarch-tuning-operator-treatment"

echo ""

# ---------------------------------------------------------------------------
# Baseline repos: ensure no agentic/ directory exists
# ---------------------------------------------------------------------------

echo "--- Configuring baseline repos (removing any agentic/ dirs) ---"

for repo in cert-manager-operator-baseline multiarch-tuning-operator-baseline; do
  agentic_dir="$REPOS_DIR/$repo/agentic"
  agents_file="$REPOS_DIR/$repo/AGENTS.md"
  if [ -d "$agentic_dir" ]; then
    echo "  Removing $agentic_dir"
    rm -rf "$agentic_dir"
  fi
  if [ -f "$agents_file" ]; then
    echo "  Removing $agents_file"
    rm -f "$agents_file"
  fi
  echo "  [ok] $repo — no agentic docs"
done

echo ""

# ---------------------------------------------------------------------------
# Treatment repos: ready for /create-agentic-docs
# ---------------------------------------------------------------------------

echo "--- Treatment repos ready for agentic doc generation ---"
echo ""
echo "  Next steps (run in Claude Code):"
echo ""
echo "  1. Generate docs for cert-manager-operator:"
echo "     cd $REPOS_DIR/cert-manager-operator-treatment"
echo "     Then run: /create-agentic-docs"
echo ""
echo "  2. Generate docs for multiarch-tuning-operator:"
echo "     cd $REPOS_DIR/multiarch-tuning-operator-treatment"
echo "     Then run: /create-agentic-docs"
echo ""
echo "  3. Validate quality (must be >= 70/100):"
echo "     /validate-agentic-docs $REPOS_DIR/cert-manager-operator-treatment"
echo "     /validate-agentic-docs $REPOS_DIR/multiarch-tuning-operator-treatment"
echo ""

# ---------------------------------------------------------------------------
# Verify baseline repos have no agentic/
# ---------------------------------------------------------------------------

echo "--- Verification ---"
ERRORS=0

for repo in cert-manager-operator-baseline multiarch-tuning-operator-baseline; do
  if [ -d "$REPOS_DIR/$repo/agentic" ]; then
    echo "  [FAIL] $repo still has agentic/ directory"
    ERRORS=$((ERRORS + 1))
  else
    echo "  [ok]   $repo — no agentic/ directory"
  fi
  if [ -d "$REPOS_DIR/$repo/.git" ]; then
    echo "  [ok]   $repo — git repo present"
  else
    echo "  [FAIL] $repo — not a git repo"
    ERRORS=$((ERRORS + 1))
  fi
done

for repo in cert-manager-operator-treatment multiarch-tuning-operator-treatment; do
  if [ -d "$REPOS_DIR/$repo/.git" ]; then
    echo "  [ok]   $repo — git repo present (agentic docs pending /create-agentic-docs)"
  else
    echo "  [FAIL] $repo — not a git repo"
    ERRORS=$((ERRORS + 1))
  fi
done

echo ""

if [ "$ERRORS" -gt 0 ]; then
  echo "Setup completed with $ERRORS error(s). Resolve before running the eval."
  exit 1
else
  echo "=== Setup complete. Run /create-agentic-docs in each treatment repo, then ./scripts/run-ab-eval.sh ==="
fi
