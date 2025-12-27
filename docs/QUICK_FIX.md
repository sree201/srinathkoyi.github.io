# Quick Fix: Get https://srinathkoyi.github.io

## The Problem
Your portfolio is at: `https://sree201.github.io/srinathkoyi.github.io/` ❌
You want: `https://srinathkoyi.github.io` ✅

## Solution: Create New GitHub Account

### Step 1: Check Username Availability
Visit: https://github.com/srinathkoyi
- If "404 - Not Found" → Username is available ✅
- If shows a profile → Username is taken ❌

### Step 2: Create New GitHub Account
1. Go to: https://github.com/signup
2. Username: `srinathkoyi`
3. Email: srinathkoyi5@gmail.com
4. Complete signup and verify email

### Step 3: Create Repository in New Account
1. Go to: https://github.com/new
2. Repository name: `srinathkoyi.github.io`
3. Description: "Professional Portfolio - Sr. Network Security Cloud Engineer"
4. Set to **Public** ✅
5. **DO NOT** check any boxes
6. Click **"Create repository"**

### Step 4: Update Your Local Repository

Run these commands in your `portfolio-website` folder:

```bash
# Remove old remote (if exists)
git remote remove origin

# Add new remote with new account
git remote add origin https://github.com/srinathkoyi/srinathkoyi.github.io.git

# Push to new repository
git push -u origin main
```

**Note**: You'll need to authenticate with your new `srinathkoyi` account credentials.

### Step 5: Enable GitHub Pages
1. Go to: https://github.com/srinathkoyi/srinathkoyi.github.io/settings/pages
2. Under **"Source"**, select:
   - **Branch**: `main`
   - **Folder**: `/ (root)`
3. Click **"Save"**

### Step 6: Verify
Wait 1-2 minutes, then visit: **https://srinathkoyi.github.io**

Your portfolio should be live! ✅

## Alternative: Rename Current Account

If you prefer to keep one account:

1. Go to: https://github.com/settings/admin
2. Click **"Change username"**
3. Enter: `srinathkoyi`
4. Follow GitHub's rename process

**Note**: This will change ALL your repositories under `sree201` to the new username.

---

**Target URL**: https://srinathkoyi.github.io

