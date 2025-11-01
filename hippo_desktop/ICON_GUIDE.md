# Application Icon Guide

## Icon Files You Need to Create

Your `hippo_desktop` folder needs these icon files:

```
hippo_desktop/
├── assets/
│   ├── icon.png              ← 1024x1024 PNG (master icon)
│   ├── tray-icon.png         ← 256x256 PNG (system tray)
│   └── dmg-background.png    ← 540x380 PNG (macOS installer background)
│
└── build/
    ├── icon.icns             ← macOS icon (all sizes)
    ├── icon.ico              ← Windows icon (all sizes)
    └── icons/                ← Linux icons
        ├── 16x16.png
        ├── 32x32.png
        ├── 48x48.png
        ├── 64x64.png
        ├── 128x128.png
        ├── 256x256.png
        └── 512x512.png
```

## Quick Creation Process

### Step 1: Design Master Icon (1024x1024 PNG)

Create ONE high-resolution icon: `assets/icon.png` (1024x1024 pixels)

**Design Guidelines:**
- **Simple**: Recognizable at small sizes (16x16)
- **Distinctive**: Unique from other medical apps
- **Professional**: Not clipart or emoji
- **Clear**: Good contrast, no fine details
- **Meaningful**: Represents brain/hippocampus/analysis

**Color Scheme Ideas:**
- Medical Blue: `#4A90E2` (trust, medical)
- Neuroscience Purple: `#667eea` (matches your app)
- Scientific Green: `#48bb78` (growth, biology)
- Modern Gradient: Blue → Purple

### Step 2: Create System Tray Icon (256x256 PNG)

Create `assets/tray-icon.png` (256x256 pixels)

**Special Requirements:**
- **Simpler** than main icon
- **Monochrome** or very simple color
- **Square aspect ratio**
- Looks good at 16x16 (final display size)

**macOS Tray Icon:**
- Filename: `tray-icon-Template.png`
- Must be **black on transparent**
- macOS will auto-invert for dark mode

### Step 3: Convert to Platform Formats

Use online tools to convert your master icon:

#### For macOS (.icns):

**Online Tool:** https://cloudconvert.com/png-to-icns

```bash
# Upload: assets/icon.png (1024x1024)
# Download: build/icon.icns
```

**Or use command line (macOS only):**
```bash
# Create iconset folder
mkdir icon.iconset

# Generate all sizes
sips -z 16 16     icon.png --out icon.iconset/icon_16x16.png
sips -z 32 32     icon.png --out icon.iconset/icon_16x16@2x.png
sips -z 32 32     icon.png --out icon.iconset/icon_32x32.png
sips -z 64 64     icon.png --out icon.iconset/icon_32x32@2x.png
sips -z 128 128   icon.png --out icon.iconset/icon_128x128.png
sips -z 256 256   icon.png --out icon.iconset/icon_128x128@2x.png
sips -z 256 256   icon.png --out icon.iconset/icon_256x256.png
sips -z 512 512   icon.png --out icon.iconset/icon_256x256@2x.png
sips -z 512 512   icon.png --out icon.iconset/icon_512x512.png
sips -z 1024 1024 icon.png --out icon.iconset/icon_512x512@2x.png

# Convert to .icns
iconutil -c icns icon.iconset -o build/icon.icns
```

#### For Windows (.ico):

**Online Tool:** https://cloudconvert.com/png-to-ico

```bash
# Upload: assets/icon.png (1024x1024)
# Settings: Include sizes 16, 24, 32, 48, 64, 256
# Download: build/icon.ico
```

**Or use ImageMagick:**
```bash
# Install ImageMagick
brew install imagemagick  # macOS
sudo apt install imagemagick  # Linux

# Convert
convert icon.png -define icon:auto-resize=256,128,64,48,32,16 build/icon.ico
```

#### For Linux (PNG files):

**Use ImageMagick to resize:**
```bash
# Create icons directory
mkdir -p build/icons

# Generate all sizes
convert icon.png -resize 16x16     build/icons/16x16.png
convert icon.png -resize 32x32     build/icons/32x32.png
convert icon.png -resize 48x48     build/icons/48x48.png
convert icon.png -resize 64x64     build/icons/64x64.png
convert icon.png -resize 128x128   build/icons/128x128.png
convert icon.png -resize 256x256   build/icons/256x256.png
convert icon.png -resize 512x512   build/icons/512x512.png
```

**Or use online batch resizer:** https://www.iloveimg.com/resize-image

## Design Tools

### Free Tools:

1. **Figma** (Web-based) - https://figma.com
   - Professional design tool
   - Templates available
   - Export to PNG

2. **Inkscape** (Desktop) - https://inkscape.org
   - Vector graphics editor
   - Free and open source
   - Export to PNG at any size

3. **GIMP** (Desktop) - https://www.gimp.org
   - Photo editor
   - Free alternative to Photoshop
   - Supports all formats

4. **Canva** (Web) - https://canva.com
   - Easy templates
   - Drag-and-drop
   - Free tier available

### Quick Icon Templates:

**Medical App Icon Template (Figma):**
https://www.figma.com/community/file/medical-app-icons

