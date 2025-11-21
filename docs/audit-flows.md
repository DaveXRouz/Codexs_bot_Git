# Conversation Flow Audit – Codexs Bot

## Overview
Inspection of `src/codexs_bot/bot.py` to identify UX, logic, and error-handling gaps across English & Farsi experiences.

## Entry / Language Selection
- `/start` sends bilingual wall of text before language is chosen → feels noisy and duplicates copy later. Should show neutral prompt first, then language-specific welcome.
- After language selection we jump straight into main menu with no confirmation or quick guidance (e.g., “Tap Apply to begin”).
- No persistence notice: users lose progress if they `/start` again mid-flow.

## Main Menu & Navigation
- Buttons rely on default Telegram blue. No visual grouping or emojis beyond labels; consider consistent ordering (e.g., Jobs first) and describe how to return to menu.
- `BACK_TO_MENU` button appended to every keyboard; however, `handle_text` resets entire flow immediately, discarding partially filled answers without warning.
- Switching languages mid-form resets collected answers silently.

## Hiring Flow (Apply for jobs)
- Questions asked sequentially but there’s no progress indicator (e.g., “3/12”). Could help manage user expectation.
- Validation:
  - Only checks empty string; no email/phone formatting hints or fallback for accidental button taps.
  - Optional salary question instructs EN users to type “Skip” but not localized in prompt for Farsi.
- Editing confirmation:
  - After summary, user can edit by entering a number but there’s no list of numbers shown at that stage (keyboard surfaces digits but text prompt doesn’t restate each question). Consider summarizing with numbered list + tap-to-edit buttons.
  - If user edits one answer, summary is regenerated but voice status remains whichever previous state; no path to re-upload voice sample if they want.
- Back button while answering simply dumps them to main menu—no “Are you sure?” guard.

## Voice Sample Handling
- While waiting for voice, any text produces reminder but there’s no escape besides “Back to main menu”. Could allow “Skip voice” if candidate cannot record.
- Non-English instructions direct them to read an English paragraph but do not explain pronunciation expectations or acceptable duration/format.
- File saving uses local filesystem; no notification to hiring team or auto-cleanup.

## About / Updates Flows
- `share_about_story` sends multiple text blocks sequentially plus image; there’s no navigation or “Next” buttons, so feed may feel spammy. Consider using carousel-like inline keyboard or Telegram albums.
- Updates logic always sends CTA in English (`More launches: ...`) even in Farsi flow; CTA buttons/links not localized.
- Media uses web URLs; if sending fails due to Telegram restrictions, fallback is plain text but no note explaining missing imagery.

## Contact Flow
- When user selects contact, bot asks “Would you like to send message?” but if they type free text without pressing Yes, it gets ignored (flow stays pending). We could detect plain text and interpret as message.
- After message submission, there is no confirmation ID or expectation on response time.
- No integration to actually notify humans beyond JSONL append → user might assume someone is alerted instantly.

## Error & Safety
- `FALLBACK_MESSAGE` loops when unknown input provided outside flows; no guidance like “Type /menu to reset.”
- No rate limiting or spam protection; malicious user could spam audio uploads, overwriting disk.

## Data / Notifications
- Applications saved to `applications.jsonl` only; no webhook/notification. Requirement from user: push to external API with name/email/phone/portfolio/voice/telegram id.
- Voice recordings stored locally but path shared only internally; not surfaced to ops team.

## Testing / Diagnostics
- No logging of state transitions or errors besides Telegram photo failures. Hard to audit candidate submissions from logs.

## Key Recommendations
1. Introduce language-specific welcome card after selection; store preference per user.
2. Enhance hiring flow with progress indicators, validation hints, and ability to re-record voice or skip (with justification).
3. Refactor About/Updates to optionally send inline keyboards or carousels; replace placeholder stock images with brand assets or disable until ready.
4. Improve contact flow to accept immediate messages and push them (plus applications) to provided external API endpoint.
5. Expand error handling: `/menu` hint, “confirm exit” prompt, logging around state resets.
6. Add configuration for notifications (Telegram admin chat, email, Slack, or custom webhook) to avoid silent submissions.

