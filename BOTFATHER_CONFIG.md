# BotFather Configuration Guide

This document provides the exact text to use in BotFather for your Codexs bot.

**⚠️ Important Branding Note:** All user-facing text should use **"Codexs"** (without ".ai"). Only URLs and email addresses should include "codexs.ai" (e.g., `https://codexs.ai`, `contact@codexs.ai`).

---

## 🤖 Bot Name

**Field:** Bot Name (in "Info" section)

**Text:**
```
Codexs Assistant
```

**Alternative (if you prefer shorter):**
```
Codexs
```

---

## 📝 Bot Description

**Field:** Description (in "Info" section - the large text area)

**Text:**
```
AI-powered gateway to Codexs – apply for remote roles, explore projects, and contact our team.
```

**Alternative (more detailed):**
```
Codexs Assistant – Your fast lane into our global digital studio. Apply for remote roles, discover AI-driven projects, and connect with our team.
```

---

## 👋 Welcome Message

**Field:** "What can this bot do?" (in "Welcome message" section)

**Text:**
```
Meet the Codexs Assistant, your fast lane into our global digital studio.

• Apply for remote roles in tech, design & operations
• Discover how we build AI-driven products and systems
• Get news and project updates from the Codexs team
• Reach support when you need a real human

Bilingual support: English & Farsi
```

**Alternative (shorter version):**
```
Welcome to Codexs – global automation studio.

• 💼 Apply for remote roles
• 🏢 Learn about our projects
• 📢 Get updates & news
• 📞 Contact our team

Bilingual: English & Farsi
```

---

## 🖼️ Welcome Picture (Optional)

**Field:** "Set Welcome Picture" button

**Recommendation:**
- Use the Codexs logo
- Or a clean, minimal banner with "Codexs" branding
- Dimensions: 640x360px (16:9 ratio) works well
- Keep it simple and professional

**If you don't have one:** You can skip this for now and add it later.

---

## 📋 Complete BotFather Setup Checklist

### Step 1: Basic Info
- [ ] **Bot Name:** `Codexs Assistant`
- [ ] **Description:** `AI-powered gateway to Codexs – apply for remote roles, explore projects, and contact our team.`

### Step 2: Welcome Message
- [ ] **"What can this bot do?"** field: Copy the welcome message text above
- [ ] **Welcome Picture:** (Optional) Upload Codexs logo/banner

### Step 3: Bot Settings
- [ ] **Allow Groups:** ✅ Enabled (so bot can post in your group)
- [ ] **Group Admin Rights:** ✅ Enabled (so bot can send messages in group)
- [ ] **Privacy Mode:** ⚠️ Disabled (so bot can see all messages in groups)

### Step 4: Commands (Optional but Recommended)
Set up these commands in BotFather:

```
start - Start the bot and select language
menu - Return to main menu
help - Show help information
commands - List available shortcuts
```

---

## 🎯 Bot Commands (Required)

In BotFather, use `/setcommands` and paste this **exact format**:

```
start - Start the Codexs Assistant and select your language
menu - Return to the main menu
help - Get help and see what I can do for you
```

**How to set commands:**
1. Open BotFather in Telegram
2. Send: `/setcommands`
3. Select your bot (@your_bot_name)
4. Paste the commands above (one per line, format: `command - description`)
5. Send the message

**Note:** The commands file is also saved as `BOTFATHER_COMMANDS.txt` in your project folder for easy copy-paste.

---

## 📝 Notes

1. **Description Length:** BotFather has a character limit for descriptions. The provided text should fit comfortably.

2. **Welcome Message:** This appears when users first open your bot. Keep it clear and action-oriented.

3. **Bilingual Note:** Since your bot supports English and Farsi, you can mention it in the welcome message (as shown above).

4. **Brand Consistency:** Make sure the text matches your brand voice (Tesla/SpaceX-level, minimal, professional).

---

## ✅ After Configuration

Once you've updated BotFather:

1. The bot description will appear on the bot's profile page
2. The welcome message will show when users first start the bot
3. Users will see what the bot can do immediately

**Note:** The bot's actual behavior is controlled by the code, not BotFather. BotFather only sets the profile information and welcome message.

---

## 🔄 If You Want to Change Later

You can always update these settings in BotFather:
- `/setdescription` - Change bot description
- `/setabouttext` - Change "About" text (shown in profile)
- `/setuserpic` - Change bot profile picture
- `/setdescriptionpic` - Change welcome picture

---

**Questions?** If you need help with any specific field, let me know!

