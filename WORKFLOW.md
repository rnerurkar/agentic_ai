# Agentic AI Development Workflow

## 🎯 **Current Setup**
- **Default Working Branch**: `agentic_ai_implementation`
- **Production Branch**: `main`
- **Merge Strategy**: Pull Requests via GitHub

## 🔄 **Daily Workflow**

### 1. Start Working (run this when you begin)
```bash
# Check you're on the right branch
git branch --show-current

# If not on agentic_ai_implementation, switch to it
git checkout agentic_ai_implementation

# Pull latest changes
git pull origin agentic_ai_implementation
```

### 2. Make Changes
- Edit your files (notebooks, code, etc.)
- Test your changes

### 3. Commit Changes
```bash
# Stage your changes
git add .

# Commit with descriptive message
git commit -m "Add: Description of what you added/changed"

# Push to your development branch
git push origin agentic_ai_implementation
```

### 4. Create Pull Request (when ready for main)
- Visit: https://github.com/rnerurkar/agentic_ai/compare/main...agentic_ai_implementation
- Click "Create pull request"
- Add description and review changes
- Merge manually when ready

## 🛠️ **Helper Commands**

```bash
# Quick status check
git status

# See what branch you're on
git check-branch

# Push to development branch
git dev-push

# View recent commits
git log --oneline -5

# See differences from main
git diff main..agentic_ai_implementation
```

## 🚨 **Safety Checks**

✅ **Always verify you're on `agentic_ai_implementation` before committing**
✅ **Never directly push to `main` branch**  
✅ **Use GitHub PR for merging to `main`**
✅ **Pull latest changes before starting work**

## 🎉 **Quick PowerShell Helper**

Run this anytime to check your status:
```powershell
.\git-workflow.ps1
```
