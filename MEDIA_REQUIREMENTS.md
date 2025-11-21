# Codexs Telegram Bot - Media & Content Requirements

This document lists all photos, banners, and content assets needed for the bot.

---

## 📋 Overview

**Current Status:** Media is currently disabled (`ENABLE_MEDIA=false`) and using placeholder Unsplash images.

**Total Assets Needed:** 4 photos + optional welcome banner

---

## 🖼️ Required Media Assets

### 1. **About Section - Main Hero Image**
**File Name:** `about-hero.jpg` or `about-hero.png`

**Where Used:** 
- Shown at the end of the "About Codexs" section
- Displayed after all 3 text sections (Mission Control, Operating Principles, Proof of Work)

**Specifications:**
- **Dimensions:** 1200x800px (16:10 ratio) or 1600x900px
- **Format:** JPG (recommended) or PNG
- **File Size:** Under 2MB (for Telegram)
- **Style:** Professional, minimal, futuristic

**Content Description:**
- Should represent: **"Codexs launch room — async squads syncing telemetry before hand-off"**
- Visual concept: Modern workspace, remote team collaboration, tech/automation theme
- Mood: Clean, minimal, Tesla/SpaceX aesthetic
- Colors: Match Codexs brand colors (if you have them)
- Elements to include:
  - Team collaboration (can be abstract/silhouette)
  - Tech/automation elements (dashboards, code, data visualization)
  - Remote work vibe (multiple screens, global team feel)
  - Professional, futuristic atmosphere

**Caption Text (EN):** "Codexs launch room — async squads syncing telemetry before hand-off."

**Caption Text (FA):** "اتاق لانچ Codexs — هماهنگی تله‌متری تیم‌های غیرهمزمان پیش از تحویل."

---

### 2. **Update Card 1: System X Automation Layer**
**File Name:** `update-system-x.jpg` or `update-system-x.png`

**Where Used:** 
- First card in "Updates & News" section
- Accompanies the "System X Automation Layer" update

**Specifications:**
- **Dimensions:** 1200x675px (16:9 ratio) or 1600x900px
- **Format:** JPG (recommended) or PNG
- **File Size:** Under 2MB

**Content Description:**
- Should represent: **AI automation, KYC systems, fintech technology**
- Visual concept: Automation systems, data processing, AI/ML visualization
- Elements:
  - Abstract tech visualization (circuits, data flows, neural networks)
  - Fintech/security theme (subtle)
  - Modern, clean aesthetic
  - Can include code snippets, dashboards, or abstract tech graphics

**Associated Text:**
- Title: "System X Automation Layer"
- Body: "We shipped a Temporal + LLM mesh that closes the loop on KYC reviews in <4 minutes for a regulated fintech. Human supervisors now audit via a single Codexs cockpit."

---

### 3. **Update Card 2: Global Ops Pods**
**File Name:** `update-ops-pods.jpg` or `update-ops-pods.png`

**Where Used:**
- Second card in "Updates & News" section
- Accompanies the "Global Ops Pods" update

**Specifications:**
- **Dimensions:** 1200x675px (16:9 ratio) or 1600x900px
- **Format:** JPG (recommended) or PNG
- **File Size:** Under 2MB

**Content Description:**
- Should represent: **Global remote teams, international collaboration, distributed operations**
- Visual concept: World map, global connectivity, remote team pods
- Elements:
  - World map with connection lines (Dubai, Warsaw, Kuala Lumpur)
  - Remote work collaboration theme
  - International/global feel
  - Modern workspace imagery (can be abstract)
  - Team diversity representation

**Associated Text:**
- Title: "Global Ops Pods"
- Body: "New pods spun up in Dubai, Warsaw, and Kuala Lumpur give 24/6 coverage without compromising Codexs craft. Every pod pairs PM, AI lead, designer, and automation ops."

---

### 4. **Update Card 3: Culture Reel 2025**
**File Name:** `update-culture-reel.jpg` or `update-culture-reel.png`

**Where Used:**
- Third card in "Updates & News" section
- Accompanies the "Culture Reel 2025" update

**Specifications:**
- **Dimensions:** 1200x675px (16:9 ratio) or 1600x900px
- **Format:** JPG (recommended) or PNG
- **File Size:** Under 2MB

