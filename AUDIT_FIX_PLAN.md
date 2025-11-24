# 🔧 Audit Report Fix Plan

**Date:** 2025-01-27  
**Source:** Codexs Telegram Bot Audit Report (24 Nov 2025)  
**Status:** 🔴 **FIXING IN PROGRESS**

---

## 📋 Issues Identified

### **1. Main Menu and Navigation**

#### Issue 1.1: Missing "My applications" button
- **Problem:** Button sometimes fails to display after certain flows
- **Root Cause:** Need to verify all places where menu is shown
- **Fix:** Ensure `main_menu_labels()` always includes history button

#### Issue 1.2: Inconsistent naming
- **Problem:** "About Codex" vs "About Codexs"
- **Status:** ✅ Already fixed (verified in code)
- **Action:** Double-check all instances

#### Issue 1.3: Language switching glitch
- **Problem:** Menu buttons hide/shuffle after language switch
- **Fix:** Ensure menu refreshes properly after language switch

---

### **2. Apply for Jobs Flow**

#### Issue 2.1: Draft handling
- **Problem:** Selecting "Yes" to discard doesn't fully clear draft
- **Fix:** Ensure `reset_hiring()` and `delete_session()` are both called, clear all state

#### Issue 2.2: Ghost drafts
- **Problem:** Draft reopens automatically after discarding
- **Fix:** Ensure session file is deleted and state is fully cleared

#### Issue 2.3: Keyboard triggers
- **Problem:** Keyboard starts application unintentionally
- **Fix:** Add better validation for menu button presses

#### Issue 2.4: Lack of progress indicator
- **Status:** ✅ Already implemented (progress bar in `ask_current_question()`)
- **Action:** Verify it's always shown

---

### **3. About Codexs Section**

#### Issue 3.1: Branding inconsistency
- **Status:** ✅ Already fixed
- **Action:** Verify all instances

#### Issue 3.2: Open roles loop
- **Problem:** "Yes, show me open roles" leads back to main menu
- **Fix:** Ensure it properly starts application flow

#### Issue 3.3: Prompt-injection risk
- **Problem:** Need to ensure prompts don't override system guidelines
- **Fix:** Review prompt handling

---

### **4. Updates & News Section**

#### Issue 4.1: Non-functional
- **Problem:** Only echoes button label, never shows content
- **Fix:** Ensure `share_updates()` properly displays content or shows "no updates" message

#### Issue 4.2: Expectation management
- **Fix:** Show content or clear "no updates" message

---

### **5. Contact & Support Flow**

#### Issue 5.1: Confusing flow
- **Problem:** Multiple prompts, unclear send/cancel options
- **Fix:** Simplify flow, add clear Send/Cancel buttons

#### Issue 5.2: No draft review
- **Problem:** No way to review message before sending
- **Fix:** Add review step with Send/Cancel buttons

#### Issue 5.3: Unexpected prompts
- **Problem:** "View open roles" appears during contact flow
- **Fix:** Ensure `awaiting_view_roles` is not set during contact flow

---

### **6. Application History**

#### Issue 6.1: Missing button
- **Problem:** Button intermittently disappears
- **Fix:** Ensure menu always includes history button

#### Issue 6.2: Static card
- **Problem:** No way to view full details
- **Fix:** Add detail view option (future enhancement - note for now)

#### Issue 6.3: Voice sample status
- **Problem:** Can't play or verify voice
- **Fix:** Add replay option (future enhancement - note for now)

---

### **7. Language Switching**

#### Issue 7.1: Partial translation
- **Problem:** Some text remains in previous language
- **Fix:** Ensure all text refreshes after language switch

#### Issue 7.2: Button visibility
- **Problem:** Menu options hide after language switch
- **Fix:** Ensure menu is properly refreshed

---

## 🔧 Implementation Plan

### **Phase 1: Critical Fixes**

1. **Fix draft clearing** - Ensure complete state reset
2. **Fix Updates section** - Ensure content displays or shows "no updates"
3. **Fix About section open roles** - Ensure it starts application flow
4. **Fix contact flow** - Simplify and add review step
5. **Fix menu consistency** - Ensure history button always shown

### **Phase 2: UX Improvements**

1. **Improve language switching** - Full refresh
2. **Add contact review step** - Send/Cancel buttons
3. **Fix unexpected prompts** - Prevent cross-flow leakage

### **Phase 3: Verification**

1. Test all flows
2. Verify menu consistency
3. Test draft clearing
4. Test language switching

---

## 📝 Notes

- Some issues (voice replay, detailed view) are future enhancements
- Focus on fixing broken functionality first
- Ensure all fixes maintain backward compatibility

