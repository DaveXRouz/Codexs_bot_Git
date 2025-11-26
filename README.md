# Codexs Telegram Bot 🤖

A professional, bilingual (English/Farsi) Telegram bot for Codexs that handles job applications, company information, and contact requests with a premium user experience.

## ✨ Features

- **Bilingual Support**: Full English and Farsi localization with persistent language memory
- **Job Application Flow**: 12-step structured hiring funnel with validation and voice sample capture
- **Company Information**: Rich About and Updates flows with media support
- **Contact Management**: Direct contact form with webhook notifications
- **Data Persistence**: JSONL storage for applications and contact messages
- **Security**: Input validation, HTML sanitization, rate limiting
- **Automated Testing**: Comprehensive test suite with 20+ tests

## 🚀 Quick Start

### Local Development

1. **Clone the repository**
   ```bash
   git clone <your-repo-url>
   cd codexs_bot
   ```

2. **Set up virtual environment**
   ```bash
   python3 -m venv .venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   pip install -e .
   ```

3. **Configure environment**
   ```bash
   cp env.example .env
   # Edit .env and add your BOT_TOKEN
   ```

4. **Run the bot**
   ```bash
   ./scripts/run_bot.sh
   # Or: codexs-bot
   ```

### Cloud Deployment (24/7 Operation)

The bot is ready for deployment on:
- **Railway** (Recommended) - See `CLOUD_DEPLOYMENT.md`
- **Render** - See `CLOUD_DEPLOYMENT.md`
- **DigitalOcean App Platform**
- **Heroku**
- **AWS EC2**

**Quick Railway Deploy:**
1. Push this repo to GitHub
2. Connect to Railway
3. Add environment variables (see `.env.example`)
4. Deploy!

## 📋 Requirements

- Python 3.11+
- Telegram Bot Token (get from [@BotFather](https://t.me/BotFather))
- (Optional) Webhook URLs for notifications
- (Optional) Telegram Group Chat ID for summaries

## ⚙️ Configuration

Create a `.env` file with:

```env
BOT_TOKEN=your_telegram_bot_token_here
DATA_DIR=data
APPLICATION_WEBHOOK_URL=https://your-api.com/candidates
APPLICATION_WEBHOOK_TOKEN=your_bearer_token
CONTACT_WEBHOOK_URL=https://your-api.com/contact
GROUP_CHAT_ID=-1001234567890
ENABLE_MEDIA=true
OPENAI_API_KEY=sk-...
OPENAI_MODEL=gpt-4o-mini
BOT_CONFIG_URL=https://<supabase-project>.functions.supabase.co/bot-config
BOT_STATUS_URL=https://<supabase-project>.functions.supabase.co/bot-status
BOT_LOG_URL=https://<supabase-project>.functions.supabase.co/bot-log
BOT_API_KEY=shared_secret_from_supabase
```

`OPENAI_API_KEY` is optional—add it to enable the conversational fallback powered by OpenAI (defaults to disabled). Leave `OPENAI_MODEL` empty to use the default `gpt-4o-mini` or point it to any compatible chat-completions model.

## 📁 Project Structure

```
codexs_bot/
├── src/codexs_bot/     # Main bot code
│   ├── bot.py          # Core bot logic
│   ├── localization.py # English/Farsi strings
│   ├── config.py       # Configuration
│   ├── session.py       # User session management
│   ├── storage.py      # Data persistence
│   └── notifications.py # Webhook notifications
├── tests/              # Automated tests
├── scripts/            # Deployment scripts
├── media/              # Bot images/assets
├── data/               # Application data (gitignored)
└── docs/               # Documentation
```

## 🧪 Testing

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=src/codexs_bot --cov-report=html
```

## 📚 Documentation

- `COMPLETE_PROJECT_DOCUMENTATION.md` - Complete project reference (all features, commands, functions)
- `PROJECT_QUICK_REFERENCE.md` - Quick reference guide
- `CLOUD_DEPLOYMENT.md` - Cloud deployment guide (Railway, Render, etc.)
- `BOTFATHER_CONFIG.md` - BotFather configuration guide

## 🔒 Security

- ✅ Input length validation (1000 char limit)
- ✅ HTML sanitization (XSS protection)
- ✅ Rate limiting (20 requests/minute)
- ✅ Email validation
- ✅ Secure environment variable handling

## 📝 License

Private - Codexs

## 🤝 Support

For issues or questions, contact the development team.

---

**Status**: ✅ Production Ready | ✅ All Tests Passing | ✅ Security Hardened

📋 **See [COMPLETE_PROJECT_DOCUMENTATION.md](COMPLETE_PROJECT_DOCUMENTATION.md) for complete project documentation.**
