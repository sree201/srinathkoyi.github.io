# Custom Domain Setup Guide: srinathkoyi.io

This guide will help you set up `srinathkoyi.io` as your custom domain for your GitHub Pages portfolio.

## Prerequisites

1. ✅ Your portfolio is deployed to GitHub Pages at `sree201.github.io`
2. ✅ You own or will purchase the domain `srinathkoyi.io`

## Step 1: Purchase the Domain (If Needed)

If you don't own `srinathkoyi.io` yet, purchase it from a domain registrar:

### Recommended Registrars:
- **Namecheap**: https://www.namecheap.com
  - Price: ~$10-15/year for .io domains
  - Good interface and support
  
- **Google Domains**: https://domains.google
  - Price: ~$10-15/year
  - Simple and reliable

- **GoDaddy**: https://www.godaddy.com
  - Price: ~$20-30/year
  - Popular but more expensive

- **Cloudflare Registrar**: https://www.cloudflare.com/products/registrar
  - Price: At-cost pricing (very affordable)
  - Great for technical users

## Step 2: Configure DNS Records

After purchasing the domain, configure DNS to point to GitHub Pages:

### DNS Configuration

1. Log into your domain registrar's DNS management panel
2. Add a **CNAME record** with these settings:

   ```
   Type: CNAME
   Name: @ (or leave blank/root)
   Value: sree201.github.io
   TTL: 3600 (or Auto/Default)
   ```

   **OR** if your registrar doesn't support CNAME at root:

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

   (These are GitHub Pages IP addresses)

3. **Save** the DNS records

## Step 3: Configure GitHub Pages Custom Domain

1. Go to your repository: https://github.com/sree201/sree201.github.io
2. Click **Settings** → **Pages** (left sidebar)
3. Under **"Custom domain"**, enter: `srinathkoyi.io`
4. Click **"Save"**
5. GitHub will create a `CNAME` file in your repository (this is automatic)

## Step 4: Wait for DNS Propagation

- DNS changes can take **24-48 hours** to propagate globally
- Usually it's much faster (1-4 hours)
- You can check propagation status at: https://www.whatsmydns.net

## Step 5: Enable HTTPS (Enforce HTTPS)

After DNS has propagated:

1. Go back to: https://github.com/sree201/sree201.github.io/settings/pages
2. Check the box **"Enforce HTTPS"**
3. GitHub will automatically provision an SSL certificate (may take a few minutes)

## Step 6: Verify Your Custom Domain

1. Visit: https://srinathkoyi.io
2. Your portfolio should load!
3. Both `https://sree201.github.io` and `https://srinathkoyi.io` will work

## Troubleshooting

### Domain Not Working After 24 Hours

1. **Check DNS Records**:
   - Verify CNAME points to `sree201.github.io`
   - Use: https://www.whatsmydns.net to check DNS propagation

2. **Check GitHub Settings**:
   - Ensure custom domain is set in GitHub Pages settings
   - Check for any error messages

3. **Clear Browser Cache**:
   - Try incognito/private browsing mode
   - Clear DNS cache: `ipconfig /flushdns` (Windows)

### HTTPS Not Available

- Wait a few hours after enabling "Enforce HTTPS"
- GitHub needs time to provision the SSL certificate
- Make sure DNS is fully propagated first

### CNAME File Issues

- GitHub automatically creates a `CNAME` file when you set a custom domain
- Don't manually edit this file unless you know what you're doing
- The file should contain: `srinathkoyi.io`

## Testing Your Setup

After setup, test these URLs:

- ✅ https://srinathkoyi.io (should work)
- ✅ https://www.srinathkoyi.io (if you set up www subdomain)
- ✅ https://sree201.github.io (will redirect to custom domain)

## Additional: WWW Subdomain (Optional)

If you want `www.srinathkoyi.io` to also work:

1. Add another CNAME record:
   ```
   Type: CNAME
   Name: www
   Value: sree201.github.io
   ```

2. In GitHub Pages settings, you can add `www.srinathkoyi.io` as an additional domain

## Cost Summary

- **Domain**: ~$10-15/year (srinathkoyi.io)
- **GitHub Pages**: Free
- **SSL Certificate**: Free (provided by GitHub)
- **Total**: ~$10-15/year

---

**Your Custom Domain**: https://srinathkoyi.io

Once set up, this will be your professional portfolio URL!

