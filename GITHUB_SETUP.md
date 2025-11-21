# GitHub Repository Setup Guide 🚀

## ✅ What's Been Done

1. ✅ Git repository initialized
2. ✅ `.gitignore` configured (excludes `.env`, `data/`, cache files)
3. ✅ Deployment configs created (`railway.json`, `render.yaml`)
4. ✅ README.md updated for GitHub
5. ✅ All source code ready to commit

## 📋 Next Steps

### Step 1: Add Repository to GitHub Desktop

**Option A: Use the repository you're creating**
1. In GitHub Desktop, click "Cancel" on the "Create New Repository" dialog
2. Go to **File → Add Local Repository**
3. Navigate to: `/Users/hamzeh/Desktop/Person/codexs_bot`
4. Click "Add Repository"

**Option B: Use your new repository location**
1. Complete creating the repository at `/Users/hamzeh/Desktop/Work/Codexs_bot_Git`
2. Copy all files from `/Users/hamzeh/Desktop/Person/codexs_bot` to the new location
3. Or use GitHub Desktop to clone/push to that location

### Step 2: Review Files to Commit

**Files that WILL be committed:**
- ✅ All source code (`src/`)
- ✅ Tests (`tests/`)
- ✅ Configuration files (`pyproject.toml`, `requirements.txt`)
- ✅ Deployment configs (`Procfile`, `railway.json`, `render.yaml`)
- ✅ Documentation (`README.md`, `QUICK_START.md`, etc.)
- ✅ Scripts (`scripts/`)

**Files that WON'T be committed (protected by `.gitignore`):**
- ❌ `.env` (contains your bot token - **NEVER commit this!**)
- ❌ `data/` (application data and voice files)
- ❌ `.venv/` (virtual environment)
- ❌ Cache files (`__pycache__/`, `.pytest_cache/`, etc.)
- ❌ Logs (`logs/`)

### Step 3: Make Your First Commit

In GitHub Desktop:
1. You'll see all the files ready to commit
2. Write a commit message: `"Initial commit: Codexs Telegram Bot"`
3. Click **"Commit to main"**

### Step 4: Push to GitHub

1. Click **"Publish repository"** (if it's local only)
2. Or click **"Push origin"** (if already connected)
3. Choose **"Keep this code private"** (recommended for bot tokens)
4. Click **"Publish Repository"**

### Step 5: Deploy to Cloud (24/7 Operation)

Once pushed to GitHub, deploy to a cloud service:

#### 🚂 Railway (Easiest - Recommended)

1. Go to [railway.app](https://railway.app)
2. Sign up/login with GitHub
3. Click **"New Project"** → **"Deploy from GitHub repo"**
4. Select your `codexs_bot` repository
5. Railway will auto-detect `railway.json`
6. Add environment variables:
   - `BOT_TOKEN` = Your Telegram bot token
   - `DATA_DIR` = `data`
   - `ENABLE_MEDIA` = `true`
   - (Optional) Add webhook URLs and tokens
7. Click **"Deploy"**
8. Bot will run 24/7! 🎉

#### 🎨 Render

1. Go to [render.com](https://render.com)
2. Sign up/login with GitHub
3. Click **"New +"** → **"Background Worker"**
4. Connect your GitHub repository
5. Render will auto-detect `render.yaml`
6. Add environment variables (same as Railway)
7. Click **"Create Background Worker"**
8. Bot will run 24/7! 🎉

### Step 6: Verify Deployment

1. Check the deployment logs in Railway/Render
2. Test the bot in Telegram
3. Send `/start` to your bot
4. Verify it responds correctly

## 🔒 Security Checklist

Before pushing to GitHub, verify:

- [ ] `.env` is in `.gitignore` ✅
- [ ] No bot tokens in code files ✅
- [ ] No sensitive data in commit history ✅
- [ ] Repository is set to **Private** (recommended)

## 📝 Environment Variables for Cloud

When deploying, add these in Railway/Render dashboard:

```
BOT_TOKEN=your_telegram_bot_token
DATA_DIR=data
ENABLE_MEDIA=true
APPLICATION_WEBHOOK_URL=https://your-api.com/candidates (optional)
APPLICATION_WEBHOOK_TOKEN=your_token (optional)
CONTACT_WEBHOOK_URL=https://your-api.com/contact (optional)
GROUP_CHAT_ID=-1001234567890 (optional)
```

## 🆘 Troubleshooting

**"Repository not found"**
- Make sure you've pushed to GitHub first
- Check repository visibility (private/public)

**"Build failed"**
- Check Python version (should be 3.11+)
- Verify `requirements.txt` is correct
- Check deployment logs

**"Bot not responding"**
- Verify `BOT_TOKEN` is set correctly
- Check deployment logs for errors
- Ensure the worker is running (not sleeping)

## ✅ Success!

Once deployed, your bot will:
- ✅ Run 24/7 even when your computer is off
- ✅ Auto-restart on failures
- ✅ Scale automatically
- ✅ Have persistent data storage

---

**Need help?** Check `CLOUD_DEPLOYMENT.md` for detailed instructions.

