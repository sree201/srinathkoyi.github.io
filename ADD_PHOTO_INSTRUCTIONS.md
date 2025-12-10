# How to Add Your Photo to the Portfolio

## Quick Steps

1. **Prepare Your Photo**:
   - Use a professional headshot or portrait
   - Recommended size: 600x600 pixels (square)
   - File format: JPG, PNG, or WebP
   - File size: Keep under 500KB for fast loading

2. **Name Your Photo**:
   - Name it: `profile-photo.jpg` (or `.png` if PNG format)
   - Place it in the `portfolio-website` folder

3. **Update HTML (if using different filename)**:
   - If your photo has a different name, edit `index.html`
   - Find: `<img src="profile-photo.jpg"`
   - Change to your photo filename

4. **Push to GitHub**:
   ```bash
   cd portfolio-website
   git add profile-photo.jpg
   git add index.html
   git commit -m "Add profile photo"
   git push
   ```

## Detailed Instructions

### Step 1: Prepare Your Photo

**Best Practices**:
- **Size**: 600x600 pixels (square format works best)
- **Format**: JPG (best compression) or PNG (if you need transparency)
- **File Size**: Under 500KB for fast loading
- **Quality**: Professional headshot or portrait
- **Background**: Solid color or professional background

**Tools to Resize**:
- Online: https://www.iloveimg.com/resize-image
- Windows: Paint or Photos app
- Mac: Preview
- Online: https://www.photopea.com (free Photoshop alternative)

### Step 2: Add Photo to Portfolio Folder

1. **Copy your photo** to the `portfolio-website` folder
2. **Rename it** to `profile-photo.jpg` (or keep your name and update HTML)

**Location**:
```
portfolio-website/
├── index.html
├── styles.css
├── script.js
├── profile-photo.jpg  ← Your photo here
└── ...
```

### Step 3: Update HTML (If Needed)

**If your photo is named `profile-photo.jpg`**: No changes needed! ✅

**If your photo has a different name**:
1. Open `index.html`
2. Find this line (around line 55):
   ```html
   <img src="profile-photo.jpg" alt="Srinath Koyi - Sr. Network Security Cloud Engineer" id="profile-img">
   ```
3. Change `profile-photo.jpg` to your actual filename
4. Save the file

**Supported formats**:
- `profile-photo.jpg` ✅
- `profile-photo.png` ✅
- `profile-photo.webp` ✅
- `srinath-photo.jpg` ✅ (just update HTML)

### Step 4: Test Locally

1. **Open `index.html`** in your browser
2. **Check if your photo appears** in the hero section
3. **Verify it looks good** (circular, centered, good quality)

### Step 5: Push to GitHub

```bash
# Navigate to portfolio folder
cd portfolio-website

# Add your photo
git add profile-photo.jpg

# Add updated HTML (if you changed it)
git add index.html

# Commit changes
git commit -m "Add profile photo"

# Push to GitHub
git push
```

### Step 6: Verify on Live Site

After pushing (wait 1-2 minutes for GitHub Pages to update):

1. Visit: `https://srinathkoyi.cloud`
2. Check if your photo appears in the hero section
3. Verify it looks professional and loads quickly

## Troubleshooting

### Photo Not Showing

**Check 1: File Name**
- Ensure filename matches exactly (case-sensitive)
- Check file extension (.jpg vs .JPG)

**Check 2: File Location**
- Photo must be in `portfolio-website` folder (same as index.html)
- Not in a subfolder

**Check 3: File Format**
- Use JPG, PNG, or WebP
- Avoid formats like HEIC, TIFF, etc.

**Check 4: Browser Cache**
- Clear browser cache (Ctrl+Shift+Delete)
- Try incognito mode

### Photo Looks Distorted

**Fix**: Use a square photo (1:1 aspect ratio)
- Recommended: 600x600 pixels
- Or crop your photo to square format

### Photo Too Large/Slow Loading

**Fix**: Compress your photo
- Use: https://tinypng.com (free compression)
- Or: https://squoosh.app (Google's tool)
- Target: Under 500KB

### Placeholder Still Showing

**Possible Causes**:
1. Photo file not uploaded to GitHub
2. Wrong filename in HTML
3. Photo failed to load (check browser console F12)

**Fix**:
- Check browser console (F12) for errors
- Verify photo is in GitHub repository
- Check filename matches exactly

## Alternative: Use Online Photo URL

If you want to host your photo elsewhere (e.g., Imgur, Google Drive):

1. Upload your photo to an image hosting service
2. Get the direct image URL
3. Update `index.html`:
   ```html
   <img src="https://your-image-url.com/photo.jpg" alt="Srinath Koyi" id="profile-img">
   ```

**Recommended Services**:
- **Imgur**: https://imgur.com (free, reliable)
- **Cloudinary**: https://cloudinary.com (free tier available)
- **GitHub**: Upload to your repository and use raw URL

## Example File Structure

```
portfolio-website/
├── index.html          ← Updated to use your photo
├── styles.css          ← Updated CSS for photo display
├── script.js           ← Updated to handle photo loading
├── profile-photo.jpg   ← YOUR PHOTO HERE
├── README.md
└── ...
```

## Quick Reference

**Current Setup**:
- Photo filename: `profile-photo.jpg`
- Location: Same folder as `index.html`
- Format: JPG, PNG, or WebP
- Size: Recommended 600x600px, under 500KB

**To Change Photo**:
1. Replace `profile-photo.jpg` with new photo
2. Keep same filename OR update HTML
3. Push to GitHub

---

**Your portfolio will look much more professional with your photo!** 📸

After adding your photo, your hero section will display your professional image instead of the placeholder icon.

