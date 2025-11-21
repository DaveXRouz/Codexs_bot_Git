# QA Checklist – Codexs Bot (v2 flows)

Use this script whenever you deploy a new build.

## 1. Startup
- `source .venv/bin/activate && codexs-bot`
- Confirm console logs “Codexs Telegram bot started.”
- Send `/help` to verify helper text.

## 2. English Flow
1. `/start` → choose English → ensure welcome + menu helper render.
2. Apply for jobs:
   - Step through 12 questions, verifying progress indicator (Question X/12).
   - Test empty answer to trigger “Please share a short answer”.
   - On salary question type `Skip`.
3. After Q12, ensure voice prompt shows skip + back buttons.
4. Tap 🎙 Skip voice → confirm acknowledgement + summary shows “Skipped”.
5. Edit a field via keypad, resubmit, confirm thank-you message, JSONL append, webhook hit (inspect logs).

## 3. Farsi Flow
1. `/menu` → switch to فارسی.
2. Ensure all menu labels + helper text display RTL correctly.
3. Start hiring flow, answer a few questions, tap ⬅️ back, verify main menu returns and partial answers cleared.
4. Complete flow including actual voice note upload; confirm status line shows ✅.

## 4. About / Updates
- Trigger each option with `ENABLE_MEDIA=false` and true (if assets configured).
- Verify text-only fallback still looks clean when media disabled.

## 5. Contact & Support
1. Tap Contact & support → reply “Yes”.
2. Send a message; verify confirmation text and check JSONL + webhook payload.
3. Repeat but send free-text instead of Yes to confirm auto-capture works.

## 6. Error Handling
- Send random text outside any flow; bot should prompt to use menu or `/menu`.
- Type `/help` mid-flow to confirm helper works without breaking context.

## 7. Files & Logs
- Inspect `data/applications.jsonl`, `data/contact_messages.jsonl`, and `data/voice_samples/`.
- If `ENABLE_MEDIA=true`, ensure assets resolve; otherwise set flag back to false.

Document any regressions in this file along with the date tested.

