# GitHub Pages Deployment Guide

## Professional Repository Name Options

Here are some professional repository name suggestions for your portfolio:

### Option 1: Personal Domain (Recommended)
**Repository Name**: `srinathkoyi.github.io`
- **URL**: `https://srinathkoyi.github.io`
- **Pros**: Clean, professional URL that's easy to remember
- **Note**: Must match your GitHub username exactly

### Option 2: Portfolio Name
**Repository Name**: `portfolio` or `srinath-koyi-portfolio`
- **URL**: `https://srinathkoyi.github.io/portfolio`
- **Pros**: Simple and clear
- **Cons**: Longer URL

### Option 3: Professional Website
**Repository Name**: `srinath-koyi-website` or `srinath-koyi-dev`
- **URL**: `https://srinathkoyi.github.io/srinath-koyi-website`
- **Pros**: Descriptive and professional

## Recommended: `srinathkoyi.github.io`

This is the most professional option as it gives you a clean URL: `https://srinathkoyi.github.io`

## Step-by-Step Deployment Instructions

### Step 1: Create Repository on GitHub

1. Go to [GitHub.com](https://github.com) and sign in
2. Click the **"+"** icon in the top right → **"New repository"**
3. **Repository name**: Enter `srinathkoyi.github.io` (or your chosen name)
4. **Description**: "Professional Portfolio - Sr. Network Security Cloud Engineer"
5. Set visibility to **Public** (required for free GitHub Pages)
6. **DO NOT** initialize with README, .gitignore, or license (we already have these)
7. Click **"Create repository"**

### Step 2: Push Your Code to GitHub

Run these commands in your terminal (you're already in the portfolio-website directory):

```bash
# Add all files
git add .

# Commit the files
git commit -m "Initial commit: Portfolio website"

# Add your GitHub repository as remote (replace YOUR_USERNAME with your GitHub username)
git remote add origin https://github.com/YOUR_USERNAME/srinathkoyi.github.io.git

# Push to GitHub
git branch -M main
git push -u origin main
```

**Example** (if your username is `srinathkoyi`):
```bash
git remote add origin https://github.com/srinathkoyi/srinathkoyi.github.io.git
git branch -M main
git push -u origin main
```

### Step 3: Enable GitHub Pages

1. Go to your repository on GitHub
2. Click **Settings** (top menu)
3. Scroll down to **Pages** (left sidebar)
4. Under **Source**, select:
   - **Branch**: `main`
   - **Folder**: `/ (root)`
5. Click **Save**

### Step 4: Access Your Live Portfolio

- Your portfolio will be live at: `https://YOUR_USERNAME.github.io`
- It may take 1-2 minutes to deploy
- You'll see a green checkmark when deployment is complete

## Updating Your Portfolio

Whenever you make changes:

```bash
# Navigate to portfolio directory
cd portfolio-website

# Add changes
git add .

# Commit changes
git commit -m "Update portfolio content"

# Push to GitHub
git push
```

GitHub Pages will automatically rebuild your site (usually takes 1-2 minutes).

## Custom Domain (Optional)

If you have a custom domain (e.g., `srinathkoyi.com`):

1. In GitHub Pages settings, add your custom domain
2. Update your domain's DNS records:
   - Add a CNAME record pointing to `YOUR_USERNAME.github.io`
3. GitHub will provide instructions for verification

## Troubleshooting

### Site Not Loading
- Wait 2-3 minutes after enabling Pages
- Check repository Settings → Pages to ensure it's enabled
- Verify the repository is Public

### Changes Not Showing
- Clear browser cache (Ctrl+F5)
- Check GitHub Actions tab for build status
- Ensure you pushed to the `main` branch

### 404 Error
- Verify `index.html` is in the root directory
- Check repository name matches username (for .github.io format)

## Quick Reference Commands

```bash
# Initial setup (one time)
cd portfolio-website
git add .
git commit -m "Initial commit: Portfolio website"
git remote add origin https://github.com/YOUR_USERNAME/srinathkoyi.github.io.git
git branch -M main
git push -u origin main

# Future updates
git add .
git commit -m "Description of changes"
git push
```

---

**Your portfolio will be live at**: `https://YOUR_USERNAME.github.io`

Replace `YOUR_USERNAME` with your actual GitHub username!

