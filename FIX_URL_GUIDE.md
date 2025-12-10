# Fix Portfolio URL: Get https://srinathkoyi.github.io

## Current Situation
- **Current URL**: `https://sree201.github.io/srinathkoyi.github.io/` ❌
- **Desired URL**: `https://srinathkoyi.github.io` ✅

## The Problem
GitHub Pages URLs follow this pattern: `https://USERNAME.github.io/REPOSITORY-NAME/`

To get `https://srinathkoyi.github.io`, you need:
- GitHub username: `srinathkoyi`
- Repository name: `srinathkoyi.github.io`

## Solution Options

### Option 1: Create New GitHub Account (Recommended)

1. **Check if username is available**:
   - Go to: https://github.com/srinathkoyi
   - If it shows "404 - Not Found", the username is available!

2. **Create new GitHub account**:
   - Go to: https://github.com/signup
   - Username: `srinathkoyi`
   - Email: Use your email (srinathkoyi5@gmail.com)
   - Complete the signup process

3. **Transfer or recreate repository**:
   
   **Option A: Transfer repository** (if you want to keep history):
   - Go to: https://github.com/sree201/srinathkoyi.github.io/settings
   - Scroll to "Danger Zone" → "Transfer ownership"
   - Transfer to: `srinathkoyi`
   
   **Option B: Create new repository** (simpler):
   - In your new `srinathkoyi` account, create repository: `srinathkoyi.github.io`
   - Push your code to the new repository

4. **Push code to new account**:
   ```bash
   # Remove old remote
   git remote remove origin
   
   # Add new remote (with new account)
   git remote add origin https://github.com/srinathkoyi/srinathkoyi.github.io.git
   
   # Push to new repository
   git push -u origin main
   ```

5. **Enable GitHub Pages**:
   - Go to: https://github.com/srinathkoyi/srinathkoyi.github.io/settings/pages
   - Source: Branch `main`, Folder `/ (root)`
   - Save

6. **Result**: Your portfolio will be at `https://srinathkoyi.github.io` ✅

### Option 2: Rename Current GitHub Account

1. **Check if username is available**:
   - Go to: https://github.com/settings/admin
   - Click "Change username"
   - Enter: `srinathkoyi`
   - GitHub will check availability

2. **Rename account** (if available):
   - Follow GitHub's rename process
   - Note: This will change your GitHub URL to `github.com/srinathkoyi`
   - All your repositories will be under the new username

3. **Update repository**:
   - Your existing `srinathkoyi.github.io` repository will automatically work
   - Just enable GitHub Pages if not already enabled

4. **Result**: Your portfolio will be at `https://srinathkoyi.github.io` ✅

### Option 3: Use Custom Domain (Alternative)

If you can't get the `srinathkoyi` username, use a custom domain:

1. **Purchase domain**: `srinathkoyi.io` (~$10-15/year)
2. **Configure DNS**: Point to `sree201.github.io`
3. **Set custom domain in GitHub Pages**
4. **Result**: Your portfolio will be at `https://srinathkoyi.io` ✅

See `CUSTOM_DOMAIN_SETUP.md` for detailed instructions.

## Quick Fix Steps (Option 1 - New Account)

```bash
# 1. Check if username available
# Visit: https://github.com/srinathkoyi

# 2. Create new GitHub account with username: srinathkoyi

# 3. In your local portfolio folder:
cd portfolio-website

# 4. Update remote to new account
git remote remove origin
git remote add origin https://github.com/srinathkoyi/srinathkoyi.github.io.git

# 5. Push to new repository
git push -u origin main

# 6. Enable GitHub Pages in new repository settings
# Go to: https://github.com/srinathkoyi/srinathkoyi.github.io/settings/pages
```

## Important Notes

- **Option 1** (new account) is recommended if `srinathkoyi` username is available
- You can keep both GitHub accounts if needed
- Option 2 (rename) will affect all your existing repositories under `sree201`
- Option 3 (custom domain) works regardless of GitHub username

## Verification

After setup, verify:
- ✅ Portfolio loads at: `https://srinathkoyi.github.io`
- ✅ No `/srinathkoyi.github.io/` in the URL
- ✅ HTTPS is enabled (green lock icon)

---

**Target URL**: https://srinathkoyi.github.io

