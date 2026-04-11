#!/usr/bin/env bash
# ==============================================================================
# Triune Orchestrator Bootstrap Script
# ==============================================================================
# Creates and initializes the triune-orchestrator parent repo with all
# ecosystem submodules. Run from the triune-swarm-engine root directory.
#
# Usage:
#   bash scripts/bootstrap_orchestrator.sh [--target-dir DIR]
#
# Options:
#   --target-dir DIR   Directory to create the orchestrator in
#                      (default: ../triune-orchestrator)
# ==============================================================================

set -euo pipefail

# --- Configuration -----------------------------------------------------------
ORCHESTRATOR_NAME="triune-orchestrator"
DEFAULT_TARGET="../${ORCHESTRATOR_NAME}"
ORG="Triune-Oracle"
REMOTE_URL="https://github.com/${ORG}/${ORCHESTRATOR_NAME}.git"

SUBMODULES=(
    "https://github.com/${ORG}/triune-swarm-engine.git"
    "https://github.com/${ORG}/culturalcodex.git"
    "https://github.com/${ORG}/monetization-agent.git"
    "https://github.com/${ORG}/triumviratemonitor.git"
)

# --- Parse arguments ----------------------------------------------------------
TARGET_DIR="${DEFAULT_TARGET}"
while [[ $# -gt 0 ]]; do
    case "$1" in
        --target-dir)
            TARGET_DIR="$2"
            shift 2
            ;;
        -h|--help)
            echo "Usage: bash scripts/bootstrap_orchestrator.sh [--target-dir DIR]"
            echo ""
            echo "Creates the triune-orchestrator repo with all ecosystem submodules."
            echo ""
            echo "Options:"
            echo "  --target-dir DIR   Directory to create the orchestrator in"
            echo "                     (default: ../triune-orchestrator)"
            exit 0
            ;;
        *)
            echo "Unknown option: $1" >&2
            exit 1
            ;;
    esac
done

# --- Preflight checks --------------------------------------------------------
if [ -d "${TARGET_DIR}" ]; then
    echo "❌ Target directory '${TARGET_DIR}' already exists. Aborting."
    exit 1
fi

if ! command -v git &>/dev/null; then
    echo "❌ git is not installed."
    exit 1
fi

# --- Initialize ---------------------------------------------------------------
echo "🚀 Creating Triune Orchestrator at: ${TARGET_DIR}"
mkdir -p "${TARGET_DIR}"
cd "${TARGET_DIR}"

git init
git checkout -b main 2>/dev/null || git branch -M main

echo "📦 Adding ecosystem submodules..."
for repo in "${SUBMODULES[@]}"; do
    name=$(basename "${repo}" .git)
    echo "   ➜ ${name}"
    git submodule add "${repo}" || {
        echo "   ⚠️  Failed to add ${name} — skipping (repo may not exist yet)"
    }
done

# --- Commit -------------------------------------------------------------------
echo ""
echo "📝 Creating initial commit..."
git add -A
git commit -m "Initialize Triune orchestration repo with linked submodules" || {
    echo "⚠️  Nothing to commit."
}

# --- Remote setup (optional) --------------------------------------------------
echo ""
echo "✅ Orchestrator initialized successfully!"
echo ""
echo "Next steps:"
echo "  1. Create the remote repo:"
echo "       gh repo create ${ORG}/${ORCHESTRATOR_NAME} --public"
echo ""
echo "  2. Add the remote and push:"
echo "       cd ${TARGET_DIR}"
echo "       git remote add origin ${REMOTE_URL}"
echo "       git push -u origin main"
echo ""
echo "  3. Clone with submodules:"
echo "       git clone --recurse-submodules ${REMOTE_URL}"
