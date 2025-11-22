# 🔴 Critical Logic Issues Found

## Issue 1: Resume Flow - Field Cleared Too Early ⚠️ CRITICAL

**Location:** `bot.py:814-815`

**Problem:**
```python
original_flow = session.exit_confirmation_flow
session.exit_confirmation_flow = None  # ❌ CLEARED TOO EARLY!
```

**What happens:**
1. User has incomplete application, bot shows resume prompt
2. User sends text (not Yes/No)
3. Code clears `exit_confirmation_flow` on line 815
4. User sends another message
5. Condition on line 812 fails because `exit_confirmation_flow` is None
6. User is STUCK - can't resume, can't proceed

**Fix:** Only clear `exit_confirmation_flow` AFTER processing the response (Yes/No), not before.

---

## Issue 2: Field Name Conflict - exit_confirmation_flow Used for Two Purposes ⚠️ CRITICAL

**Location:** `bot.py:404` and `session.py:83`

**Problem:**
- `exit_confirmation_flow` is used for:
  1. Storing flow during exit confirmation (normal use)
  2. Storing original flow during resume prompt (hack)

**What happens:**
- If user is in exit confirmation AND has incomplete application, these conflict
- The field gets overwritten, losing the original purpose

**Fix:** Use a separate field like `resume_original_flow` for resume logic.

---

## Issue 3: Resume from CONFIRM - Missing Edit Mode Check ⚠️ HIGH

**Location:** `bot.py:826-829`

**Problem:**
```python
elif original_flow == Flow.CONFIRM:
    session.flow = Flow.CONFIRM
    await prompt_confirmation(update, session)
```

**What happens:**
- User was editing question 5
- Bot restarts
- User resumes
- Code goes to CONFIRM, but doesn't check if they were in edit mode
- User loses their edit context

**Fix:** Check `edit_mode` and `awaiting_edit_selection` when resuming from CONFIRM.

---

## Issue 4: Menu Command During Resume Prompt ⚠️ MEDIUM

**Location:** `bot.py:856-862`

**Problem:**
- User is in resume prompt state (flow = IDLE, has_incomplete_application = True)
- User sends `/menu`
- Code checks `_needs_exit_confirmation()` which returns True
- Shows exit confirmation, but user is already in resume prompt

**What happens:**
- Confusing UX - user sees exit confirmation when they're trying to go to menu
- Should handle resume prompt state specially

**Fix:** Check for resume prompt state before checking exit confirmation.

---

## Issue 5: Resume Progress Count - Includes Empty Strings ⚠️ LOW

**Location:** `bot.py:847`

**Problem:**
```python
progress=len([v for v in session.answers.values() if v])
```

**What happens:**
- If user skipped optional questions, empty strings might be counted
- Progress count might be inaccurate

**Fix:** Already fixed in line 396, but line 847 still uses old logic.

---

## Issue 6: Resume Flow - No Check for awaiting_edit_selection ⚠️ MEDIUM

**Location:** `bot.py:826-832`

**Problem:**
- When resuming, we restore `awaiting_edit_selection` (line 395)
- But in resume logic, we don't check if user was waiting to select edit
- If they were at "Select question to edit", they should resume there

**Fix:** Check `awaiting_edit_selection` when resuming and restore that state.

---

## Issue 7: Exit Confirmation During Resume Prompt ⚠️ MEDIUM

**Location:** `bot.py:812-854`

**Problem:**
- User is in resume prompt state
- User tries to exit (sends back/menu)
- Code might show exit confirmation
- But user is already in a prompt state (resume)

**What happens:**
- Confusing - two prompts at once
- Should handle resume prompt state first

**Fix:** Check resume prompt state before exit confirmation.

---

## Summary

**Critical Issues:** 2
**High Priority:** 1
**Medium Priority:** 3
**Low Priority:** 1

**Total:** 7 logic issues found