**Content Description:**
- Should represent: **Company culture, team collaboration, bilingual workflows, quality processes**
- Visual concept: Team culture, workspace, collaboration, quality focus
- Elements:
  - Team members (can be silhouettes or abstract)
  - Bilingual work environment
  - Quality/process focus
  - Modern, professional workspace
  - Can include video reel thumbnail aesthetic (play button overlay optional)

**Associated Text:**
- Title: "Culture Reel 2025"
- Body: "A two-minute reel that shows how we run bilingual standups, async critiques, and Tesla-level QA rituals from anywhere on the planet."

---

## 🎨 Optional Assets

### 5. **Welcome Banner** (Optional)
**File Name:** `welcome-banner.jpg` or `welcome-banner.png`

**Where Used:**
- Could be shown when user first starts the bot (after language selection)
- Optional enhancement for first impression

**Specifications:**
- **Dimensions:** 1200x400px (3:1 ratio) or 1600x533px
- **Format:** JPG or PNG
- **File Size:** Under 1.5MB

**Content Description:**
- Codexs logo + tagline
- "Welcome to Codexs" message
- Clean, minimal design
- Brand colors

---

## 📝 Content Guidelines

### Brand Aesthetic
- **Style:** Tesla/SpaceX-level, minimal, futuristic, professional
- **Colors:** Use Codexs brand colors (if available), or stick to:
  - Dark backgrounds with light accents
  - Or light backgrounds with dark accents
  - Avoid overly bright/saturated colors
- **Typography:** Clean, modern (if text is included in images)
- **Mood:** Professional, innovative, trustworthy, minimal

### Technical Requirements
- All images should be **high quality** but optimized for web
- **File naming:** Use lowercase with hyphens (e.g., `about-hero.jpg`)
- **Compression:** Optimize for Telegram (under 2MB per image)
- **Aspect ratios:** Maintain specified ratios for best display

### Content Themes
1. **Technology & Automation:** AI, ML, data processing, automation systems
2. **Remote Collaboration:** Global teams, async work, distributed operations
3. **Quality & Precision:** Tesla/SpaceX-level quality, attention to detail
4. **Bilingual Culture:** English/Farsi workflows, international teams
5. **Innovation:** Cutting-edge tech, modern solutions, forward-thinking

---

## 📁 File Structure

Once you have the assets, organize them like this:

```
codexs_bot/
├── media/
│   ├── about-hero.jpg
│   ├── update-system-x.jpg
│   ├── update-ops-pods.jpg
│   ├── update-culture-reel.jpg
│   └── welcome-banner.jpg (optional)
```

---

## 🔄 How to Provide Assets

**Option 1: Direct File Upload**
- Upload files to a folder in the project
- I'll update the code to reference local files or hosted URLs

**Option 2: Hosted URLs**
- Upload to your own CDN/server
- Provide me with the URLs
- I'll update the code to use those URLs

**Option 3: Cloud Storage**
- Upload to Google Drive, Dropbox, or similar
- Share the folder link
- I'll download and integrate them

---

## ✅ Checklist

Before providing assets, ensure:

- [ ] All 4 required images are created
- [ ] Images match the specified dimensions
- [ ] File sizes are under 2MB each
- [ ] Images follow the brand aesthetic (minimal, professional, futuristic)
- [ ] Images are relevant to their respective sections
- [ ] Optional welcome banner (if desired)

---

## 📧 Next Steps

1. **Create the assets** based on the descriptions above
2. **Organize them** in the file structure
3. **Share them** with me (via upload, URLs, or cloud storage)
4. **I'll integrate them** into the bot and enable media (`ENABLE_MEDIA=true`)

---

## 💡 Design Tips

- **Keep it minimal:** Less is more (Tesla/SpaceX aesthetic)
- **Focus on concept:** Abstract representations work well
- **Brand consistency:** All images should feel cohesive
- **Professional tone:** No stock photo clichés (handshakes, generic office scenes)
- **Tech-forward:** Show innovation, automation, modern tools
- **Global feel:** Represent international/remote collaboration

---

**Questions?** If any description is unclear, let me know and I can provide more specific guidance!

