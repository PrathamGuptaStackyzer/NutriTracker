# Assets Folder

Place your logo and images here.

## Required Assets

### logo.png
- **Size:** 80x80px or higher (will be scaled)
- **Format:** PNG with transparent background
- **Design:** Bowl with food icon (🍱 emoji is used as placeholder)
- **Colors:** Should work well on white background

## Current Status
Using emoji as placeholder (🍱). Replace with actual logo when ready.

## How to Add Logo
1. Save your logo as `logo.png` in this folder
2. Update `index.html` line with logo:
   ```html
   <div class="logo-icon">🍱</div>
   ```
   Replace with:
   ```html
   <img src="assets/logo.png" alt="NutriTracker Logo" class="logo-icon">
   ```
3. Update CSS in `style.css` for `.logo-icon` to handle image instead of emoji