**App Icon Generator:**
https://appicon.co/ (upload one image, get all sizes)

**Icon Kitchen (Android-style but works):**
https://icon.kitchen/

## Example: Creating NeuroInsight Icon

### Design Concept:

```
┌─────────────────────────────────┐
│                                 │
│    Circular badge (gradient)    │
│    ┌─────────────────┐         │
│    │   Purple → Blue  │         │
│    │                  │         │
│    │      🧠 or       │         │
│    │   Hippocampus    │         │
│    │      shape       │         │
│    │                  │         │
│    │       NI         │         │
│    │   (small text)   │         │
│    └─────────────────┘         │
│                                 │
└─────────────────────────────────┘

Colors:
- Primary: #667eea (purple)
- Secondary: #4A90E2 (blue)
- Accent: White or #48bb78 (green)
```

### Using Free Stock Icons:

**Option 1: Noun Project** (simple icons)
1. Go to https://thenounproject.com/
2. Search "brain" or "hippocampus"
3. Download free PNG
4. Add background and customize

**Option 2: Flaticon** (flat design)
1. Go to https://www.flaticon.com/
2. Search "brain medical"
3. Download free icon
4. Customize colors

**Option 3: Icons8** (modern icons)
1. Go to https://icons8.com/
2. Search "brain"
3. Customize online
4. Download PNG

### Simple DIY in PowerPoint/Keynote:

```
1. Create 1024x1024 canvas
2. Insert circle shape (gradient fill: purple to blue)
3. Insert brain emoji 🧠 or download brain SVG
4. Resize to fit in circle
5. Add "NI" text (optional)
6. Export as PNG
```

## Testing Your Icons

### Preview at Different Sizes:

```bash
# Create test montage
convert icon.png -resize 512x512 icon-512.png
convert icon.png -resize 256x256 icon-256.png
convert icon.png -resize 128x128 icon-128.png
convert icon.png -resize 64x64 icon-64.png
convert icon.png -resize 32x32 icon-32.png
convert icon.png -resize 16x16 icon-16.png

montage icon-*.png -geometry +10+10 -background white icon-preview.png
```

**Check:**
- ✓ Recognizable at 16x16?
- ✓ Not too busy or detailed?
- ✓ Clear contrast?
- ✓ Looks professional?

## Placeholder Icons (for testing)

**If you want to test the app before creating final icons:**

### Temporary Placeholder:

Use a simple colored circle with text:

```bash
# Create placeholder (requires ImageMagick)
convert -size 1024x1024 xc:transparent \
  -fill "#667eea" -draw "circle 512,512 512,100" \
  -fill white -font Arial -pointsize 300 \
  -gravity center -annotate +0+0 "NI" \
  assets/icon.png
```

**Or download a placeholder:**
- https://via.placeholder.com/1024x1024/667eea/ffffff?text=NI
- Save as `assets/icon.png`

## What Happens If You Don't Have Icons?

**Build will fail** with error:
```
Error: Cannot find icon at build/icon.icns
```

**Temporary workaround** (testing only):
```javascript
// In package.json, disable code signing
"build": {
  "mac": {
    "icon": null  // Remove icon requirement
  },
  "win": {
    "icon": null
  }
}
```

But app will show **generic icon** - looks unprofessional!

## Professional Icon Design Services

If you want a professional custom icon:

**Affordable:**
- **Fiverr**: $5-50 (search "app icon design")
- **99designs**: $299+ (contest with multiple designers)
- **Upwork**: $50-200 (hire designer)

**Premium:**
- **Dribbble**: $500-2000 (top designers)
- **Design studio**: $1000-5000 (full branding)

**AI-Generated** (experimental):
- **DALL-E**: https://labs.openai.com/
- **Midjourney**: https://midjourney.com/
- Prompt: "Modern minimalist app icon for brain analysis software, purple and blue gradient, professional medical design, 3D"

## Quick Start (5 minutes)

**Fastest way to get started:**

1. **Go to:** https://appicon.co/
2. **Upload:** Any brain image (1024x1024)
3. **Click:** "Generate"
4. **Download:** All sizes
5. **Extract to:** `hippo_desktop/build/`

Done! Now you can build the app.

## Icon Checklist

Before building:

- [ ] Created `assets/icon.png` (1024x1024)
- [ ] Created `assets/tray-icon.png` (256x256)
- [ ] Generated `build/icon.icns` (macOS)
- [ ] Generated `build/icon.ico` (Windows)
- [ ] Generated `build/icons/*.png` (Linux, 7 sizes)
- [ ] Tested at small sizes (16x16)
- [ ] Looks professional and clear
- [ ] Matches brand/app purpose

## Resources

- **Icon converter:** https://cloudconvert.com/
- **Resize tool:** https://www.iloveimg.com/resize-image
- **Icon generator:** https://appicon.co/
- **Free icons:** https://thenounproject.com/
- **Design tool:** https://www.figma.com/
- **AI generator:** https://labs.openai.com/

---

**Quick Tip:** Start with a simple, clear design. You can always refine it later. A simple circle with "NI" text is better than no icon!


