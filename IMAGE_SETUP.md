# Image Setup Guide

## 📁 Where to Place Your Images

Create a `media` folder in your project root and place your images there:

```
codexs_bot/
├── media/
│   ├── codex-logo.png          ← CodeX logo (confirmation image)
│   └── global-ops-pods.png     ← Global Ops Pods image
```

## 🖼️ Image Files Needed

### 1. **Welcome Banner** (Hero Image)
**File Name:** `welcome-banner.png` (or `.jpg`)

**Location:** `codexs_bot/media/welcome-banner.png`

**When Used:** 
- Shown immediately after user selects their language (English or Farsi)
- First visual impression of Codexs brand
- Appears before the main menu

**Format:** PNG or JPG
**Recommended Size:** 1200x400px (3:1 ratio) or 1600x533px
**Content:** Your "CODEX - ENTER THE FUTURE" banner with futuristic design

---

### 2. **CodeX Logo** (Confirmation Image)
**File Name:** `codex-logo.png` (or `.jpg`)

**Location:** `codexs_bot/media/codex-logo.png`

**When Used:** 
- Shown after user successfully submits a job application
- Appears with caption: "Thank you for applying to Codexs. We'll be in touch soon."

**Format:** PNG or JPG
**Recommended Size:** 1200x400px or similar (will be scaled by Telegram)

---

### 3. **Global Ops Pods** (Update Card Image)
**File Name:** `global-ops-pods.png` (or `.jpg`)

**Location:** `codexs_bot/media/global-ops-pods.png`

**When Used:**
- Shown in "Updates & News" section
- Accompanies the "Global Ops Pods" update card

**Format:** PNG or JPG
**Recommended Size:** 1200x675px (16:9 ratio) or 1600x900px

---

## ✅ Setup Steps

1. **Create the media folder:**
   ```bash
   mkdir -p codexs_bot/media
   ```

2. **Add your images:**
   - Place `welcome-banner.png` in `codexs_bot/media/`
   - Place `codex-logo.png` in `codexs_bot/media/`
   - Place `global-ops-pods.png` in `codexs_bot/media/`

3. **Enable media in .env:**
   ```
   ENABLE_MEDIA=true
   ```

4. **Restart the bot:**
   The bot will automatically detect and use these images.

---

## 🔍 File Name Requirements

The bot looks for these exact file names:
- `welcome-banner.png` (or `.jpg`) - for welcome screen
- `codex-logo.png` (or `.jpg`) - for confirmation
- `global-ops-pods.png` (or `.jpg`) - for updates

**Note:** The bot will try both `.png` and `.jpg` extensions automatically.

---

## 🧪 Testing

After adding images:

1. **Test welcome banner:**
   - Start the bot with `/start`
   - Select a language (English or Farsi)
   - You should see the welcome banner with "CODEX - ENTER THE FUTURE" design

2. **Test confirmation image:**
   - Submit a job application
   - You should see the CodeX logo with thank you message

3. **Test Global Ops Pods:**
   - Go to "Updates & News" menu
   - You should see the Global Ops Pods card with your image

---

## ❌ Removed Images

The following images have been removed (no longer needed):
- About section hero image
- System X Automation Layer card image
- Culture Reel 2025 card image

These sections will now display as text-only.

---

## 📝 Notes

- If an image file is missing, the bot will gracefully fall back to text-only
- Images are optional - the bot works fine without them
- Make sure file names match exactly (case-sensitive on some systems)

