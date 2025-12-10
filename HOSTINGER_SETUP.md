# Hostinger Domain Setup: srinathkoyi.cloud

Complete guide to integrate your `srinathkoyi.cloud` domain with GitHub Pages.

## Your Domain Information
- **Domain**: srinathkoyi.cloud
- **Registrar**: Hostinger
- **Target URL**: https://srinathkoyi.cloud
- **GitHub Repository**: sree201.github.io (or srinathkoyi.github.io if you create new account)

## Step-by-Step Integration Guide

### Step 1: Access Hostinger DNS Settings

1. **Log in to Hostinger**:
   - Go to: https://hpanel.hostinger.com
   - Log in with your Hostinger account

2. **Navigate to Domain Management**:
   - Click on **"Domains"** in the left sidebar
   - Find `srinathkoyi.cloud` in your domain list
   - Click on **"Manage"** or **"DNS / Nameservers"**

3. **Access DNS Zone Editor**:
   - Look for **"DNS Zone Editor"** or **"DNS Management"**
   - Click to open DNS settings

### Step 2: Configure DNS Records for GitHub Pages

You need to add DNS records to point your domain to GitHub Pages.

#### Option A: Using CNAME Record (Recommended)

1. **Delete existing A records** (if any) for the root domain (@)

2. **Add CNAME Record**:
   - Click **"Add Record"** or **"+"** button
   - **Type**: Select **CNAME**
   - **Name/Host**: Enter `@` (or leave blank, or enter `srinathkoyi.cloud`)
   - **Points to/Value**: Enter `sree201.github.io` (or `srinathkoyi.github.io` if you have that account)
   - **TTL**: 3600 (or leave default)
   - Click **"Save"** or **"Add Record"**

   **Note**: Some registrars don't allow CNAME at root (@). If Hostinger doesn't support this, use Option B.

#### Option B: Using A Records (If CNAME not supported at root)

If Hostinger doesn't allow CNAME at root domain, use these A records:

1. **Delete any existing A records** for `@`

2. **Add Multiple A Records**:
   
   **Record 1**:
   - **Type**: A
   - **Name/Host**: `@` (or blank)
   - **Points to/Value**: `185.199.108.153`
   - **TTL**: 3600
   - Save

   **Record 2**:
   - **Type**: A
   - **Name/Host**: `@` (or blank)
   - **Points to/Value**: `185.199.109.153`
   - **TTL**: 3600
   - Save

   **Record 3**:
   - **Type**: A
   - **Name/Host**: `@` (or blank)
   - **Points to/Value**: `185.199.110.153`
   - **TTL**: 3600
   - Save

   **Record 4**:
   - **Type**: A
   - **Name/Host**: `@` (or blank)
   - **Points to/Value**: `185.199.111.153`
   - **TTL**: 3600
   - Save

   (These are GitHub Pages IP addresses)

### Step 3: (Optional) Add WWW Subdomain

If you want `www.srinathkoyi.cloud` to also work:

1. **Add CNAME Record for WWW**:
   - **Type**: CNAME
   - **Name/Host**: `www`
   - **Points to/Value**: `sree201.github.io` (or your GitHub Pages URL)
   - **TTL**: 3600
   - Save

### Step 4: Verify DNS Configuration

After adding records, verify they're correct:

**Your DNS should have**:
- ✅ CNAME record: `@` → `sree201.github.io` (OR)
- ✅ 4 A records: `@` → GitHub IPs (185.199.108.153, 185.199.109.153, 185.199.110.153, 185.199.111.153)
- ✅ (Optional) CNAME record: `www` → `sree201.github.io`

**Wait 5-10 minutes** for DNS changes to propagate.

### Step 5: Configure GitHub Pages Custom Domain

1. **Go to your GitHub repository**:
   - If using `sree201` account: https://github.com/sree201/sree201.github.io/settings/pages
   - If using `srinathkoyi` account: https://github.com/srinathkoyi/srinathkoyi.github.io/settings/pages

2. **Set Custom Domain**:
   - Scroll to **"Custom domain"** section
   - Enter: `srinathkoyi.cloud`
   - Click **"Save"**

3. **GitHub will verify the domain**:
   - This may take a few minutes
   - You'll see a checkmark when verified ✅

