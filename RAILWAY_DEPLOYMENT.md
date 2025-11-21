# Railway Deployment Guide ✅

## Current Status

Your bot is deployed on Railway! Here's what you need to know:

### Environment Variables Set ✅
- ✅ `BOT_TOKEN` - Your Telegram bot token (masked for security)
- ✅ `DATA_DIR` - Set to `data`
- ✅ `ENABLE_MEDIA` - Set to `true`

### Railway System Variables (Auto-added)
Railway automatically provides these - you don't need to set them:
- `RAILWAY_PROJECT_NAME`
- `RAILWAY_ENVIRONMENT_NAME`
- `RAILWAY_SERVICE_NAME`
- `RAILWAY_PROJECT_ID`
- `RAILWAY_ENVIRONMENT_ID`
- `RAILWAY_SERVICE_ID`

## Monitoring Your Bot

### 1. Check Deployment Status
- Go to the **"Deployments"** tab to see build progress
- Status will show: Building → Deploying → Active

### 2. View Logs
- Click on the **"Deployments"** tab
- Click on the latest deployment
- View real-time logs to see:
  - Build progress
  - Bot startup messages
  - Any errors

### 3. Check Metrics
- Go to **"Metrics"** tab to see:
  - CPU usage
  - Memory usage
  - Network traffic

## Testing Your Bot

Once deployment shows "Active" or "Running":

1. **Open Telegram**
2. **Find your bot** (search for your bot's username)
3. **Send `/start`**
4. **Verify it responds** with the language selection

## Troubleshooting

### Bot Not Responding?

1. **Check Logs**:
   - Go to "Deployments" → Latest deployment → View logs
   - Look for errors or warnings

2. **Common Issues**:
   - **"Module not found"**: Check `requirements.txt` is correct
   - **"BOT_TOKEN invalid"**: Verify token in Variables tab
   - **"Import error"**: Check Python version (should be 3.11+)

3. **Restart Service**:
   - Go to "Settings" tab
   - Click "Restart" if needed

### Build Failed?

1. Check the build logs for errors
2. Common fixes:
   - Ensure `requirements.txt` has all dependencies
   - Verify `Procfile` or `railway.json` is correct
   - Check Python version compatibility

## Adding More Environment Variables

If you need to add webhooks later:

1. Go to **"Variables"** tab
2. Click **"+ New Variable"**
3. Add:
   - `APPLICATION_WEBHOOK_URL` = Your webhook URL
   - `APPLICATION_WEBHOOK_TOKEN` = Your bearer token
   - `CONTACT_WEBHOOK_URL` = Contact webhook URL
   - `GROUP_CHAT_ID` = Your Telegram group ID

## Bot Features Now Live

Once running, your bot will:
- ✅ Run 24/7 (even when your computer is off)
- ✅ Auto-restart on failures
- ✅ Handle job applications
- ✅ Process contact messages
- ✅ Support English and Farsi
- ✅ Save data to Railway's persistent storage

## Success Indicators

You'll know it's working when:
- ✅ Deployment status shows "Active"
- ✅ Logs show "Bot started" or similar
- ✅ Bot responds to `/start` in Telegram
- ✅ No errors in logs

---

**Your bot is now running in the cloud! 🎉**

