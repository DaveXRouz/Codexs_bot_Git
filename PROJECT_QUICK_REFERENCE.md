# 🚀 Codexs Telegram Bot - Quick Reference

**Quick overview of all features, commands, and capabilities**

---

## 📋 Core Features (9 Main Features)

1. **🌍 Bilingual Support** - English & Farsi with RTL support
2. **💼 Job Application System** - 12-question hiring funnel
3. **🎤 Voice Sample Collection** - Mandatory English voice test
4. **🤖 AI-Powered Fallback** - OpenAI GPT-4o-mini integration
5. **📝 Session Persistence** - Resume incomplete applications
6. **📊 Application History** - View all past submissions
7. **📞 Contact System** - Direct messaging to Codexs team
8. **ℹ️ Information System** - About Codexs & Updates
9. **🔐 Admin Panel** - Management & monitoring tools

---

## 🎯 Application Questions (12 Questions)

1. Full Name
2. Email (validated)
3. Contact/Phone (validated, supports contact button)
4. Location (validated, supports location button)
5. Role Category
6. Skills
7. Experience
8. Portfolio URL (validated, optional)
9. Motivation
10. Earliest Start Date
11. Preferred Working Hours
12. Salary Expectations

**Plus:** Mandatory English voice sample

---

## ⌨️ Commands (16 Total)

### **Public Commands (4)**
- `/start` - Start bot & select language
- `/menu` - Return to main menu
- `/help` - Get help information
- `/commands` - List all commands

### **Admin Commands (8)**
- `/admin` - Admin panel menu
- `/status` - Bot health & statistics
- `/stats` - Application statistics
- `/debug <user_id>` - Inspect user session
- `/sessions` - List active sessions
- `/cleanup` - Clean old session files
- `/testadmin` - Verify admin access
- `/testgroup` - Test group notifications

### **Group Commands (5)**
- `/daily` or `/report` - Today's application report
- `/gstats` - Detailed statistics
- `/recent` - List recent applications
- `/app <id>` - View application details
- `/ghelp` - Show group commands help

---

## 📁 Main Menu (5 Options)

1. **💼 Apply for jobs** - Start application flow
2. **🏢 About Codexs** - Company information
3. **📢 Updates & news** - Latest updates
4. **📞 Contact & support** - Send message to team
5. **📋 My applications** - View application history

**Plus:** Language switching option

---

## 🏗️ Technical Stack

- **Language:** Python 3.11+
- **Framework:** python-telegram-bot 21.5
- **AI:** OpenAI GPT-4o-mini
- **Storage:** JSONL files
- **Architecture:** Async/await

---

## 📊 Code Statistics

- **Total Lines:** ~5,100+ lines
- **Core Files:** 8 Python files
- **Functions:** 83 functions
- **Strings:** 100+ user-facing strings
- **Languages:** 2 (English, Farsi)

---

## 💾 Data Storage

- **Applications:** `data/applications.jsonl`
- **Contact Messages:** `data/contact_messages.jsonl`
- **Voice Samples:** `data/voice_samples/`
- **Sessions:** `data/sessions/session_<user_id>.json`

---

## ⚙️ Configuration (10 Variables)

**Required:**
- `BOT_TOKEN` - Telegram bot token

**Optional:**
- `DATA_DIR` - Data directory path
- `APPLICATION_WEBHOOK_URL` - Application webhook
- `APPLICATION_WEBHOOK_TOKEN` - Webhook auth token
- `CONTACT_WEBHOOK_URL` - Contact webhook
- `GROUP_CHAT_ID` - Telegram group ID
- `OPENAI_API_KEY` - OpenAI API key
- `OPENAI_MODEL` - OpenAI model (default: gpt-4o-mini)
- `ADMIN_USER_IDS` - Comma-separated admin IDs
- `ENABLE_MEDIA` - Enable media support

---

## 🔧 Core Modules (7 Files)

1. **`bot.py`** - Main bot logic (2,950 lines, 83 functions)
2. **`session.py`** - Session management (192 lines)
3. **`storage.py`** - Data persistence (293 lines)
4. **`localization.py`** - Localization (1,434 lines)
5. **`notifications.py`** - Webhook integration (28 lines)
6. **`ai.py`** - AI fallback (95 lines)
7. **`config.py`** - Configuration (120 lines)

---

## ✅ Key Features

- ✅ Full bilingual support (EN/FA)
- ✅ 12-question application flow
- ✅ Voice sample collection
- ✅ Session persistence & resume
- ✅ Application history
- ✅ Contact system
- ✅ AI-powered fallback
- ✅ Admin panel
- ✅ Group notifications
- ✅ Input validation
- ✅ Webhook integration
- ✅ Security features

---

## 🎯 What Makes It Unique

1. **Complete ATS System** - Full applicant tracking
2. **True Bilingual** - Real RTL support
3. **AI-Powered** - Intelligent responses
4. **User-Friendly** - Polished UX
5. **Developer-Friendly** - Admin tools
6. **Production-Ready** - Error handling
7. **Business-Ready** - Notifications & webhooks

---

**For detailed documentation, see:** `COMPLETE_PROJECT_DOCUMENTATION.md`

