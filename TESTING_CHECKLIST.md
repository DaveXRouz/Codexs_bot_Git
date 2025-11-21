# Testing Checklist for Codexs Bot

## ✅ Pre-Testing Verification

- [x] Bot is running (Process ID: 21891)
- [x] All dependencies installed (`httpx` present)
- [x] Environment variables configured:
  - [x] `BOT_TOKEN` set
  - [x] `GROUP_CHAT_ID=-5094334512` configured
  - [x] `ENABLE_MEDIA=false` (media disabled)
- [x] No syntax errors in code
- [x] All code fixes implemented

---

## 🧪 Manual Testing Tasks

### Test 1: Full English Job Application Submission Flow

**Steps:**
1. Open Telegram and start the bot with `/start`
2. Select **🇬🇧 English** language
3. Verify welcome banner appears (if media enabled)
4. Click **💼 Apply for jobs**
5. Verify application intro message appears
6. Answer all 12 questions:
   - [ ] Q1: Full name
   - [ ] Q2: Email address
   - [ ] Q3: Contact (use 📱 Share Contact button)
   - [ ] Q4: Location (use 📍 Share Location button)
   - [ ] Q5: Role category (select from buttons)
   - [ ] Q6: Skills (type text)
   - [ ] Q7: Experience (select from buttons)
   - [ ] Q8: Portfolio (type text/URL)
   - [ ] Q9: Start date (select from buttons)
   - [ ] Q10: Working hours (select Morning/Night/Flexible)
   - [ ] Q11: Motivation (type text)
   - [ ] Q12: Salary (optional - can skip)
7. Verify voice prompt appears with mandatory text
8. Record and send English voice message (30-45 seconds)
9. Verify confirmation summary appears with all answers
10. Click **✅ Yes** to confirm
11. Verify thank you message appears
12. Verify CodeX logo image appears (if media enabled)
13. **Check Telegram group** - verify notification message appears with:
    - All application data formatted correctly
    - Voice message forwarded to group
    - Clickable Telegram ID link

**Expected Results:**
- ✅ All questions display with clean formatting
- ✅ Contact/Location sharing buttons work
- ✅ Voice recording is mandatory (cannot skip)
- ✅ Summary shows all answers correctly
- ✅ Group notification received with proper formatting
- ✅ Voice file forwarded to group

---

### Test 2: Full Farsi Job Application Submission Flow

**Steps:**
1. Open Telegram and start the bot with `/start`
2. Select **🇮🇷 فارسی** language
3. Verify welcome message in Farsi
4. Click **💼 ارسال درخواست همکاری**
5. Answer all 12 questions in Farsi:
   - [ ] Q1: نام و نام خانوادگی
   - [ ] Q2: ایمیل
   - [ ] Q3: تماس (استفاده از دکمه 📱)
   - [ ] Q4: موقعیت (استفاده از دکمه 📍)
   - [ ] Q5: دسته نقش
   - [ ] Q6: مهارت‌ها
   - [ ] Q7: سابقه
   - [ ] Q8: نمونه کارها
   - [ ] Q9: تاریخ شروع
   - [ ] Q10: شیفت کاری
   - [ ] Q11: انگیزه
   - [ ] Q12: حقوق (اختیاری)
6. Record and send English voice message
7. Verify confirmation in Farsi
8. Submit application
9. **Check Telegram group** - verify notification in Farsi format

**Expected Results:**
- ✅ All text in Farsi
- ✅ Persian digits displayed correctly
- ✅ Group notification formatted properly
- ✅ Voice forwarded successfully

---

### Test 3: About, Updates, Contact, and Language Switching Flows

#### 3.1 About Section Flow
- [ ] Click **🏢 About Codex**
- [ ] Verify 3 sections appear:
  - Mission Control
  - Operating Principles
  - Proof of Work
