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
    "Website-Sonotheia-v251120"
)

for repo in "${REPOS[@]}"; do
    echo "Syncing rules to $repo..."
    # Skip if source and dest are the same file
    if [ "$(realpath AGENT_KNOWLEDGE_BASE.md)" == "$(realpath ../$repo/AGENT_KNOWLEDGE_BASE.md)" ]; then
        continue
    fi
    cp AGENT_KNOWLEDGE_BASE.md "../$repo/AGENT_KNOWLEDGE_BASE.md"
done

# Cleanup local generated file
rm AGENT_KNOWLEDGE_BASE.md

echo "Sync complete!"
