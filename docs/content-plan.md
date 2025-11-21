# Content & Media Plan – Codexs Bot Revamp

This document translates the audit findings into concrete copy, translation, and media updates to be reflected in `localization.py`, `bot.py`, and supporting assets.

## 1. Entry & Language Selection
| Context | English Copy | Farsi Copy |
| --- | --- | --- |
| Welcome (post-language choice) | “Welcome to **Codexs**. Select what you’d like to do.” | «به **Codexs** خوش آمدید. لطفاً مقصد خود را انتخاب کنید.» |
| Language prompt (pre-choice) | “Tap a language to continue ↓” | «برای ادامه زبان را انتخاب کنید ↓» |
| Main menu prompt | “Main menu · Pick a focus area.” | «منوی اصلی · یکی از بخش‌ها را انتخاب کنید.» |
| Menu helper | “Use the blue buttons below. You can always tap ⬅️ Back to main menu.” | «با دکمه‌های آبی زیر کار کنید و هر زمان خواستید ⬅️ بازگشت به منوی اصلی را بزنید.» |

## 2. Hiring Flow Copy Refresh
### Question Prompts (English → Farsi)
1. `Full legal name?` → «نام و نام خانوادگی کامل؟»
2. `Best email for Codexs follow-ups?` → «ایمیلی که برای پیگیری Codexs استفاده کنیم؟»
3. `Telegram @handle or phone (with country code)?` → «آیدی تلگرام یا شماره تماس (با کد کشور)؟»
4. `City + time zone?` → «شهر و منطقه زمانی؟»
5. `Role focus (choose button)` → same buttons, ensure FA labels are RTL.
6. `Key skills / stack (comma separated)?` → «مهارت‌های کلیدی / استک (با ویرگول جدا کنید)؟»
7. `Years of relevant experience?` → localized buttons.
8. `Portfolio / case link (or short note)?` → «لینک نمونه‌کار یا توضیح کوتاه؟»
9. `Earliest start date?` → «زودترین تاریخ شروع؟»
10. `Preferred working hours or overlap window?` → «ساعات کاری ترجیحی یا بازه هم‌پوشانی؟»
11. `Why Codexs? What gets you excited?` → «چرا Codexs؟ چه چیزی شما را جذب می‌کند؟»
12. Optional salary → instruct per language: `Type "Skip" to skip` vs «کلمه «رد کردن» را بنویسید اگر نمی‌خواهید بگویید.»

### Instructional Text
- `HIRING_INTRO_EN`: “This form has 12 short questions (~3 min). Answers stay confidential with the Codexs hiring team.”
- `HIRING_INTRO_FA`: localized equivalent.
- Progress hint appended to each question: `Question {current}/{total}` via helper.
- Reminder before voice: “You can tap ⬅️ Back to exit; your answers stay saved until you confirm.”

## 3. Voice Sample
- English paragraph remains the same; add localized explanation:
  - EN: “Read the paragraph below in English (30–45 seconds).”
  - FA: «لطفاً متن انگلیسی زیر را بلند بخوانید (۳۰ تا ۴۵ ثانیه کافی است).»
- Add optional skip/reschedule button: `🎙 Skip voice for now` / «🎙 فعلاً رد کردن ویس». Set expectation: “If skipped, team may follow up later.”

## 4. Confirmation & Editing
- Summary header: `Review your data before sending to Codexs`.
- Provide buttons for each question in edit keypad labelled `1 • Full name`, etc. (English & Farsi).
- Add note after summary: “Reply with a number to edit or tap ✅ Send.”

## 5. About / Updates Storytelling
- Instead of repeating `ABOUT_TEXT`, show:
  1. “Codexs · Global automation studio” (brief).
  2. Cards from `ABOUT_SECTIONS`.
  3. CTA: `🔗 View open roles` and `⬅️ Back to main menu`.
- Farsi translations already drafted; refine for tone.

### Media Requirements
| Section | File | Notes |
| --- | --- | --- |
| About hero | `assets/about_hero.jpg` | Replace stock Unsplash; 1600×900. |
| Updates card 1 | `assets/update_systemx.jpg/mp4` | Visual of System X automation. |
| Updates card 2 | `assets/update_ops.jpg` | Ops pods/team shot. |
| Updates card 3 | `assets/update_culture.mp4` | Culture reel snippet. |
| Optional | `assets/hiring_banner.jpg`, `assets/contact_card.jpg` | To show at start of hiring/contact flows. |

Until assets arrive, disable images to keep UX clean (send text only).

## 6. Contact & Notifications
- Contact info text:
  - EN: “Email contact@codexs.ai or tap Yes to send us a short message here.”
  - FA: localized equivalent.
- After message: “Saved for the ops team. Expect a reply within 1–2 business days.”
- Add configuration for webhook/API so submissions include: name, email, phone, portfolio, voice path, Telegram ID, plus full answer dict.

## 7. Fallback / Help
- Provide `/menu` hint: “Type /menu anytime to restart.”
- Add `HELP_TEXT` to explain available commands in both languages.

## 8. Documentation Notes
- README section: “Updating copy & assets” referencing this plan.
- Mention how to obtain Telegram `file_id` if using uploaded assets rather than URLs.

