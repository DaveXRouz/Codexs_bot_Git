# 📋 Complete BotFather Commands List

**Use this to set up all bot commands in BotFather.**

---

## 🚀 How to Set Commands in BotFather

1. Open [@BotFather](https://t.me/BotFather) in Telegram
2. Send: `/setcommands`
3. Select your bot
4. Copy and paste the commands below (exactly as shown)
5. Send the message

---

## ✅ Complete Commands List

Copy this **entire block** and paste it into BotFather:

```
start - Start the Codexs bot and select your language
menu - Return to the main menu
help - Get help and see what I can do for you
commands - List all available commands
admin - Admin panel (admin only)
status - Bot health and status (admin only)
stats - Application statistics (admin only)
debug - Debug user session (admin only)
sessions - List active sessions (admin only)
cleanup - Clean up old session files (admin only)
testadmin - Verify admin access (admin only)
testgroup - Test group notifications (admin only)
daily - Today's application report (group admin only)
report - Today's application report (group admin only)
gstats - Detailed statistics (group admin only)
recent - List recent applications (group admin only)
app - View application details by ID (group admin only)
ghelp - Show group commands help (group admin only)
```

---

## 📊 Commands Breakdown

### 🌐 Public Commands (Available to Everyone)
- `/start` - Start the bot and select language
- `/menu` - Return to main menu
- `/help` - Get help information
- `/commands` - List all available commands

### 🔐 Admin Commands (Admin Only)
- `/admin` - Admin panel menu
- `/status` - Bot health and status
- `/stats` - Application statistics
- `/debug <user_id>` - Debug user session
- `/sessions` - List active sessions
- `/cleanup` - Clean up old session files
- `/testadmin` - Verify admin access
- `/testgroup` - Test group notifications

### 👥 Group Commands (Group Admin Only)
- `/daily` or `/report` - Today's application report
- `/gstats` - Detailed statistics
- `/recent` - List recent applications
- `/app <id>` - View application details by ID
- `/ghelp` - Show group commands help

---

## 📝 Notes

1. **Command Descriptions:** These descriptions appear when users type "/" in Telegram, helping them discover available commands.

2. **Access Control:** 
   - Public commands work for everyone
   - Admin commands require user ID in `ADMIN_USER_IDS`
   - Group commands require Telegram group admin status (or fallback to `ADMIN_USER_IDS`)

3. **Command Aliases:** 
   - `/daily` and `/report` do the same thing (both show daily report)
   - Both are included for user convenience

4. **Command Format:** 
   - Format: `command - description`
   - One command per line
   - Descriptions should be clear and concise

---

## ✅ After Setting Commands

Once you've set the commands in BotFather:
- Users will see command suggestions when typing "/" in Telegram
- Command descriptions will appear in the autocomplete menu
- All commands will be discoverable and documented

---

**Last Updated:** 2025-01-27  
**Total Commands:** 16 commands (4 public + 8 admin + 4 group)

