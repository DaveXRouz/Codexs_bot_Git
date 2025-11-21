# Codexs Bot - Deployment & Running Guide

## 🚀 How to Keep the Bot Running

The bot needs to run continuously to respond to users. Here are several options:

---

## Option 1: Background Script (Simple) ⭐ Recommended for Testing

### Start Bot in Background
```bash
cd /Users/hamzeh/Desktop/Person/codexs_bot
./scripts/run_bot_background.sh
```

**What this does:**
- Runs bot in background using `nohup`
- Survives terminal closure
- Logs to `logs/bot.log`
- Saves process ID to `bot.pid`

### Stop Bot
```bash
./scripts/stop_bot.sh
```

### Check if Bot is Running
```bash
ps aux | grep codexs-bot | grep -v grep
```

### View Logs
```bash
tail -f logs/bot.log
```

**Note:** If you restart your computer, you'll need to start the bot again.

---

## Option 2: macOS Launch Agent (Permanent) ⭐ Recommended for Production

This makes the bot start automatically on system boot and restart if it crashes.

### Install Launch Agent

1. **Copy the plist file:**
   ```bash
   cp scripts/com.codexs.bot.plist ~/Library/LaunchAgents/
   ```

2. **Load the service:**
   ```bash
   launchctl load ~/Library/LaunchAgents/com.codexs.bot.plist
   ```

3. **Start the bot:**
   ```bash
   launchctl start com.codexs.bot
   ```

### Manage the Service

**Start:**
```bash
launchctl start com.codexs.bot
```

**Stop:**
```bash
launchctl stop com.codexs.bot
```

**Unload (remove from auto-start):**
```bash
launchctl unload ~/Library/LaunchAgents/com.codexs.bot.plist
```

**Check status:**
```bash
launchctl list | grep codexs
```

**View logs:**
```bash
tail -f logs/bot.log
tail -f logs/bot.error.log
```

**Benefits:**
- ✅ Starts automatically on boot
- ✅ Restarts automatically if it crashes
- ✅ Runs in background permanently
- ✅ Survives terminal closure and logout

---

## Option 3: Screen/Tmux (Terminal Multiplexer)

### Using Screen

1. **Start a screen session:**
   ```bash
   screen -S codexs-bot
   ```

2. **Run the bot:**
   ```bash
   cd /Users/hamzeh/Desktop/Person/codexs_bot
   source .venv/bin/activate
   codexs-bot
   ```

3. **Detach (keep running):**
   Press `Ctrl+A` then `D`

4. **Reattach later:**
   ```bash
   screen -r codexs-bot
   ```

5. **List sessions:**
   ```bash
   screen -ls
   ```

### Using Tmux

1. **Start tmux:**
   ```bash
   tmux new -s codexs-bot
   ```

2. **Run the bot:**
   ```bash
   cd /Users/hamzeh/Desktop/Person/codexs_bot
   source .venv/bin/activate
   codexs-bot
   ```

3. **Detach:**
   Press `Ctrl+B` then `D`

4. **Reattach:**
   ```bash
   tmux attach -t codexs-bot
   ```

---

## Option 4: PM2 (Process Manager)

If you have Node.js installed, PM2 is excellent for managing Python processes.

### Install PM2
```bash
npm install -g pm2
```

### Start Bot with PM2
```bash
cd /Users/hamzeh/Desktop/Person/codexs_bot
pm2 start .venv/bin/codexs-bot --name codexs-bot --interpreter python3
```

### PM2 Commands
```bash
pm2 list              # List all processes
pm2 logs codexs-bot    # View logs
pm2 stop codexs-bot    # Stop bot
pm2 restart codexs-bot # Restart bot
pm2 delete codexs-bot  # Remove from PM2
pm2 save              # Save process list
pm2 startup           # Auto-start on boot
```

---

## Option 5: Cloud Hosting (Production)

For production, consider hosting on:
- **Heroku** - Easy deployment
- **DigitalOcean** - VPS with full control
- **AWS EC2** - Scalable cloud hosting
- **Railway** - Simple Python hosting
- **Render** - Free tier available

---

## 📋 Quick Reference

### Current Status
```bash
# Check if running
ps aux | grep codexs-bot | grep -v grep

# View logs
tail -f logs/bot.log
```

### Start Bot
```bash
# Simple background
./scripts/run_bot_background.sh

# Or with launchd (permanent)
launchctl start com.codexs.bot
```

### Stop Bot
```bash
# Simple
./scripts/stop_bot.sh

# Or with launchd
launchctl stop com.codexs.bot
```

---

## 🔧 Troubleshooting

### Bot Not Responding
1. Check if it's running: `ps aux | grep codexs-bot`
2. Check logs: `tail -f logs/bot.log`
3. Restart: `./scripts/stop_bot.sh && ./scripts/run_bot_background.sh`

### Bot Crashes
- Check error logs: `tail -f logs/bot.error.log`
- Verify `.env` file has correct `BOT_TOKEN`
- Check internet connection
- Verify Python dependencies: `pip list | grep telegram`

### Permission Issues
```bash
chmod +x scripts/*.sh
```

---

## 💡 Recommendation

**For Development/Testing:**
- Use **Option 1** (background script) - Simple and easy to manage

**For Production:**
- Use **Option 2** (launchd) - Automatic startup, crash recovery, most reliable on macOS

---

## 📝 Notes

- The bot needs internet connection to work
- Make sure `.env` file is configured correctly
- Logs are saved in `logs/` directory
- Bot token must be valid and active

