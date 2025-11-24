# Codexs Bot - 24/7 Cloud Deployment Guide

## 🌐 Why Cloud Hosting?

Your local PC can't run 24/7 if it's turned off. To keep the bot running **always**, you need to deploy it to a **cloud server** that runs continuously.

---

## 🚀 Recommended Cloud Hosting Options

### Option 1: Railway (Easiest) ⭐ **RECOMMENDED**

**Why:** Free tier, super easy setup, automatic deployments

**Steps:**

1. **Sign up:** https://railway.app (free tier available)

2. **Create new project:**
   - Click "New Project"
   - Select "Deploy from GitHub repo" (or upload your code)

3. **Configure environment:**
   - Go to "Variables" tab
   - Add these environment variables:
     ```
     BOT_TOKEN=your_bot_token_here
     DATA_DIR=/app/data
     ENABLE_MEDIA=true
     GROUP_CHAT_ID=-5094334512
     OPENAI_API_KEY=sk-... (optional)
     ADMIN_USER_IDS=123456789,987654321 (optional)
     ```

4. **Deploy:**
   - Railway auto-detects Python and installs dependencies from `requirements.txt`
   - Bot starts automatically using `railway.json` or `Procfile`
   - Bot runs 24/7

5. **Monitor:**
   - Check "Deployments" tab for build progress
   - View real-time logs
   - Check "Metrics" for CPU/memory usage

**Cost:** Free tier: $5/month credit (usually enough for a bot)

**Troubleshooting:**
- If bot not responding, check logs in "Deployments" tab
- Verify `BOT_TOKEN` is correct in "Variables" tab
- Check Python version (should be 3.11+)
- Restart service from "Settings" if needed

---

### Option 2: Render (Free Tier Available)

**Why:** Free tier, simple setup, good for Python

**Steps:**

1. **Sign up:** https://render.com

2. **Create new Web Service:**
   - Connect your GitHub repo
   - Or upload code manually

3. **Settings:**
   - **Build Command:** `pip install -r requirements.txt`
   - **Start Command:** `python -m codexs_bot.bot`
   - **Environment:** Python 3

4. **Environment Variables:**
   ```
   BOT_TOKEN=your_bot_token_here
   DATA_DIR=/opt/render/project/src/data
   ENABLE_MEDIA=true
   GROUP_CHAT_ID=-5094334512
   ```

5. **Deploy:**
   - Render builds and deploys automatically
   - Bot runs 24/7 on free tier

**Cost:** Free tier available (with limitations), $7/month for always-on

---

### Option 3: DigitalOcean App Platform

**Why:** Reliable, good performance, easy scaling

**Steps:**

1. **Sign up:** https://www.digitalocean.com

2. **Create App:**
   - Connect GitHub or upload code
   - Select Python runtime

3. **Configure:**
   - Add environment variables
   - Set start command: `python -m codexs_bot.bot`

4. **Deploy:**
   - Auto-deploys on git push
   - Runs 24/7

**Cost:** $5/month (basic plan)

---

### Option 4: Heroku (Classic, but still works)

**Why:** Well-established, lots of documentation

**Steps:**

1. **Install Heroku CLI:**
   ```bash
   brew install heroku/brew/heroku
   ```

2. **Login:**
   ```bash
   heroku login
   ```

3. **Create app:**
   ```bash
   cd /Users/hamzeh/Desktop/Person/codexs_bot
   heroku create codexs-bot
   ```

4. **Set environment variables:**
   ```bash
   heroku config:set BOT_TOKEN=your_token_here
   heroku config:set ENABLE_MEDIA=true
   heroku config:set GROUP_CHAT_ID=-5094334512
   ```

5. **Create Procfile:**
   ```
   worker: python -m codexs_bot.bot
   ```

6. **Deploy:**
   ```bash
   git push heroku main
   ```

**Cost:** Free tier discontinued, paid plans start at $5/month

---

### Option 5: AWS EC2 / Lightsail (Most Control)

**Why:** Full control, scalable, professional

**Steps:**

1. **Create EC2 instance:**
   - Choose Ubuntu server
   - t2.micro (free tier eligible)

2. **SSH into server:**
   ```bash
   ssh ubuntu@your-server-ip
   ```

3. **Install dependencies:**
   ```bash
   sudo apt update
   sudo apt install python3 python3-pip python3-venv git
   ```

4. **Clone and setup:**
   ```bash
   git clone your-repo-url
   cd codexs_bot
   python3 -m venv .venv
   source .venv/bin/activate
   pip install -r requirements.txt
   ```