4. **Enable HTTPS** (after verification):
   - Check the box **"Enforce HTTPS"**
   - GitHub will automatically provision an SSL certificate
   - This may take 10-30 minutes

### Step 6: Wait for DNS Propagation

- DNS changes can take **1-24 hours** to propagate globally
- Usually it's much faster (30 minutes to 2 hours)
- Check propagation status: https://www.whatsmydns.net/#CNAME/srinathkoyi.cloud

### Step 7: Verify Your Custom Domain

1. **Test the domain**:
   - Visit: https://srinathkoyi.cloud
   - Your portfolio should load!

2. **Test HTTPS**:
   - After GitHub provisions SSL, visit: https://srinathkoyi.cloud
   - You should see a green lock icon 🔒

3. **Both URLs work**:
   - ✅ https://srinathkoyi.cloud (your custom domain)
   - ✅ https://sree201.github.io (GitHub Pages URL - will redirect)

## Hostinger-Specific Tips

### Finding DNS Settings in Hostinger

**Method 1: Via hPanel**
1. Login to hPanel
2. Domains → Your Domain → DNS Zone Editor

**Method 2: Via Hostinger Website**
1. Login to Hostinger.com
2. Go to "Domains" section
3. Click on your domain
4. Look for "DNS" or "Nameservers" option

### Common Hostinger DNS Record Types

- **A Record**: Points to IPv4 address
- **CNAME Record**: Points to another domain name
- **TXT Record**: Text records (for verification)
- **MX Record**: Mail exchange (not needed for GitHub Pages)

### If You Can't Find DNS Settings

1. **Contact Hostinger Support**:
   - They can guide you to DNS settings
   - Or they can add records for you

2. **Check Domain Status**:
   - Ensure domain is active and not expired
   - Check if domain is locked (unlock if needed)

## Troubleshooting

### Domain Not Working After 24 Hours

1. **Check DNS Records**:
   - Verify CNAME/A records are correct
   - Use: https://www.whatsmydns.net/#CNAME/srinathkoyi.cloud

2. **Check GitHub Settings**:
   - Ensure custom domain is set in GitHub Pages
   - Check for any error messages

3. **Clear Browser Cache**:
   - Try incognito/private browsing
   - Clear DNS cache: `ipconfig /flushdns` (Windows)

### HTTPS Not Available

- Wait 1-2 hours after enabling "Enforce HTTPS"
- GitHub needs time to provision SSL certificate
- Ensure DNS is fully propagated first

### CNAME File Issues

- GitHub automatically creates a `CNAME` file when you set custom domain
- Don't manually edit this file
- It should contain: `srinathkoyi.cloud`

### Hostinger DNS Not Saving

- Try refreshing the page
- Clear browser cache
- Try a different browser
- Contact Hostinger support if issues persist

## Testing Your Setup

After configuration, test these URLs:

- ✅ https://srinathkoyi.cloud (should work)
- ✅ http://srinathkoyi.cloud (should redirect to HTTPS)
- ✅ https://www.srinathkoyi.cloud (if you set up www)
- ✅ https://sree201.github.io (will redirect to custom domain)

## Quick Reference: DNS Records Summary

**For srinathkoyi.cloud pointing to GitHub Pages:**

```
Type: CNAME
Name: @
Value: sree201.github.io
TTL: 3600
```

**OR (if CNAME not supported):**

```
Type: A
Name: @
Value: 185.199.108.153

Type: A
Name: @
Value: 185.199.109.153

Type: A
Name: @
Value: 185.199.110.153

Type: A
Name: @
Value: 185.199.111.153
```

## Next Steps After Setup

1. ✅ DNS configured in Hostinger
2. ✅ Custom domain set in GitHub Pages
3. ✅ HTTPS enabled
4. ✅ Portfolio accessible at https://srinathkoyi.cloud

**Your portfolio is now live at**: https://srinathkoyi.cloud 🎉

---

## Support Resources

- **Hostinger Support**: https://www.hostinger.com/contact
- **GitHub Pages Docs**: https://docs.github.com/en/pages/configuring-a-custom-domain-for-your-github-pages-site
- **DNS Check Tool**: https://www.whatsmydns.net

---

**Need Help?** If you encounter issues, check the troubleshooting section or contact Hostinger support for DNS-related questions.

