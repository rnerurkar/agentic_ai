# Git workflow helper for Agentic AI repository (PowerShell)
# This script ensures you're always working on the agentic_ai_implementation branch

Write-Host "🔍 Checking current branch..." -ForegroundColor Cyan
$currentBranch = git branch --show-current

if ($currentBranch -ne "agentic_ai_implementation") {
    Write-Host "⚠️  Warning: You're on branch '$currentBranch'" -ForegroundColor Yellow
    Write-Host "🔄 Switching to agentic_ai_implementation branch..." -ForegroundColor Yellow
    git checkout agentic_ai_implementation
    Write-Host "✅ Now on agentic_ai_implementation branch" -ForegroundColor Green
} else {
    Write-Host "✅ Already on agentic_ai_implementation branch" -ForegroundColor Green
}

Write-Host ""
Write-Host "📋 Current status:" -ForegroundColor Cyan
git status --short

Write-Host ""
Write-Host "🎯 Available commands:" -ForegroundColor Cyan
Write-Host "  git add .                    # Stage all changes" -ForegroundColor White
Write-Host "  git commit -m `"message`"      # Commit changes" -ForegroundColor White
Write-Host "  git push                     # Push to agentic_ai_implementation branch" -ForegroundColor White
Write-Host ""
Write-Host "🚀 To create a PR to main:" -ForegroundColor Green
Write-Host "  Visit: https://github.com/rnerurkar/agentic_ai/compare/main...agentic_ai_implementation" -ForegroundColor Blue
