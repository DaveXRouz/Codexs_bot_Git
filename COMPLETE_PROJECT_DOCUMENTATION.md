# 📚 Codexs Telegram Bot - Complete Project Documentation

**Last Updated:** 2025-01-27  
**Version:** Production Ready  
**Status:** ✅ Fully Operational

---

## 📋 Table of Contents

1. [Project Overview](#project-overview)
2. [Core Features](#core-features)
3. [User Flows](#user-flows)
4. [Commands & Functions](#commands--functions)
5. [Technical Architecture](#technical-architecture)
6. [Data Storage](#data-storage)
7. [Configuration](#configuration)
8. [Admin Features](#admin-features)
9. [Group Features](#group-features)
10. [Security & Validation](#security--validation)
11. [Integration Points](#integration-points)
12. [File Structure](#file-structure)

---

## 🎯 Project Overview

**Codexs Telegram Bot** is a production-ready, enterprise-grade bilingual (English/Farsi) Telegram bot designed for:
- **Job Application Collection** - Structured 12-question hiring funnel
- **Company Information** - About Codexs and updates
- **Contact Management** - Direct messaging to Codexs team
- **Candidate Management** - Application history and tracking

**Technology Stack:**
- Python 3.11+
- python-telegram-bot 21.5
- OpenAI API (GPT-4o-mini) for AI fallback
- JSONL for data persistence
- Async/await architecture

---

## ✨ Core Features

### 1. 🌍 Bilingual Support (English & Farsi)

**Capabilities:**
- ✅ Full RTL (Right-to-Left) support for Farsi/Persian
- ✅ Persistent language memory per user
- ✅ Instant language switching from main menu
- ✅ Localized keyboards and button labels
- ✅ Smart text rendering (emojis work in both directions)
- ✅ All 100+ user-facing strings translated

**Implementation:**
- Language selection on first `/start`
- Language stored in user session
- All messages use `localization.py` dictionary
- RTL text properly formatted with emoji handling

---

### 2. 💼 Job Application System

#### **12-Step Hiring Funnel:**

1. **Full Name** (`full_name`)
   - Legal name as on official documents
   - Required field

2. **Email** (`email`)
   - Primary email for official communication
   - Validation: Must be valid email format
   - Required field

3. **Contact/Phone** (`contact`)
   - Phone number or Telegram contact
   - Validation: Phone format or Telegram contact button
   - Supports Telegram contact sharing button
   - Required field

4. **Location** (`location`)
   - City/Country or coordinates
   - Validation: Location format or Telegram location button
   - Supports Telegram location sharing button
   - Required field

5. **Role Category** (`role_category`)
   - Type of role interested in
   - Required field

6. **Skills** (`skills`)
   - Technical skills and expertise
   - Required field

7. **Experience** (`experience`)
   - Years of experience
   - Required field

8. **Portfolio URL** (`portfolio_url`)
   - Link to portfolio/work samples
   - Validation: Must be valid URL format
   - Optional field (can skip)

9. **Motivation** (`motivation`)
   - Why interested in Codexs
   - Required field

10. **Earliest Start Date** (`earliest_start`)
    - When can start working
    - Required field

11. **Preferred Working Hours** (`working_hours`)
    - Full-time/Part-time preference
    - Required field

12. **Salary Expectations** (`salary_expectations`)
    - Expected compensation range
    - Required field

#### **Application Flow Features:**

- ✅ **Progress Tracking** - Shows "Question X/12"
- ✅ **Input Validation** - Email, phone, URL, location formats
- ✅ **Smart Skip Logic** - Optional questions can be skipped
- ✅ **Edit Before Submit** - Review and edit any answer
- ✅ **Mandatory Voice Sample** - English voice recording required
- ✅ **Confirmation Summary** - Beautiful formatted review
- ✅ **Session Persistence** - Resume incomplete applications
- ✅ **Application History** - View all past submissions
- ✅ **Exit Confirmation** - Prevents accidental data loss
- ✅ **Back Navigation** - Return to previous question
- ✅ **Repeat Question** - Re-ask current question

---

### 3. 🎤 Voice Sample Collection

**Features:**
- ✅ **Mandatory English Voice Test** - Required for all candidates
- ✅ **Clear Instructions** - What to say in voice message
- ✅ **File Storage** - Voice files saved to `data/voice_samples/`
- ✅ **Metadata Tracking** - File IDs, message IDs, timestamps
- ✅ **Group Forwarding** - Voice samples sent to hiring team
- ✅ **Re-recording Option** - Can re-record during edit mode
- ✅ **Skip Tracking** - Records if voice was skipped (though mandatory)
- ✅ **File Size Validation** - Checks file size limits
- ✅ **Format Support** - Handles .ogg and .mp3 formats

**Voice Prompt Text:**
- Instructions in user's selected language
- Explains why voice is required
- Provides sample text to read
- Clear expectations

---

### 4. 🤖 AI-Powered Fallback System

**OpenAI Integration:**
- ✅ **GPT-4o-mini Model** - Fast, cost-effective responses
- ✅ **Context-Aware** - Understands user's current flow state
- ✅ **Rate Limiting** - 5 requests per 5 minutes per user
- ✅ **Graceful Degradation** - Falls back if AI fails
- ✅ **Intent Recognition** - Understands user questions
- ✅ **Bilingual Support** - Responds in user's language
- ✅ **System Prompts** - Custom prompts for Codexs brand

**When AI Responds:**
- User asks question outside current flow
- User needs clarification
- User asks "what does this mean?"
- General inquiries about Codexs

**Rate Limiting:**
- Window: 5 minutes
- Max requests: 5 per window
- Exceeded: Shows rate limit message
- Resets automatically after window

---

### 5. 📝 Session Persistence & Resume

**Features:**
- ✅ **Auto-save** - Sessions saved after every answer
- ✅ **Resume Prompts** - Offers to resume incomplete applications
- ✅ **State Restoration** - Restores all answers, flow state, voice status
- ✅ **Progress Tracking** - Shows how many questions completed
- ✅ **Smart Detection** - Knows when application is incomplete
- ✅ **Session Files** - Stored in `data/sessions/session_<user_id>.json`
- ✅ **Cleanup** - Admin can clean old sessions (30+ days)

**Resume Flow:**
1. User starts bot with `/start`
2. Bot detects incomplete application
3. Shows resume prompt with progress count
4. User chooses "Yes" to resume or "No" to start fresh
5. If resume: Restores all answers and continues from last question

---

### 6. 📊 Application History

**Features:**
- ✅ **View All Past Applications** - Complete history per user
- ✅ **Application IDs** - Unique tracking for each submission
- ✅ **Submission Dates** - When each application was submitted
- ✅ **Voice Status** - Shows if voice was received or skipped
- ✅ **Quick Access** - From main menu
- ✅ **Empty State** - Helpful message if no applications

**History Display:**
- Lists all applications in reverse chronological order
- Shows application ID, date, voice status
- Clickable to view details (future feature)

---

### 7. 📞 Contact & Support System

**Features:**
- ✅ **Direct Messaging** - Users can send messages to Codexs team
- ✅ **Contact Sharing** - Supports Telegram contact button
- ✅ **Location Sharing** - Supports Telegram location button
- ✅ **Webhook Notifications** - Sends contact messages to external API
- ✅ **Group Notifications** - Alerts team in Telegram group
- ✅ **Confirmation** - Users get acknowledgment
- ✅ **Explicit Decision** - Requires Yes/No before sending

**Contact Flow:**
1. User selects "Contact" from menu
2. Bot explains what contact is for
3. User must explicitly choose "Yes" or "No"
4. If Yes: User types message
5. Message saved and notifications sent
6. User gets thank you message

---

### 8. ℹ️ Information System

#### **About Codexs:**
- ✅ **Rich Text Sections** - Multiple sections with formatting
- ✅ **Media Support** - Images/videos (if configured)
- ✅ **Call-to-Action Buttons** - Links to external resources
- ✅ **Professional Formatting** - HTML formatting with emojis
- ✅ **Bilingual Content** - All content in both languages

#### **Updates:**
- ✅ **Latest Company News** - Update cards with information
- ✅ **Update Cards** - Formatted cards with links
- ✅ **Organized Presentation** - Clean, readable format
- ✅ **External Links** - Links to blog posts, announcements

---

### 9. 🎨 User Experience Features

**Navigation:**
- ✅ **Smart Navigation** - Back buttons, menu shortcuts
- ✅ **Exit Confirmation** - Prevents accidental data loss
- ✅ **Help System** - Context-aware help messages
- ✅ **Command Shortcuts** - `/start`, `/menu`, `/help`, `/commands`
- ✅ **Visual Design** - Professional formatting with emojis
- ✅ **Error Messages** - User-friendly, actionable
- ✅ **Progress Indicators** - Users know where they are

**Intent Recognition:**
- Recognizes "menu", "back", "repeat" commands
- Works in both English and Farsi
- Case-insensitive matching
- Handles variations

---

## 🔧 Commands & Functions

### **Public Commands (Available to Everyone)**

| Command | Description | Handler Function |
|---------|-------------|------------------|
| `/start` | Start the bot and select language | `start()` |
| `/menu` | Return to main menu | `menu_command()` |
| `/help` | Get help and see what bot can do | `handle_help()` |
| `/commands` | List all available commands | `handle_commands()` |

### **Admin Commands (Admin Only)**

| Command | Description | Handler Function | Requirements |
|---------|-------------|------------------|--------------|
| `/admin` | Admin panel menu | `handle_admin()` | Admin user ID |
| `/status` | Bot health and status | `handle_admin_status()` | Admin user ID |
| `/stats` | Application statistics | `handle_admin_stats()` | Admin user ID |
| `/debug <user_id>` | Debug user session | `handle_admin_debug()` | Admin user ID |
| `/sessions` | List active sessions | `handle_admin_sessions()` | Admin user ID |
| `/cleanup` | Clean up old session files | `handle_admin_cleanup()` | Admin user ID |
| `/testadmin` | Verify admin access | `handle_test_admin()` | Admin user ID |
| `/testgroup` | Test group notifications | `handle_admin_test_group()` | Admin user ID |

### **Group Commands (Group Admin Only)**

| Command | Description | Handler Function | Requirements |
|---------|-------------|------------------|--------------|
| `/daily` or `/report` | Today's application report | `handle_group_daily_report()` | Group admin or Admin user ID |
| `/gstats` | Detailed statistics | `handle_group_stats()` | Group admin or Admin user ID |
| `/recent` | List recent applications | `handle_group_recent()` | Group admin or Admin user ID |
| `/app <id>` | View application details by ID | `handle_group_app_details()` | Group admin or Admin user ID |
| `/ghelp` | Show group commands help | `handle_group_help()` | Group admin or Admin user ID |

### **Message Handlers**

| Handler | Description | Trigger |
|---------|-------------|---------|
| `handle_text()` | Process text messages | All text messages (not commands) |
| `handle_voice()` | Process voice messages | Voice or audio messages |
| `handle_contact_shared()` | Process shared contacts | Telegram contact button |
| `handle_location_shared()` | Process shared locations | Telegram location button |

---

## 🏗️ Technical Architecture

### **Core Modules**

#### **1. `bot.py` (Main Bot Logic)**
- **Size:** ~2,950 lines
- **Functions:** 83 functions
- **Responsibilities:**
  - Command handlers
  - Message handlers
  - Flow management
  - State management
  - UI rendering
  - Validation
  - Navigation

**Key Functions:**
- `start()` - Initialize bot and language selection
- `handle_text()` - Main text message processor
- `handle_application_answer()` - Process application answers
- `handle_voice()` - Process voice messages
- `finalize_application()` - Submit application
- `_maybe_ai_reply()` - AI fallback logic
- `_open_menu_section()` - Menu navigation
- `handle_main_menu_choice()` - Process menu selections

#### **2. `session.py` (Session Management)**
- **Size:** ~192 lines
- **Classes:** `UserSession`, `Flow` enum
- **Responsibilities:**
  - User session state
  - Flow tracking
  - Session persistence
  - State serialization

**Key Features:**
- `UserSession` dataclass with 20+ fields
- Flow states: IDLE, APPLY, CONTACT_MESSAGE, CONFIRM
- Session serialization/deserialization
- Incomplete application detection

#### **3. `storage.py` (Data Persistence)**
- **Size:** ~293 lines
- **Classes:** `DataStorage`
- **Responsibilities:**
  - Application storage
  - Contact message storage
  - Session file management
  - Data retrieval

**Key Methods:**
- `save_application()` - Save application to JSONL
- `save_contact_message()` - Save contact message
- `save_session()` - Save user session
- `load_session()` - Load user session
- `get_all_applications()` - Get all applications
- `get_user_applications()` - Get user's applications
- `cleanup_old_sessions()` - Clean old session files

#### **4. `localization.py` (Localization)**
- **Size:** ~1,434 lines
- **Content:** 100+ user-facing strings
- **Languages:** English, Farsi
- **Responsibilities:**
  - All user-facing text
  - Menu labels
  - Question prompts
  - Error messages
  - Help text

**Key Sections:**
- `HIRING_QUESTIONS` - 12 application questions
- `MENU_LABELS` - Main menu buttons
- `ERROR_*` - Error messages
- `HELP_TEXT` - Help content
- `ABOUT_*` - About Codexs content
- `UPDATES` - Updates content

#### **5. `notifications.py` (Webhook Integration)**
- **Size:** ~28 lines
- **Classes:** `WebhookNotifier`
- **Responsibilities:**
  - Send webhook notifications
  - HTTP POST requests
  - Error handling

**Key Methods:**
- `post()` - Send payload to webhook URL

#### **6. `ai.py` (AI Fallback)**
- **Size:** ~95 lines
- **Classes:** `OpenAIFallback`
- **Responsibilities:**
  - OpenAI API integration
  - AI response generation
  - Rate limiting
  - Context building

**Key Methods:**
- `generate_reply()` - Generate AI response
- `enabled` - Check if AI is configured

#### **7. `config.py` (Configuration)**
- **Size:** ~120 lines
- **Classes:** `Settings` dataclass
- **Responsibilities:**
  - Environment variable loading
  - Settings management
  - Path configuration

**Key Settings:**
- Bot token
- Data directories
- Webhook URLs
- OpenAI API key
- Admin user IDs
- Group chat ID

---

## 💾 Data Storage

### **Storage Files**

#### **1. Applications** (`data/applications.jsonl`)
- **Format:** JSONL (one JSON object per line)
- **Content:** All submitted job applications
- **Fields:**
  - `application_id` - Unique ID
  - `submitted_at` - ISO timestamp
  - `language` - "en" or "fa"
  - `applicant` - User information
  - `answers` - All 12 question answers
  - `voice_file_path` - Path to voice file
  - `voice_file_id` - Telegram file ID
  - `voice_skipped` - Boolean

#### **2. Contact Messages** (`data/contact_messages.jsonl`)
- **Format:** JSONL
- **Content:** All contact messages from users
- **Fields:**
  - `submitted_at` - ISO timestamp
  - `language` - "en" or "fa"
  - `sender` - User information
  - `message` - Message text

#### **3. Voice Samples** (`data/voice_samples/`)
- **Format:** `.ogg` or `.mp3` files
- **Naming:** `<user_id>_<timestamp>.ogg`
- **Content:** Voice recordings from candidates

#### **4. User Sessions** (`data/sessions/session_<user_id>.json`)
- **Format:** JSON
- **Content:** User session state
- **Fields:**
  - `language` - User's language preference
  - `flow` - Current flow state
  - `question_index` - Current question number
  - `answers` - All answers so far
  - `waiting_voice` - Boolean
  - `voice_file_path` - Path to voice file
  - `voice_file_id` - Telegram file ID
  - `edit_mode` - Boolean
  - `contact_pending` - Boolean
  - And more...

---

## ⚙️ Configuration

### **Environment Variables**

| Variable | Required | Description | Example |
|----------|----------|-------------|---------|
| `BOT_TOKEN` | ✅ Yes | Telegram bot token | `1234567890:ABC...` |
| `DATA_DIR` | ❌ No | Data directory path | `/app/data` |
| `APPLICATION_WEBHOOK_URL` | ❌ No | Webhook for applications | `https://api.example.com/applications` |
| `APPLICATION_WEBHOOK_TOKEN` | ❌ No | Bearer token for webhook | `secret_token` |
| `CONTACT_WEBHOOK_URL` | ❌ No | Webhook for contact messages | `https://api.example.com/contact` |
| `GROUP_CHAT_ID` | ❌ No | Telegram group ID for notifications | `-1001234567890` |
| `OPENAI_API_KEY` | ❌ No | OpenAI API key for AI fallback | `sk-...` |
| `OPENAI_MODEL` | ❌ No | OpenAI model name | `gpt-4o-mini` |
| `ADMIN_USER_IDS` | ❌ No | Comma-separated admin user IDs | `123456789,987654321` |
| `ENABLE_MEDIA` | ❌ No | Enable media support | `true` or `false` |

### **Default Paths**
- Data directory: `./data` (relative to project root)
- Applications file: `data/applications.jsonl`
- Contact file: `data/contact_messages.jsonl`
- Voice samples: `data/voice_samples/`
- Sessions: `data/sessions/`
- Media: `./media/`

---

## 🔐 Admin Features

### **Admin Panel** (`/admin`)

**Menu Options:**
1. **Status** - Bot health and statistics
2. **Stats** - Application statistics
3. **Debug** - Inspect user session
4. **Sessions** - List active sessions
5. **Cleanup** - Clean old session files
6. **Test Group** - Test group notifications

### **Status Command** (`/status`)

**Shows:**
- Bot uptime
- Total applications
- Active sessions
- Today's applications
- Voice samples collected
- Language breakdown
- Storage file sizes

### **Stats Command** (`/stats`)

**Shows:**
- Total applications
- Applications by date range
- Applications by language
- Voice completion rate
- Application completion rate
- Recent activity

### **Debug Command** (`/debug <user_id>`)

**Shows:**
- User information
- Current session state
- Flow state
- Question index
- Answers so far
- Voice status
- All session fields

### **Sessions Command** (`/sessions`)

**Shows:**
- List of all active sessions
- User IDs
- Flow states
- Last activity
- Session file sizes

### **Cleanup Command** (`/cleanup`)

**Action:**
- Deletes session files older than 30 days
- Shows count of deleted files
- Safe operation (only old sessions)

---

## 👥 Group Features

### **Daily Report** (`/daily` or `/report`)

**Shows:**
- Today's application count
- Applications with voice
- Applications without voice
- Language breakdown
- Recent applications list (last 5)
- Formatted for group chat

### **Group Stats** (`/gstats`)

**Shows:**
- Total applications
- Applications this week
- Applications this month
- Voice completion rate
- Language breakdown
- Detailed statistics

### **Recent Applications** (`/recent`)

**Shows:**
- List of recent applications (last 10)
- Application IDs
- Names
- Dates
- Voice status
- Language

### **Application Details** (`/app <id>`)

**Shows:**
- Full application details
- All answers
- Applicant information
- Voice status
- Submission date
- Formatted for group chat

### **Group Help** (`/ghelp`)

**Shows:**
- List of all group commands
- Usage instructions
- Examples

---

## 🛡️ Security & Validation

### **Input Validation**

#### **Email Validation**
- Regex pattern matching
- Must contain @ symbol
- Must have valid domain
- Error message in user's language

#### **Phone Validation**
- Regex pattern matching
- Supports international formats
- Accepts Telegram contact button
- Error message in user's language

#### **URL Validation**
- Regex pattern matching
- Must start with http:// or https://
- Must have valid domain
- Error message in user's language

#### **Location Validation**
- Checks for valid location format
- Accepts Telegram location button
- Error message in user's language

#### **Text Length Validation**
- Max length: 1000 characters (configurable)
- Truncation for display
- Error message if too long

### **Security Features**

#### **HTML Sanitization**
- All user input sanitized
- HTML entities escaped
- XSS prevention
- Safe message rendering

#### **Rate Limiting**
- AI requests: 5 per 5 minutes
- Prevents API abuse
- Graceful error messages

#### **Access Control**
- Admin commands require admin user ID
- Group commands require group admin or admin user ID
- Access denied messages for unauthorized users

#### **Error Handling**
- Comprehensive try/catch blocks
- Graceful degradation
- User-friendly error messages
- Logging for debugging

---

## 🔌 Integration Points

### **1. Telegram Bot API**
- **Purpose:** Core messaging
- **Methods Used:**
  - `send_message()`
  - `send_photo()`
  - `send_voice()`
  - `forward_message()`
  - `reply_text()`

### **2. OpenAI API**
- **Purpose:** AI fallback responses
- **Endpoint:** `https://api.openai.com/v1/chat/completions`
- **Model:** GPT-4o-mini (configurable)
- **Rate Limit:** 5 requests per 5 minutes per user

### **3. Application Webhook**
- **Purpose:** Send applications to external system
- **Method:** HTTP POST
- **Format:** JSON payload
- **Headers:** Content-Type, Authorization (optional)
- **Payload:** Full application data

### **4. Contact Webhook**
- **Purpose:** Send contact messages to external system
- **Method:** HTTP POST
- **Format:** JSON payload
- **Headers:** Content-Type, Authorization (optional)
- **Payload:** Contact message data

### **5. Telegram Group**
- **Purpose:** Team notifications
- **Features:**
  - Application notifications
  - Contact message notifications
  - Voice sample forwarding
  - Daily reports
  - Statistics

---

## 📁 File Structure

```
Codexs_bot_Git/
├── src/
│   └── codexs_bot/
│       ├── __init__.py
│       ├── __main__.py
│       ├── bot.py              # Main bot logic (2,950 lines)
│       ├── session.py          # Session management (192 lines)
│       ├── storage.py          # Data persistence (293 lines)
│       ├── localization.py    # Localization (1,434 lines)
│       ├── notifications.py   # Webhook integration (28 lines)
│       ├── ai.py              # AI fallback (95 lines)
│       └── config.py          # Configuration (120 lines)
├── data/
│   ├── applications.jsonl      # All applications
│   ├── contact_messages.jsonl  # Contact messages
│   ├── voice_samples/          # Voice files
│   └── sessions/               # Session files
├── media/                      # Media files (if enabled)
├── tests/                      # Test files
├── docs/                       # Documentation
├── scripts/                    # Utility scripts
├── .env                        # Environment variables
├── requirements.txt            # Python dependencies
├── pyproject.toml              # Package configuration
└── README.md                   # Main documentation
```

---

## 📊 Statistics

### **Code Metrics**
- **Total Lines of Code:** ~5,100+ lines
- **Python Files:** 8 core files
- **Functions:** 83 functions
- **User-Facing Strings:** 100+ strings
- **Languages Supported:** 2 (English, Farsi)
- **Commands:** 16 commands
- **Handlers:** 4 message handlers

### **Feature Count**
- **Application Questions:** 12 questions
- **Menu Options:** 5 main menu items
- **Admin Commands:** 8 commands
- **Group Commands:** 5 commands
- **Validation Rules:** 5 validation types
- **Storage Files:** 4 file types

---

## ✅ What's Working

### **Fully Operational:**
- ✅ Bilingual support (EN/FA)
- ✅ 12-question application flow
- ✅ Voice sample collection
- ✅ Session persistence & resume
- ✅ Application history
- ✅ Contact system
- ✅ About & Updates flows
- ✅ AI fallback system
- ✅ Admin commands
- ✅ Group commands
- ✅ Input validation
- ✅ Webhook integration
- ✅ Group notifications
- ✅ Error handling
- ✅ Security features

### **Tested & Verified:**
- ✅ Language switching
- ✅ Application flow (all 12 questions)
- ✅ Voice collection
- ✅ Edit functionality
- ✅ Session resume
- ✅ Contact sharing
- ✅ Location sharing
- ✅ Admin access control
- ✅ Group notifications
- ✅ Error messages
- ✅ Input validation

---

## 🎯 What Makes This Bot Unique

1. **Complete ATS System** - Not just a form, a full applicant tracking system
2. **True Bilingual** - Real RTL support, not just translations
3. **AI-Powered** - Intelligent responses, not just scripts
4. **User-Friendly** - Polished UX, not clunky forms
5. **Developer-Friendly** - Admin tools, logging, debugging
6. **Production-Ready** - Error handling, persistence, security
7. **Business-Ready** - Notifications, webhooks, analytics-ready

---

## 📝 Summary

**Codexs Telegram Bot** is a **production-ready, enterprise-grade solution** that combines:
- ✅ Professional UX design
- ✅ Advanced technical architecture
- ✅ Complete feature set
- ✅ Production-ready reliability
- ✅ Business value delivery

**It's not just a bot—it's a complete candidate management and communication platform.**

---

**Document Version:** 1.0  
**Last Updated:** 2025-01-27  
**Maintained By:** Codexs Development Team

