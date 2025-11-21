# Localization Audit – Codexs Bot (EN / FA)

## Scope
- Strings defined in `src/codexs_bot/localization.py`
- Focus on tone alignment, translation quality, functional clarity, numbering consistency, and media labels

## Findings

### Entry Experience
- `BILINGUAL_WELCOME` crams both languages in one block; first impression is cluttered and instead should greet in user language post selection. Recommend an English welcome plus a separate Farsi welcome shown only after choice.
- `LANGUAGE_PROMPT` is fine, but no direction on what happens next; could add “Tap 🇬🇧 or 🇮🇷 below to continue.”
- `MAIN_MENU_PROMPT` uses em dash message but lacks explicit reminder of available actions.

### Menu Labels / Buttons
- English text is polished, yet Farsi buttons mix borrowed English words (e.g., “مارکتینگ”) without RTL punctuation normalization.
- `MENU_LABELS["switch"]` uses Persian text “English” within RTL sentence—needs bidi-aware formatting or quotes.
- Keyboards default to Telegram blue; but no string indicates button color cues—should mention within copy (e.g., “Use the blue buttons below…”).

### Hiring Flow Questions
1. Numbering icons (`1️⃣`, Persian digits) inconsistent: EN uses emoji digits, FA uses localized digits but same emoji for 10/11/12. Consider using `localize_number()` for headings.
2. Some prompts combine multiple requests (e.g., question 3: “Telegram handle / phone or best contact method?”). Farsi version mirrors structure but could be clearer by separating slash alternatives.
3. `skills` question translation literally says “technologies you work” but could be “فناوری‌هایی که روی آن مسلط هستید”.
4. Optional salary question instructs to type “Skip” in EN but Farsi says «رد کردن» text; enforcement logic treats lowercase `skip`. Need to clarify accepted token in each language.
5. No confirmation text telling user they can type “Back to main menu” button mid flow.

### Voice Sample
- `VOICE_SAMPLE_TEXT` remains English in both versions; Farsi prompt embeds the same English paragraph, which could confuse candidates with limited English reading skills. Provide Farsi explanation + keep English paragraph inside quotes.
- No localized note about acceptable audio duration/format.

### Error / Edit Prompts
- `MISSING_ANSWER`, `INVALID_EDIT`, `VOICE_WAITING_REMINDER` fine but could mention available buttons (“یا دکمه بازگشت را بزنید”).
- `EDIT_PROMPT` instructs to send numbers 1-12 but doesn’t show bilingual numbering examples.

### About / Updates Content
- `ABOUT_TEXT` duplicates information later shown in `ABOUT_SECTIONS`, causing repetition. Need structural hierarchy: teaser -> sections -> CTA.
- Media captions currently reference stock Unsplash assets; once brand artwork is ready we should replace placeholders or suppress photos.
- `UPDATE_CARDS` call-to-action labels are English-only; Farsi records still show Latin URLs and might need localized CTA text plus parentheses for LTR links.

### Contact Flow
- `CONTACT_INFO` includes raw URL; add RTL-friendly parentheses and instruct to tap button to leave message.
- Success / skip texts are acceptable but could set expectation on response time.

### Miscellaneous
- `THANK_YOU` text states “feel free to explore other sections” but doesn’t provide button names.
- `VOICE_STATUS_*` strings should match whichever iconography we use in confirmation summary; maybe show localized statuses (“در انتظار بارگذاری”).

## Recommended Next Steps
1. Split welcome messaging per language selection and ensure keyboards follow immediately.
2. Rewrite hiring prompts with shorter sentences + bolded keywords; apply consistent numbering helper for both locales.
3. Localize the English paragraph instructions (explain in Farsi, keep English reading sample as quoted block).
4. Replace or remove stock `ABOUT_MEDIA` / `UPDATE_CARDS` images until on-brand assets supplied; update CTA labels for RTL readability.
5. Expand contact/thank-you copy to mention next steps, estimated response time, and button cues.
6. Update README to instruct operators on editing localization strings and asset references.

