#!/bin/bash
# GitHub Deployment Script for sree201
# Run these commands to deploy your portfolio to GitHub Pages

echo "Setting up GitHub repository for sree201..."

# Add remote repository
git remote add origin https://github.com/sree201/sree201.github.io.git

# Rename branch to main (GitHub standard)
git branch -M main

# Push to GitHub
git push -u origin main

echo ""
echo "✅ Code pushed successfully!"
echo ""
echo "Next steps:"
echo "1. Go to: https://github.com/sree201/sree201.github.io/settings/pages"
echo "2. Under 'Source', select: Branch 'main' and Folder '/ (root)'"
echo "3. Click 'Save'"
echo ""
echo "Your portfolio will be live at: https://sree201.github.io"
echo "(May take 1-2 minutes to deploy)"