5. **Create systemd service:**
   ```bash
   sudo nano /etc/systemd/system/codexs-bot.service
   ```
   
   Add:
   ```ini
   [Unit]
   Description=Codexs Telegram Bot
   After=network.target

   [Service]
   Type=simple
   User=ubuntu
   WorkingDirectory=/home/ubuntu/codexs_bot
   Environment="PATH=/home/ubuntu/codexs_bot/.venv/bin"
   ExecStart=/home/ubuntu/codexs_bot/.venv/bin/python -m codexs_bot.bot
   Restart=always

   [Install]
   WantedBy=multi-user.target
   ```

6. **Start service:**
   ```bash
   sudo systemctl enable codexs-bot
   sudo systemctl start codexs-bot
   ```

**Cost:** Free tier (t2.micro) for 12 months, then ~$10/month

---

## 📋 Pre-Deployment Checklist

Before deploying to cloud:

- [ ] Bot works locally (tested)
- [ ] `.env` file has all required variables
- [ ] `requirements.txt` is up to date
- [ ] Code is in a Git repository (GitHub/GitLab)
- [ ] Media files are uploaded (or use URLs)
- [ ] Bot token is valid

---

## 🔧 Required Files for Cloud Deployment

### 1. `Procfile` (for Heroku/Railway)
```
worker: python -m codexs_bot.bot
```

### 2. `runtime.txt` (optional, specify Python version)
```
python-3.12.0
```

### 3. `requirements.txt` (already exists)
```
python-telegram-bot==21.5
python-dotenv==1.0.1
httpx==0.27.0
```

### 4. Update `.env` for cloud
- Use environment variables in cloud platform
- Don't commit `.env` to Git (use `.gitignore`)

---

## 🎯 Quick Start: Railway (Recommended)

**Fastest way to get 24/7 hosting:**

1. **Push code to GitHub:**
   ```bash
   git init
   git add .
   git commit -m "Initial commit"
   git remote add origin your-github-repo-url
   git push -u origin main
   ```

2. **Go to Railway:**
   - https://railway.app
   - Sign up with GitHub
   - "New Project" → "Deploy from GitHub repo"
   - Select your repo

3. **Add environment variables:**
   - Click on your service
   - Go to "Variables" tab
   - Add:
     - `BOT_TOKEN`
     - `ENABLE_MEDIA=true`
     - `GROUP_CHAT_ID=-5094334512`

4. **Deploy:**
   - Railway auto-detects Python
   - Installs dependencies
   - Starts bot automatically
   - **Bot runs 24/7!** ✅

---

## 💰 Cost Comparison

| Platform | Free Tier | Paid (24/7) | Ease of Use |
|----------|-----------|-------------|-------------|
| Railway | $5 credit/month | $5-10/month | ⭐⭐⭐⭐⭐ |
| Render | Limited free | $7/month | ⭐⭐⭐⭐ |
| DigitalOcean | No | $5/month | ⭐⭐⭐ |
| Heroku | No | $5/month | ⭐⭐⭐ |
| AWS EC2 | 12 months free | $10/month | ⭐⭐ |

---

## 🔍 Monitoring & Logs

Once deployed, monitor your bot:

**Railway:**
- View logs in Railway dashboard
- Real-time log streaming

**Render:**
- Logs tab in dashboard
- Can download logs

**DigitalOcean:**
- App logs in dashboard
- Can SSH for direct access

---

## 🚨 Important Notes

1. **Environment Variables:**
   - Never commit `.env` to Git
   - Set variables in cloud platform dashboard
   - Keep `BOT_TOKEN` secret

2. **Media Files:**
   - Upload to cloud storage (S3, Cloudinary)
   - Or use URLs instead of local files
   - Or include in deployment (larger size)

3. **Data Persistence:**
   - Cloud platforms may reset files
   - Consider using a database (PostgreSQL) for production
   - Or use cloud storage for voice files

4. **Scaling:**
   - One bot instance is usually enough
   - Don't run multiple instances (Telegram will rate limit)

---

## ✅ Recommendation

**For 24/7 hosting, I recommend Railway:**
- ✅ Easiest setup
- ✅ Free tier available
- ✅ Automatic deployments
- ✅ Good documentation
- ✅ Reliable uptime

**Next Steps:**
1. Push your code to GitHub
2. Sign up for Railway
3. Connect repo and deploy
4. Add environment variables
5. Bot runs 24/7! 🎉

---

## 🆘 Need Help?

If you need help with deployment:
1. Check platform-specific documentation
2. Verify environment variables are set
3. Check logs for errors
4. Test bot locally first

