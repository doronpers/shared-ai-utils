#!/bin/bash
set -e

# Build the rules
python3 src/shared_ai_utils/rules/builder.py > AGENT_KNOWLEDGE_BASE.md

# Copy to all repositories
REPOS=(
    "sono-eval"
    "sono-platform"
    "council-ai"
    "feedback-loop"
    "spatial-selecta"
    "shared-ai-utils"
)

for repo in "${REPOS[@]}"; do
    echo "Syncing rules to $repo..."
    cp AGENT_KNOWLEDGE_BASE.md "../$repo/AGENT_KNOWLEDGE_BASE.md"
done

# Cleanup local generated file
rm AGENT_KNOWLEDGE_BASE.md

echo "Sync complete!"
