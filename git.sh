#!/bin/bash
cd "/c/Users/Jonas/code/vscode/quant_fin"

# Initialize or use the existing repository
git init

# Remove a problematic file named "nul" if it exists.
if [ -e "nul" ]; then
    echo "Removing problematic file: nul"
    rm -f "nul"
    git rm --cached "nul" 2>/dev/null
fi

# If remote "origin" exists, remove it
if git remote | grep -q "^origin$"; then
    git remote remove origin
fi

# Add the proper remote URL using SSH (ensure your SSH keys are configured)
git remote add origin git@github.com:IO-n-A/quant_fin.git

git add .
# Parameterize the commit message, defaulting to a message if not provided
COMMIT_MESSAGE=${COMMIT_MESSAGE:-"Auto commit: $(date)"}
git commit -m "$COMMIT_MESSAGE"

git branch -M io-n-a

# Pull the latest changes from the remote io-n-a branch, rebasing your commit on top
git pull --rebase origin io-n-a

# Push your changes to the remote io-n-a branch
git push -u origin io-n-a