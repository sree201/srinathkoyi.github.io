# Fix DNS and HTTPS for srinathkoyi.cloud

## Current Issues

1. ❌ **www CNAME is wrong**: Points to `srinathkoyi.github.io` (doesn't exist)
2. ⚠️ **Conflicting records**: Both ALIAS and A records for `@` (can cause issues)
3. ❌ **HTTPS not working**: "Not secure" warning in browser

## Step 1: Fix DNS Records in Hostinger

### Remove Conflicting Records

You currently have BOTH ALIAS and A records for `@`. You need to choose ONE method:

**Recommended: Keep ALIAS, Remove A Records**

1. **Delete these 4 A records** (they conflict with ALIAS):
   - A record: `@` → `185.199.108.153` ❌ DELETE
   - A record: `@` → `185.199.109.153` ❌ DELETE
   - A record: `@` → `185.199.110.153` ❌ DELETE
   - A record: `@` → `185.199.111.153` ❌ DELETE

2. **Keep this ALIAS record**:
   - ALIAS: `@` → `sree201.github.io` ✅ KEEP

3. **Fix the www CNAME**:
   - Current: CNAME `www` → `srinathkoyi.github.io` ❌ WRONG
   - Change to: CNAME `www` → `sree201.github.io` ✅ CORRECT

### Correct DNS Configuration

After cleanup, you should have ONLY these records:

```
ALIAS    @     →  sree201.github.io    3600
CNAME    www   →  sree201.github.io    3600
```

**That's it!** No A records needed when using ALIAS.

## Step 2: Fix GitHub Pages Settings

1. **Go to your repository**:
   - https://github.com/sree201/sree201.github.io/settings/pages
   - (Or whatever your actual repository name is)

2. **Check Custom Domain**:
   - Under "Custom domain", it should show: `srinathkoyi.cloud`
   - If it's empty or wrong, enter: `srinathkoyi.cloud`
   - Click **"Save"**

3. **Wait for Domain Verification**:
   - GitHub will verify the domain (may take 5-10 minutes)
   - You'll see a checkmark ✅ when verified

4. **Enable HTTPS** (CRITICAL):
   - After domain is verified, check the box **"Enforce HTTPS"**
   - GitHub will provision an SSL certificate
   - This may take 10-30 minutes

## Step 3: Wait for Changes to Propagate

1. **DNS Propagation**: 30 minutes to 2 hours
2. **SSL Certificate**: 10-30 minutes after enabling "Enforce HTTPS"
3. **Total wait time**: Up to 2-3 hours for everything to work

## Step 4: Verify Everything Works

### Check DNS Propagation
Visit: https://www.whatsmydns.net/#CNAME/srinathkoyi.cloud

### Test Your Site
1. Clear browser cache (Ctrl+Shift+Delete)
2. Try incognito/private browsing
3. Visit: https://srinathkoyi.cloud
4. You should see:
   - ✅ Green lock icon 🔒
   - ✅ "Secure" or no warning
   - ✅ Your portfolio loads correctly

## Troubleshooting

### Still Getting "Not Secure" Warning

**Check 1: Is HTTPS Enforced in GitHub?**
- Go to: https://github.com/sree201/sree201.github.io/settings/pages
- Ensure "Enforce HTTPS" is checked ✅
- If unchecked, check it and wait 30 minutes

**Check 2: Is Certificate Provisioned?**
- In GitHub Pages settings, look for certificate status
- Should show "Certificate is valid" or similar
- If it shows an error, wait longer or contact GitHub support

**Check 3: Mixed Content Issues**
- Open browser console (F12)
- Look for errors about "mixed content" or "insecure resources"
- If found, your HTML/CSS might be loading HTTP resources

**Check 4: DNS Not Fully Propagated**
- Use: https://www.whatsmydns.net/#CNAME/srinathkoyi.cloud
- If not all locations show `sree201.github.io`, wait longer

### Site Not Loading at All

1. **Check DNS Records**:
   - Ensure ALIAS `@` → `sree201.github.io` exists
   - Ensure CNAME `www` → `sree201.github.io` exists
   - Remove all A records for `@`

2. **Check GitHub Repository**:
   - Ensure repository exists: `sree201.github.io` (or your actual repo name)
   - Ensure GitHub Pages is enabled
   - Ensure files are in the `main` branch

3. **Clear Everything**:
   ```bash
   # Clear DNS cache (Windows)
   ipconfig /flushdns
   
   # Clear browser cache
   # Use Ctrl+Shift+Delete or incognito mode
   ```

## Quick Fix Checklist

- [ ] Removed 4 A records for `@` in Hostinger
- [ ] Kept ALIAS `@` → `sree201.github.io` in Hostinger
- [ ] Fixed CNAME `www` → `sree201.github.io` in Hostinger
- [ ] Set custom domain to `srinathkoyi.cloud` in GitHub Pages
- [ ] Enabled "Enforce HTTPS" in GitHub Pages
- [ ] Waited 30 minutes for DNS propagation
- [ ] Waited 30 minutes for SSL certificate
- [ ] Cleared browser cache
- [ ] Tested in incognito mode

## Expected Final DNS Configuration

In Hostinger DNS Zone Editor, you should see:

```
Type      Name    TTL    Value
-----     ----    ---    -----
ALIAS     @       3600   sree201.github.io
CNAME     www     3600   sree201.github.io
```

**That's all you need!**

---

## Still Having Issues?

1. **Screenshot your Hostinger DNS settings** and share
2. **Screenshot your GitHub Pages settings** and share
3. **Check browser console** (F12) for any errors
4. **Wait longer** - DNS and SSL can take time

---

**Your site should work at**: https://srinathkoyi.cloud (with green lock 🔒)

