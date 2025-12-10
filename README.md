# Portfolio Website - Srinath Koyi

A modern, responsive portfolio website showcasing professional experience, skills, and projects.

## Features

- **Responsive Design**: Works seamlessly on desktop, tablet, and mobile devices
- **Modern UI**: Dark theme with gradient accents and smooth animations
- **Smooth Scrolling**: Navigation with smooth scroll effects
- **Interactive Elements**: Hover effects, animations, and mobile menu
- **Professional Sections**:
  - Hero section with introduction
  - About section with professional summary
  - Skills section with categorized technologies
  - Projects section with featured work
  - Contact section with social links

## Getting Started

1. **Open the Website**:
   - Simply open `index.html` in your web browser
   - Or use a local server (recommended):
     ```bash
     # Using Python
     python -m http.server 8000
     
     # Using Node.js (if you have http-server installed)
     npx http-server
     ```

2. **View the Portfolio**:
   - Navigate to `http://localhost:8000` (or the port you specified)
   - The website will load with all your information

## Customization

### Update Profile Picture
Replace the profile placeholder icon by:
1. Adding your photo to the `portfolio-website` folder
2. Updating the `.profile-placeholder` in `styles.css` to use your image:
   ```css
   .profile-placeholder {
       background-image: url('your-photo.jpg');
       background-size: cover;
       background-position: center;
   }
   ```

### Update Project Links
Edit the project links in `index.html`:
- Replace `#` with your actual GitHub repository URLs
- Add live demo links if available

### Modify Colors
Update the color scheme in `styles.css` by changing the CSS variables:
```css
:root {
    --primary-color: #6366f1;
    --secondary-color: #8b5cf6;
    /* ... other colors */
}
```

## File Structure

```
portfolio-website/
├── index.html      # Main HTML file
├── styles.css      # All styling and responsive design
├── script.js       # Interactive features and animations
└── README.md       # This file
```

## Technologies Used

- HTML5
- CSS3 (with CSS Grid and Flexbox)
- JavaScript (Vanilla JS)
- Font Awesome Icons (via CDN)

## Browser Support

- Chrome (latest)
- Firefox (latest)
- Safari (latest)
- Edge (latest)

## Deployment

### GitHub Pages (Recommended)

1. **Initial Setup**: Deploy to GitHub Pages at `sree201.github.io`
   - See `DEPLOY.md` for step-by-step instructions
   
2. **Custom Domain**: Set up `srinathkoyi.io` as your custom domain
   - See `CUSTOM_DOMAIN_SETUP.md` for detailed instructions
   - Requires purchasing the domain (~$10-15/year)
   - GitHub provides free SSL certificate

### Other Hosting Options

- **Netlify**: Drag and drop the folder to Netlify
- **Vercel**: Connect your GitHub repository
- **AWS S3**: Upload files to an S3 bucket with static website hosting

## Contact Information

- **Name**: Srinath Koyi
- **Title**: Sr. Network Security Cloud Engineer
- **Email**: srinathkoyi5@gmail.com
- **Phone**: +1 (657) 877-9052
- **Location**: Los Angeles, CA, USA
- **LinkedIn**: [Srinath Koyi](https://www.linkedin.com/in/srinath-k-6572389590s/)
- **Portfolio URL**: https://srinathkoyi.cloud (custom domain from Hostinger ✅)
- **GitHub**: [sree201](https://github.com/sree201)

---

© 2024 Srinath Koyi. All rights reserved.

