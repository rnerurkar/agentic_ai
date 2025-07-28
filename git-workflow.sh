#!/bin/bash
# Git workflow helper for Agentic AI repository
# This script ensures you're always working on the agentic_ai_implementation branch

echo "🔍 Checking current branch..."
CURRENT_BRANCH=$(git branch --show-current)

if [ "$CURRENT_BRANCH" != "agentic_ai_implementation" ]; then
    echo "⚠️  Warning: You're on branch '$CURRENT_BRANCH'"
    echo "🔄 Switching to agentic_ai_implementation branch..."
    git checkout agentic_ai_implementation
    echo "✅ Now on agentic_ai_implementation branch"
else
    echo "✅ Already on agentic_ai_implementation branch"
fi

echo ""
echo "📋 Current status:"
git status --short

echo ""
echo "🎯 Available commands:"
echo "  git add .                    # Stage all changes"
echo "  git commit -m 'message'      # Commit changes"
echo "  git push                     # Push to agentic_ai_implementation branch"
echo ""
echo "🚀 To create a PR to main:"
echo "  Visit: https://github.com/rnerurkar/agentic_ai/compare/main...agentic_ai_implementation"
