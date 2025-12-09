# Quick Deployment Guide for sree201

## Your GitHub Information
- **Username**: sree201
- **GitHub URL**: https://github.com/sree201
- **GitHub Pages URL**: https://sree201.github.io (temporary, until custom domain is set up)
- **Custom Domain**: https://srinathkoyi.io (after domain configuration)

## Repository Name
**Recommended**: `sree201.github.io`
- This gives you the clean URL: `https://sree201.github.io` (temporary)
- Then configure custom domain: `srinathkoyi.io`

## Step 1: Create Repository on GitHub

1. Go to: https://github.com/new
2. **Repository name**: `sree201.github.io`
3. **Description**: "Professional Portfolio - Sr. Network Security Cloud Engineer"
4. Set to **Public** ✅
5. **DO NOT** check any boxes (no README, .gitignore, or license)
6. Click **"Create repository"**

## Step 2: Push Your Code

Run these commands in your terminal (you're already in the portfolio-website directory):

```bash
# Add remote repository
git remote add origin https://github.com/sree201/sree201.github.io.git

# Rename branch to main
git branch -M main

# Push to GitHub
git push -u origin main
```

**Note**: You'll be prompted for your GitHub username and password/token.

## Step 3: Enable GitHub Pages

1. Go to: https://github.com/sree201/sree201.github.io/settings/pages
2. Under **"Source"**, select:
   - **Branch**: `main`
   - **Folder**: `/ (root)`
3. Click **"Save"**

## Step 4: Access Your Live Portfolio

Your portfolio will be live at: **https://sree201.github.io**

⏱️ It may take 1-2 minutes for the site to deploy. You'll see a green checkmark when it's ready.

## Step 5: Set Up Custom Domain (srinathkoyi.io)

### Option A: If you already own srinathkoyi.io

1. **Purchase the domain** (if not already owned):
   - Go to a domain registrar (Namecheap, GoDaddy, Google Domains, etc.)
   - Purchase `srinathkoyi.io`

2. **Configure DNS Settings**:
   - Add a **CNAME record**:
     - **Type**: CNAME
     - **Name**: `@` (or root domain)
     - **Value**: `sree201.github.io`
     - **TTL**: 3600 (or default)

3. **Configure GitHub Pages Custom Domain**:
   - Go to: https://github.com/sree201/sree201.github.io/settings/pages
   - Under **"Custom domain"**, enter: `srinathkoyi.io`
   - Check **"Enforce HTTPS"** (after DNS propagates)
   - Click **"Save"**

4. **Wait for DNS Propagation**:
   - This can take 24-48 hours (usually much faster)
   - GitHub will verify the domain automatically

5. **Your portfolio will be live at**: **https://srinathkoyi.io**

### Option B: If you need to purchase the domain

**Recommended Domain Registrars**:
- **Namecheap**: https://www.namecheap.com (around $10-15/year for .io)
- **Google Domains**: https://domains.google (around $10-15/year)
- **GoDaddy**: https://www.godaddy.com (around $20-30/year)

**Steps**:
1. Purchase `srinathkoyi.io` from your chosen registrar
2. Follow Option A steps 2-5 above

## Future Updates

When you make changes to your portfolio:

```bash
git add .
git commit -m "Update portfolio"
git push
```

GitHub Pages will automatically rebuild your site!

---

## URLs

- **GitHub Pages (Temporary)**: https://sree201.github.io
- **Custom Domain (After Setup)**: https://srinathkoyi.io

**Note**: The GitHub Pages URL will continue to work even after setting up the custom domain. Both URLs will redirect to your portfolio.