- [ ] Verify "Would you like to view open roles?" prompt appears
- [ ] Click **✅ Yes, show me open roles**
- [ ] Verify application flow starts
- [ ] Go back and click **⬅️ Back to main menu**
- [ ] Verify returns to main menu

#### 3.2 Updates Section Flow
- [ ] Click **📢 Updates & news**
- [ ] Verify update cards appear:
  - System X Automation Layer
  - Global Ops Pods (with image if media enabled)
  - Culture Reel 2025
- [ ] Verify "More launches" link appears
- [ ] Verify main menu button appears

#### 3.3 Contact Section Flow
- [ ] Click **📞 Contact & support**
- [ ] Verify contact info appears (email, website)
- [ ] Click **✅ Yes** to send message
- [ ] Type a test message
- [ ] Verify confirmation message appears
- [ ] **Check Telegram group** - verify contact message notification appears
- [ ] Go back and click **♻️ No, edit** (skip message)
- [ ] Verify returns to main menu

#### 3.4 Language Switching
- [ ] From English menu, click **🔁 Switch to فارسی**
- [ ] Verify menu switches to Farsi
- [ ] From Farsi menu, click **🔁 تغییر به English**
- [ ] Verify menu switches back to English

#### 3.5 Navigation & Back Buttons
- [ ] During application flow, click **⬅️ Back to main menu**
- [ ] Verify exit confirmation appears
- [ ] Click **✅ Yes** - verify returns to menu
- [ ] Click **♻️ No, edit** - verify continues application
- [ ] Test back button from all sections

---

## 🔍 Additional Edge Cases to Test

### Error Handling
- [ ] Send empty answer to required question - verify error message
- [ ] Send invalid input - verify graceful handling
- [ ] Try to skip voice recording - verify it's mandatory
- [ ] Test with very long text answers
- [ ] Test with special characters in answers

### Data Persistence
- [ ] Check `data/applications.jsonl` - verify application saved
- [ ] Check `data/contact_messages.jsonl` - verify contact message saved
- [ ] Check `data/voice_samples/` - verify voice file saved

### Group Notifications
- [ ] Verify notification formatting is readable
- [ ] Verify all fields show correct data (not "—")
- [ ] Verify Telegram ID is clickable
- [ ] Verify voice message is forwarded (not just text)
- [ ] Test with missing optional fields

---

## 📊 Test Results Template

```
Test Date: ___________
Tester: ___________

English Application Flow: [ ] Pass [ ] Fail
Notes: _________________________________

Farsi Application Flow: [ ] Pass [ ] Fail
Notes: _________________________________

About Section: [ ] Pass [ ] Fail
Notes: _________________________________

Updates Section: [ ] Pass [ ] Fail
Notes: _________________________________

Contact Section: [ ] Pass [ ] Fail
Notes: _________________________________

Language Switching: [ ] Pass [ ] Fail
Notes: _________________________________

Group Notifications: [ ] Pass [ ] Fail
Notes: _________________________________

Overall Status: [ ] Ready for Production [ ] Needs Fixes
```

---

## 🐛 Known Issues to Watch For

1. **Voice forwarding** - If voice doesn't forward, check:
   - `user_chat_id` is stored correctly
   - Bot has permission in group
   - Voice file_id is valid

2. **Contact/Location sharing** - If not working:
   - Verify buttons use `request_contact=True` / `request_location=True`
   - Check handlers are registered

3. **Group notifications** - If not received:
   - Verify `GROUP_CHAT_ID` is correct
   - Bot must be admin in group
   - Check bot logs for errors

---

## ✅ Completion Criteria

All tests pass when:
- [ ] English application flow completes successfully
- [ ] Farsi application flow completes successfully
- [ ] All menu sections work correctly
- [ ] Group notifications are received and formatted properly
- [ ] Voice messages are forwarded to group
- [ ] Data is persisted correctly
- [ ] No errors in bot logs

---

**Ready to test!** Start with Test 1 and work through each section systematically.

