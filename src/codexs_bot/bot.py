from __future__ import annotations

import html
import logging
import re
import time
import uuid
from collections import defaultdict
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Dict, List, Optional

from telegram import KeyboardButton, ReplyKeyboardMarkup, Update
from telegram.error import TelegramError
from telegram.ext import (
    Application,
    CommandHandler,
    ContextTypes,
    MessageHandler,
    filters,
)

from .ai import OpenAIFallback
from .config import load_settings
from .localization import (
    ABOUT_CTA,
    ABOUT_MEDIA,
    ABOUT_SECTIONS,
    ABOUT_TEXT,
    AI_RATE_LIMIT_MESSAGE,
    BACK_TO_MENU,
    BILINGUAL_WELCOME,
    COMMANDS_TEXT,
    CONTACT_SHARED_ACK,
    CONTACT_SHARED_NOTIFICATION,
    EXIT_CONFIRM_CANCEL,
    EXIT_CONFIRM_DONE,
    EXIT_CONFIRM_PROMPT,
    FALLBACK_MESSAGE,
    HELP_TEXT,
    CONTACT_DECISION_REMINDER,
    CONTACT_INFO,
    CONTACT_MESSAGE_PROMPT,
    CONTACT_SKIP,
    CONTACT_THANKS,
    CONFIRM_PROMPT,
    CONFIRMATION_IMAGE_CAPTION,
    EDIT_PROMPT,
    ERROR_CONTACT_INVALID,
    ERROR_EMAIL_INVALID,
    ERROR_GENERIC,
    ERROR_GROUP_NOTIFICATION_FAILED,
    ERROR_LOCATION_INVALID,
    ERROR_VOICE_INVALID,
    ERROR_VOICE_TOO_LARGE,
    ERROR_TEXT_TOO_LONG,
    HELP_TEXT_APPLY,
    HELP_TEXT_VOICE,
    HIRING_INTRO,
    HIRING_QUESTIONS,
    INVALID_EDIT,
    LANDING_CARD_CAPTION,
    LANGUAGE_PROMPT,
    LANGUAGE_REMINDER,
    Language,
    LOCATION_SHARED_ACK,
    MAIN_MENU_PROMPT,
    MENU_HELPER,
    MENU_LABELS,
    MENU_TOPIC_TITLES,
    MISSING_ANSWER,
    SHARE_CONTACT_BUTTON,
    SHARE_LOCATION_BUTTON,
    SKIPPED_TEXT,
    SMART_FALLBACK_HINT,
    SUMMARY_HEADER,
    THANK_YOU,
    UPDATES,
    UPDATE_CARDS,
    UPDATES_CTA,
    UPDATES_LINK,
    VIEW_ROLES_NO,
    VIEW_ROLES_YES,
    VOICE_ACK,
    VOICE_PROMPT,
    VOICE_STATUS_LINE,
    VOICE_STATUS_PENDING,
    VOICE_STATUS_SKIPPED,
    VOICE_STATUS_RECEIVED,
    VOICE_WAITING_REMINDER,
    WELCOME_MESSAGE,
    QUESTION_PROGRESS,
    RATE_LIMIT_MESSAGE,
    RERECORD_VOICE_PROMPT,
    back_keyboard,
    contact_keyboard,
    edit_keyboard,
    get_language_from_button,
    is_back_button,
    is_no,
    is_yes,
    is_skip,
    language_keyboard,
    location_keyboard,
    main_menu_labels,
    yes_no_keyboard,
    switch_language,
)
from .session import Flow, UserSession, get_session
from .storage import DataStorage
from .notifications import WebhookNotifier


logger = logging.getLogger(__name__)

# Rate limiting: track user requests per minute
_rate_limit_store: Dict[int, List[datetime]] = defaultdict(list)
RATE_LIMIT_MAX_REQUESTS = 20  # Max requests per minute
RATE_LIMIT_WINDOW = timedelta(minutes=1)

_MENU_KEYWORDS = {
    "apply": {
        Language.EN: ("apply", "application", "job", "career", "role", "position", "hire"),
        Language.FA: ("درخواست", "شغل", "کار", "استخدام", "فرصت"),
    },
    "about": {
        Language.EN: ("about", "studio", "company", "codexs"),
        Language.FA: ("درباره", "استودیو", "codexs", "شرکت"),
    },
    "updates": {
        Language.EN: ("news", "update", "launch", "what's new", "latest"),
        Language.FA: ("خبر", "آپدیت", "به‌روزرسانی", "لانچ", "جدید"),
    },
    "contact": {
        Language.EN: ("contact", "support", "help", "reach", "message"),
        Language.FA: ("تماس", "پشتیبانی", "کمک", "پیام"),
    },
}

_MENU_COMMANDS = {
    Language.EN: {"menu", "mainmenu", "startover", "cancel", "stop", "quit", "restart"},
    Language.FA: {"منو", "منویاصلی", "بازگشتبمنو", "بازگشتبهمنو", "لغو"},
}

_BACK_COMMANDS = {
    Language.EN: {"back", "previous", "goback"},
    Language.FA: {"بازگشت", "برگشت", "قبلی"},
}

_REPEAT_COMMANDS = {
    Language.EN: {"repeat", "again", "what", "pardon", "huh"},
    Language.FA: {"تکرار", "دوباره", "چی", "??"},
}

_VIDEO_EXTENSIONS = {".mp4", ".mov", ".m4v", ".webm"}

AI_MAX_RESPONSES = 5
AI_WINDOW = timedelta(minutes=10)


def _check_rate_limit(user_id: int) -> bool:
    """Check if user has exceeded rate limit. Returns True if allowed, False if rate limited."""
    now = datetime.now(timezone.utc)
    user_requests = _rate_limit_store[user_id]
    
    # Remove old requests outside the window
    cutoff = now - RATE_LIMIT_WINDOW
    user_requests[:] = [req for req in user_requests if req > cutoff]
    
    # Check if limit exceeded
    if len(user_requests) >= RATE_LIMIT_MAX_REQUESTS:
        return False
    
    # Add current request
    user_requests.append(now)
    return True


def _format_hiring_intro(language: Language) -> str:
    """Format hiring intro with clean, minimal design."""
    intro_text = HIRING_INTRO[language]
    
    # Clean, minimal format
    return intro_text


def _normalize_for_intent(text: str) -> str:
    normalized = re.sub(r"[^a-zA-Z0-9\u0600-\u06FF\s]", " ", text)
    return normalized.lower()


def _collapse_intent_token(text: str) -> str:
    return _normalize_for_intent(text).replace(" ", "")


def _is_menu_command(text: str, language: Language) -> bool:
    collapsed = _collapse_intent_token(text)
    return collapsed in _MENU_COMMANDS[language]


def _is_back_command(text: str, language: Language) -> bool:
    collapsed = _collapse_intent_token(text)
    return collapsed in _BACK_COMMANDS[language]


def _is_repeat_command(text: str, language: Language) -> bool:
    collapsed = _collapse_intent_token(text)
    return collapsed in _REPEAT_COMMANDS[language] or text.strip() in {"?", "؟"}


def _match_menu_button(text: str, language: Language) -> Optional[str]:
    for key, labels in MENU_LABELS.items():
        if text == labels[language]:
            return key
    return None


def _infer_menu_choice(text: str, language: Language) -> Optional[str]:
    normalized = _normalize_for_intent(text)
    for key, language_map in _MENU_KEYWORDS.items():
        if language not in language_map:
            continue
        for keyword in language_map[language]:
            if keyword and keyword in normalized:
                return key
    return None


def _format_question_box(progress: str, question_text: str, language: Language) -> str:
    """Format question with clean, minimal design."""
    # Split question text into title and instruction if they exist
    lines = question_text.split('\n')
    title = lines[0] if lines else question_text
    instruction = '\n'.join(lines[1:]) if len(lines) > 1 else None
    
    # Clean, minimal design - Tesla/SpaceX aesthetic
    message_parts = [
        f"<b>{progress}</b>",
        "",
        f"{title}",
    ]
    
    if instruction:
        message_parts.extend([
            "",
            f"<i>{instruction}</i>",
        ])
    
    return "\n".join(message_parts)


def _keyboard_with_back(
    base_rows: Optional[List[List[str]]],
    language: Language,
    one_time: bool = False,
) -> ReplyKeyboardMarkup:
    rows = [list(row) for row in base_rows] if base_rows else []
    rows.append([BACK_TO_MENU[language]])
    return ReplyKeyboardMarkup(rows, resize_keyboard=True, one_time_keyboard=one_time)


def _language_keyboard() -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(
        language_keyboard(),
        resize_keyboard=True,
        one_time_keyboard=True,
    )


async def _send_photo_with_fallback(message, photo_url: Optional[str], caption: str, photo_path: Optional[Path] = None) -> None:
    if not message:
        return
    
    # Try local file first if provided
    if photo_path and photo_path.exists():
        try:
            with open(photo_path, "rb") as photo_file:
                await message.reply_photo(photo=photo_file, caption=caption, parse_mode="HTML")
            return
        except Exception as exc:
            logger.warning("Local photo send failed: %s", exc)
    
    # Fallback to URL if provided
    if photo_url:
        try:
            await message.reply_photo(photo=photo_url, caption=caption, parse_mode="HTML")
            return
        except TelegramError as exc:
            logger.warning("Photo URL send failed: %s", exc)
    
    # Fallback to text only
    await message.reply_text(caption, parse_mode="HTML")


async def _send_landing_card(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not update.message:
        return

    settings = _get_settings(context)
    if not settings.enable_media:
        await update.message.reply_text(LANDING_CARD_CAPTION, parse_mode="HTML")
        return

    hero_path: Optional[Path] = None
    for filename in [
        "landing-card.mp4",
        "landing-card.mov",
        "landing-card.webm",
        "landing-card.m4v",
        "landing-card.jpg",
        "landing-card.jpeg",
        "landing-card.png",
    ]:
        candidate = settings.media_dir / filename
        if candidate.exists():
            hero_path = candidate
            break

    if hero_path:
        try:
            with open(hero_path, "rb") as media_file:
                if hero_path.suffix.lower() in _VIDEO_EXTENSIONS:
                    await update.message.reply_video(
                        video=media_file,
                        caption=LANDING_CARD_CAPTION,
                        parse_mode="HTML",
                    )
                else:
                    await update.message.reply_photo(
                        photo=media_file,
                        caption=LANDING_CARD_CAPTION,
                        parse_mode="HTML",
                    )
                return
        except Exception as exc:
            logger.warning("Failed to send landing media: %s", exc)

    await update.message.reply_text(LANDING_CARD_CAPTION, parse_mode="HTML")


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not update.message:
        return
    session = get_session(context.user_data)
    session.reset_hiring()
    session.language = None
    session.flow = Flow.IDLE
    session.contact_pending = False
    await _send_landing_card(update, context)
    await update.message.reply_text(
        f"{BILINGUAL_WELCOME}\n\n"
        f"🇬🇧 {LANGUAGE_PROMPT[Language.EN]}\n"
        f"🇮🇷 {LANGUAGE_PROMPT[Language.FA]}",
        reply_markup=_language_keyboard(),
    )


async def menu_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not update.message:
        return
    session = get_session(context.user_data)
    if session.language is None:
        await start(update, context)
        return
    session.reset_hiring()
    session.flow = Flow.IDLE
    session.contact_pending = False
    await show_main_menu(update, session)


async def send_language_prompt(update: Update) -> None:
    if not update.message:
        return
    reminder = f"{LANGUAGE_REMINDER[Language.EN]}\n{LANGUAGE_REMINDER[Language.FA]}"
    await update.message.reply_text(reminder, reply_markup=_language_keyboard())


async def show_main_menu(update: Update, session: UserSession) -> None:
    if not update.message:
        return
    language = session.language or Language.EN
    session.last_menu_choice = None
    await update.message.reply_text(
        f"{MAIN_MENU_PROMPT[language]}\n{MENU_HELPER[language]}",
        reply_markup=ReplyKeyboardMarkup(
            main_menu_labels(language),
            resize_keyboard=True,
        ),
    )


async def send_language_welcome(update: Update, context: ContextTypes.DEFAULT_TYPE, session: UserSession) -> None:
    if not update.message:
        return
    language = session.language or Language.EN
    
    # Send welcome banner image if available
    settings = _get_settings(context)
    welcome_banner_path = None
    for ext in [".png", ".jpg", ".jpeg"]:
        path = settings.media_dir / f"welcome-banner{ext}"
        if path.exists():
            welcome_banner_path = path
            break
    
    if welcome_banner_path and settings.enable_media:
        try:
            with open(welcome_banner_path, "rb") as banner_file:
                await update.message.reply_photo(
                    photo=banner_file,
                    caption=WELCOME_MESSAGE[language],
                    parse_mode="HTML",
                )
        except Exception as exc:
            logger.warning(f"Failed to send welcome banner: {exc}")
            # Fallback to text only
            await update.message.reply_text(WELCOME_MESSAGE[language], parse_mode="HTML")
    else:
        await update.message.reply_text(WELCOME_MESSAGE[language], parse_mode="HTML")


def _resolve_language_choice(text: str) -> Optional[Language]:
    return get_language_from_button(text)


def _get_storage(context: ContextTypes.DEFAULT_TYPE) -> DataStorage:
    return context.application.bot_data["storage"]  # type: ignore[return-value]


def _get_settings(context: ContextTypes.DEFAULT_TYPE):
    return context.application.bot_data["settings"]


def _get_application_notifier(context: ContextTypes.DEFAULT_TYPE) -> WebhookNotifier:
    return context.application.bot_data["application_notifier"]


def _get_contact_notifier(context: ContextTypes.DEFAULT_TYPE) -> WebhookNotifier:
    return context.application.bot_data["contact_notifier"]


def _get_ai_responder(context: ContextTypes.DEFAULT_TYPE) -> Optional[OpenAIFallback]:
    return context.application.bot_data.get("ai_responder")  # type: ignore[return-value]


def _summarize_session_state(session: UserSession, language: Language) -> str:
    if session.flow == Flow.APPLY:
        summary = f"User is filling the hiring application (question {session.question_index + 1}/12)."
    elif session.flow == Flow.CONFIRM:
        summary = "User is reviewing answers before submission."
    elif session.flow == Flow.CONTACT_MESSAGE and session.contact_pending:
        summary = "User is deciding whether to leave a contact/support message."
    elif session.flow == Flow.CONTACT_MESSAGE:
        summary = "User is composing a contact/support message."
    elif session.waiting_voice:
        summary = "User must submit the mandatory English voice sample."
    else:
        summary = "User is at the main menu."

    extras: List[str] = []
    if session.last_menu_choice:
        topic = MENU_TOPIC_TITLES.get(session.last_menu_choice, {}).get(language)
        if topic:
            extras.append(f"Last selected focus: {topic}.")
    if session.answers:
        extras.append(f"{len([v for v in session.answers.values() if v])} answers saved so far.")
    if session.waiting_voice:
        extras.append("Voice sample is still pending.")
    return " ".join([summary] + extras)


def _build_ai_context(session: UserSession, language: Language) -> str:
    parts = [_summarize_session_state(session, language)]
    if session.flow == Flow.APPLY and 0 <= session.question_index < len(HIRING_QUESTIONS):
        question = HIRING_QUESTIONS[session.question_index]
        parts.append(f"Current question ({question.key}): {question.prompts[language]}")
    return "\n".join(parts)


def _reset_ai_window(session: UserSession) -> None:
    now = datetime.now(timezone.utc)
    if not session.ai_window_start or now - session.ai_window_start > AI_WINDOW:
        session.ai_window_start = now
        session.ai_reply_count = 0


def _needs_exit_confirmation(session: UserSession) -> bool:
    return (
        session.flow in {Flow.APPLY, Flow.CONFIRM, Flow.CONTACT_MESSAGE}
        or session.waiting_voice
        or session.contact_pending
        or session.awaiting_edit_selection
    )


async def _prompt_exit_confirmation(
    update: Update,
    session: UserSession,
    language: Language,
) -> None:
    session.request_exit_confirmation(session.flow or Flow.IDLE)
    await update.message.reply_text(
        EXIT_CONFIRM_PROMPT[language],
        reply_markup=ReplyKeyboardMarkup(yes_no_keyboard(language), resize_keyboard=True),
    )


async def _maybe_ai_reply(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
    session: UserSession,
    user_text: str,
) -> bool:
    responder = _get_ai_responder(context)
    if not responder or not responder.enabled:
        return False
    if not update.message:
        return False

    language = session.language or Language.EN
    _reset_ai_window(session)
    if session.ai_reply_count >= AI_MAX_RESPONSES:
        await update.message.reply_text(
            AI_RATE_LIMIT_MESSAGE[language],
            parse_mode="HTML",
            reply_markup=ReplyKeyboardMarkup(main_menu_labels(language), resize_keyboard=True),
        )
        return True

    context_text = _build_ai_context(session, language)
    ai_reply = await responder.generate_reply(language, context_text, user_text)
    if not ai_reply:
        return False

    await update.message.reply_text(
        ai_reply,
        parse_mode="HTML",
        reply_markup=ReplyKeyboardMarkup(main_menu_labels(language), resize_keyboard=True),
    )
    session.ai_reply_count += 1
    return True


async def _open_menu_section(
    key: str,
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
    session: UserSession,
    language: Language,
) -> None:
    if not update.message:
        return
    session.last_menu_choice = key

    if key == "apply":
        session.start_hiring()
        intro_formatted = _format_hiring_intro(language)
        await update.message.reply_text(
            intro_formatted,
            reply_markup=ReplyKeyboardMarkup(back_keyboard(language), resize_keyboard=True),
            parse_mode="HTML",
        )
        await ask_current_question(update, session)
        return

    if key == "about":
        await share_about_story(update, context, session, language)
        return

    if key == "updates":
        await share_updates(update, context, language)
        return

    if key == "contact":
        session.flow = Flow.CONTACT_MESSAGE
        session.contact_pending = True
        await update.message.reply_text(
            CONTACT_INFO[language],
            reply_markup=ReplyKeyboardMarkup(yes_no_keyboard(language), resize_keyboard=True),
        )
        return


async def handle_exit_confirmation(update: Update, session: UserSession, text: str) -> None:
    if not update.message:
        return
    language = session.language or Language.EN
    if is_yes(text, language):
        session.cancel_exit_confirmation()
        session.reset_hiring()
        await update.message.reply_text(
            EXIT_CONFIRM_DONE[language],
            reply_markup=ReplyKeyboardMarkup(main_menu_labels(language), resize_keyboard=True),
        )
        return
    if is_no(text, language):
        session.cancel_exit_confirmation()
        await update.message.reply_text(EXIT_CONFIRM_CANCEL[language])
        await resume_flow_after_cancel(update, session)
        return
    await update.message.reply_text(
        EXIT_CONFIRM_PROMPT[language],
        reply_markup=ReplyKeyboardMarkup(yes_no_keyboard(language), resize_keyboard=True),
    )


async def resume_flow_after_cancel(update: Update, session: UserSession) -> None:
    if not update.message:
        return
    language = session.language or Language.EN
    if session.waiting_voice:
        await update.message.reply_text(
            VOICE_PROMPT[language],
            reply_markup=_keyboard_with_back(None, language),
            parse_mode="HTML",
        )
        return
    if session.flow == Flow.APPLY:
        await ask_current_question(update, session)
        return
    if session.flow == Flow.CONFIRM:
        await prompt_confirmation(update, session)
        return
    if session.flow == Flow.CONTACT_MESSAGE and session.contact_pending:
        await update.message.reply_text(
            CONTACT_MESSAGE_PROMPT[language],
            reply_markup=_keyboard_with_back(None, language),
        )


async def handle_text(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not update.message or not update.message.text:
        return
    
    # Rate limiting check
    user_id = update.effective_user.id
    if not _check_rate_limit(user_id):
        language = get_session(context.user_data).language or Language.EN
        await update.message.reply_text(
            RATE_LIMIT_MESSAGE[language],
            parse_mode="HTML",
        )
        return
    
    text = update.message.text.strip()
    session = get_session(context.user_data)

    if session.language is None:
        choice = _resolve_language_choice(text)
        if choice is None:
            await send_language_prompt(update)
            return
        session.language = choice
        await send_language_welcome(update, context, session)
        await show_main_menu(update, session)
        return

    language = session.language

    if _is_menu_command(text, language) or _is_back_command(text, language):
        if _needs_exit_confirmation(session):
            await _prompt_exit_confirmation(update, session, language)
        else:
            session.reset_hiring()
            await show_main_menu(update, session)
        return

    if session.exit_confirmation_pending:
        await handle_exit_confirmation(update, session, text)
        return

    if is_back_button(text, language):
        if session.flow in {Flow.APPLY, Flow.CONFIRM} or session.waiting_voice:
            session.request_exit_confirmation(session.flow)
            await update.message.reply_text(
                EXIT_CONFIRM_PROMPT[language],
                reply_markup=ReplyKeyboardMarkup(yes_no_keyboard(language), resize_keyboard=True),
            )
        else:
            session.reset_hiring()
            await show_main_menu(update, session)
        return

    if session.waiting_voice:
        # Voice is mandatory, no skip allowed
        await update.message.reply_text(
            VOICE_WAITING_REMINDER[language],
            reply_markup=_keyboard_with_back(None, language),
            parse_mode="HTML",
        )
        return

    if session.awaiting_view_roles:
        if text == VIEW_ROLES_YES[language] or is_yes(text, language):
            session.awaiting_view_roles = False
            session.start_hiring()
            # Format hiring intro with visual design
            intro_formatted = _format_hiring_intro(language)
            await update.message.reply_text(
                intro_formatted,
                reply_markup=ReplyKeyboardMarkup(back_keyboard(language), resize_keyboard=True),
                parse_mode="HTML",
            )
            await ask_current_question(update, session)
            return
        elif text == VIEW_ROLES_NO[language] or is_back_button(text, language) or is_no(text, language):
            session.awaiting_view_roles = False
            await show_main_menu(update, session)
            return
        else:
            # Remind user to use buttons
            view_roles_keyboard = ReplyKeyboardMarkup(
                [[VIEW_ROLES_YES[language], VIEW_ROLES_NO[language]]],
                resize_keyboard=True,
            )
            await update.message.reply_text(
                ABOUT_CTA[language],
                reply_markup=view_roles_keyboard,
                parse_mode="HTML",
            )
            return

    if session.awaiting_edit_selection:
        number = _parse_number(text)
        # Allow editing questions 1-12, or 13 for voice re-recording
        if number is None or not (1 <= number <= len(HIRING_QUESTIONS) + 1):
            await update.message.reply_text(
                INVALID_EDIT[language],
                reply_markup=ReplyKeyboardMarkup(edit_keyboard(language), resize_keyboard=True),
                parse_mode="HTML",
            )
            return
        
        session.awaiting_edit_selection = False
        
        # If number is 13, allow re-recording voice
        if number == len(HIRING_QUESTIONS) + 1:
            session.mark_voice_wait()
            session.voice_file_path = None
            session.voice_file_id = None
            session.voice_message_id = None
            session.user_chat_id = None
            session.voice_skipped = False
            await update.message.reply_text(
                RERECORD_VOICE_PROMPT[language],
                reply_markup=_keyboard_with_back(None, language),
                parse_mode="HTML",
            )
            return
        
        # Otherwise, edit the selected question
        session.edit_mode = True
        session.question_index = number - 1
        await ask_current_question(update, session)
        return

    if session.flow == Flow.APPLY:
        await handle_application_answer(update, session, text)
        return

    if session.flow == Flow.CONFIRM:
        if is_yes(text, language):
            await finalize_application(update, context, session)
            return
        if is_no(text, language):
            session.awaiting_edit_selection = True
            await update.message.reply_text(
                EDIT_PROMPT[language],
                reply_markup=ReplyKeyboardMarkup(edit_keyboard(language), resize_keyboard=True),
            )
            return
        await update.message.reply_text(
            CONFIRM_PROMPT[language],
            reply_markup=ReplyKeyboardMarkup(yes_no_keyboard(language), resize_keyboard=True),
        )
        return

    if session.flow == Flow.CONTACT_MESSAGE:
        # Refactored contact flow for clarity
        if session.contact_pending:
            # User is deciding whether to send a message
            if is_yes(text, language):
                session.contact_pending = False
                await update.message.reply_text(
                    CONTACT_MESSAGE_PROMPT[language],
                    reply_markup=_keyboard_with_back(None, language),
                )
                return
            elif is_no(text, language):
                session.flow = Flow.IDLE
                session.contact_pending = False
                await update.message.reply_text(
                    CONTACT_SKIP[language],
                    reply_markup=ReplyKeyboardMarkup(main_menu_labels(language), resize_keyboard=True),
                )
                return
            else:
                # User sent text instead of Yes/No - treat as message
                session.contact_pending = False
                await save_contact_message(update, context, session, text)
                return
        else:
            # User is sending the actual message
            # Validate length first
            if not _validate_text_length(text, max_length=1000):
                await update.message.reply_text(
                    ERROR_TEXT_TOO_LONG[language],
                    reply_markup=_keyboard_with_back(None, language),
                    parse_mode="HTML",
                )
                return
            await save_contact_message(update, context, session, text)
            return

    await handle_main_menu_choice(update, context, session, text)


async def handle_main_menu_choice(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
    session: UserSession,
    text: str,
) -> None:
    if not update.message:
        return
    language = session.language or Language.EN
    session.contact_pending = False
    session.flow = Flow.IDLE
    session.last_menu_choice = None
    matched_key = _match_menu_button(text, language)
    if matched_key in {"apply", "about", "updates", "contact"}:
        await _open_menu_section(matched_key, update, context, session, language)
        return
    if matched_key == "switch":
        session.language = switch_language(language)
        await show_main_menu(update, session)
        return

    inferred_key = _infer_menu_choice(text, language)
    if inferred_key:
        topic = MENU_TOPIC_TITLES[inferred_key][language]
        await update.message.reply_text(
            SMART_FALLBACK_HINT[language].format(topic=topic),
            parse_mode="HTML",
        )
        await _open_menu_section(inferred_key, update, context, session, language)
        return

    if not await _maybe_ai_reply(update, context, session, text):
        await update.message.reply_text(
            FALLBACK_MESSAGE[language],
            reply_markup=ReplyKeyboardMarkup(main_menu_labels(language), resize_keyboard=True),
            parse_mode="HTML",
        )


async def share_about_story(update: Update, context: ContextTypes.DEFAULT_TYPE, session: UserSession, language: Language) -> None:
    if not update.message:
        return
    sections = ABOUT_SECTIONS.get(language, [])
    settings = context.application.bot_data["settings"]
    if not sections:
        await update.message.reply_text(ABOUT_TEXT[language], parse_mode="HTML")
    else:
        for section in sections:
            text = f"<b>{section['title']}</b>\n{section['body']}"
            await update.message.reply_text(text, parse_mode="HTML")
        media = ABOUT_MEDIA.get(language)
        if media and settings.enable_media and media.get("photo"):
            await _send_photo_with_fallback(
                update.message,
                media.get("photo"),
                media.get("caption", ""),
            )
    
    # Set flag to await user's response about viewing roles
    session.awaiting_view_roles = True
    view_roles_keyboard = ReplyKeyboardMarkup(
        [[VIEW_ROLES_YES[language], VIEW_ROLES_NO[language]]],
        resize_keyboard=True,
    )
    await update.message.reply_text(
        ABOUT_CTA[language],
        reply_markup=view_roles_keyboard,
        parse_mode="HTML",
    )


async def share_updates(update: Update, context: ContextTypes.DEFAULT_TYPE, language: Language) -> None:
    if not update.message:
        return
    cards = UPDATE_CARDS.get(language, [])
    settings = context.application.bot_data["settings"]
    if not cards:
        news = "\n".join(UPDATES[language])
        await update.message.reply_text(
            f"{news}\n\nMore: {UPDATES_LINK}",
            reply_markup=ReplyKeyboardMarkup(main_menu_labels(language), resize_keyboard=True),
        )
        return
    for card in cards:
        text = f"<b>{card['title']}</b>\n{card['body']}"
        if card.get("cta_url"):
            text += f"\n{card['cta_label']}: {card['cta_url']}"
        
        if settings.enable_media:
            # Check if this is Global Ops Pods card and use local file
            photo_path = None
            if card.get("title") in ["Global Ops Pods", "پادهای عملیات جهانی"]:
                # Try both .png and .jpg extensions
                for ext in [".png", ".jpg", ".jpeg"]:
                    ops_pods_path = settings.media_dir / f"global-ops-pods{ext}"
                    if ops_pods_path.exists():
                        photo_path = ops_pods_path
                        break
            
            await _send_photo_with_fallback(
                update.message,
                card.get("photo"),
                text,
                photo_path=photo_path,
            )
        else:
            await update.message.reply_text(text, parse_mode="HTML")
    await update.message.reply_text(
        f"{UPDATES_CTA[language]} {UPDATES_LINK}",
        reply_markup=ReplyKeyboardMarkup(main_menu_labels(language), resize_keyboard=True),
    )


async def ask_current_question(update: Update, session: UserSession) -> None:
    if not update.message:
        return
    language = session.language or Language.EN
    question = HIRING_QUESTIONS[session.question_index]
    
    # Determine keyboard based on input type
    if question.input_type == "contact":
        contact_btn = KeyboardButton(SHARE_CONTACT_BUTTON[language], request_contact=True)
        keyboard = ReplyKeyboardMarkup(
            [[contact_btn], [BACK_TO_MENU[language]]],
            resize_keyboard=True,
            one_time_keyboard=True,
        )
    elif question.input_type == "location":
        location_btn = KeyboardButton(SHARE_LOCATION_BUTTON[language], request_location=True)
        keyboard = ReplyKeyboardMarkup(
            [[location_btn], [BACK_TO_MENU[language]]],
            resize_keyboard=True,
            one_time_keyboard=True,
        )
    else:
        keyboard_rows = question.keyboard[language] if question.keyboard else None
        keyboard = _keyboard_with_back(keyboard_rows, language)
    
    progress = QUESTION_PROGRESS[language].format(
        current=session.question_index + 1,
        total=len(HIRING_QUESTIONS),
    )
    
    # Extract question text and instruction from prompts
    prompt_text = question.prompts[language]
    
    # Format with visual box design
    formatted_message = _format_question_box(progress, prompt_text, language)
    
    await update.message.reply_text(
        formatted_message,
        reply_markup=keyboard,
        parse_mode="HTML",
    )


def _validate_email(email: str) -> bool:
    """Basic email validation."""
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return bool(re.match(pattern, email.strip()))


def _validate_text_length(text: str, max_length: int = 1000) -> bool:
    """Validate text input length."""
    return len(text.strip()) <= max_length


def _sanitize_html(text: str) -> str:
    """Sanitize HTML by escaping special characters."""
    return html.escape(text, quote=True)


async def handle_application_answer(update: Update, session: UserSession, text: str) -> None:
    if not update.message:
        return
    language = session.language or Language.EN
    question = HIRING_QUESTIONS[session.question_index]
    cleaned = text.strip()
    if cleaned:
        if _is_menu_command(cleaned, language) or _is_back_command(cleaned, language) or is_back_button(cleaned, language):
            await _prompt_exit_confirmation(update, session, language)
            return
        if _is_repeat_command(cleaned, language):
            await ask_current_question(update, session)
            return

    if not cleaned and not question.optional:
        keyboard_rows = question.keyboard[language] if question.keyboard else None
        await update.message.reply_text(
            MISSING_ANSWER[language],
            reply_markup=_keyboard_with_back(keyboard_rows, language),
        )
        return

    if not question.optional and cleaned and is_skip(cleaned, language):
        keyboard_rows = question.keyboard[language] if question.keyboard else None
        await update.message.reply_text(
            MISSING_ANSWER[language],
            reply_markup=_keyboard_with_back(keyboard_rows, language),
        )
        return
    
    # Text length validation (prevent DoS attacks)
    if cleaned and not _validate_text_length(cleaned, max_length=1000):
        await update.message.reply_text(
            ERROR_TEXT_TOO_LONG[language],
            reply_markup=_keyboard_with_back(None, language),
            parse_mode="HTML",
        )
        return
    
    # Email validation for email question
    if question.key == "email" and cleaned:
        if not _validate_email(cleaned):
            await update.message.reply_text(
                ERROR_EMAIL_INVALID[language],
                reply_markup=_keyboard_with_back(None, language),
                parse_mode="HTML",
            )
            return
    
    if question.optional and cleaned and is_skip(cleaned, language):
        value: Optional[str] = None
    else:
        value = cleaned
    session.answers[question.key] = value
    logger.info(f"Saved answer for '{question.key}': '{value}' (Question {session.question_index + 1}/{len(HIRING_QUESTIONS)})")
    if session.edit_mode:
        session.edit_mode = False
        session.flow = Flow.CONFIRM
        await prompt_confirmation(update, session)
        return

    session.question_index += 1
    if session.question_index < len(HIRING_QUESTIONS):
        await ask_current_question(update, session)
    else:
        session.mark_voice_wait()
        session.voice_skipped = False
        await update.message.reply_text(
            VOICE_PROMPT[language],
            reply_markup=_keyboard_with_back(None, language),
            parse_mode="HTML",
        )


async def handle_voice(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not update.message:
        return
    session = get_session(context.user_data)
    language = session.language or Language.EN
    if not session.waiting_voice or session.language is None:
        await update.message.reply_text(
            ERROR_GENERIC[language],
            reply_markup=ReplyKeyboardMarkup(main_menu_labels(language), resize_keyboard=True),
        )
        return

    voice_message = update.message.voice
    audio_message = update.message.audio
    telegram_media = voice_message or audio_message
    language = session.language
    
    if telegram_media is None:
        await update.message.reply_text(
            ERROR_VOICE_INVALID[language],
            reply_markup=_keyboard_with_back(None, language),
            parse_mode="HTML",
        )
        return

    # Validate file size (max 20MB for Telegram voice messages)
    MAX_VOICE_SIZE = 20 * 1024 * 1024  # 20MB in bytes
    if telegram_media.file_size and telegram_media.file_size > MAX_VOICE_SIZE:
        await update.message.reply_text(
            ERROR_VOICE_TOO_LARGE[language],
            reply_markup=_keyboard_with_back(None, language),
            parse_mode="HTML",
        )
        return

    try:
        file = await telegram_media.get_file()
        settings = _get_settings(context)
        voice_dir: Path = settings.voice_dir
        if voice_message:
            extension = ".ogg"
        else:
            filename = (audio_message.file_name or "").strip() if audio_message else ""
            extension = Path(filename).suffix if filename else ".mp3"
        file_name = f"{update.effective_user.id}_{int(time.time())}{extension}"
        file_path = voice_dir / file_name
        await file.download_to_drive(file_path)
    except TelegramError as exc:
        logger.error(f"Failed to download voice file: {exc}", exc_info=True)
        await update.message.reply_text(
            ERROR_VOICE_INVALID[language],
            reply_markup=_keyboard_with_back(None, language),
            parse_mode="HTML",
        )
        return

    session.finish_voice_wait()
    session.voice_file_path = str(file_path)
    session.voice_file_id = telegram_media.file_id
    session.voice_message_id = update.message.message_id
    session.user_chat_id = update.effective_chat.id
    session.voice_skipped = False
    session.flow = Flow.CONFIRM
    logger.info(
        f"Voice received from user {update.effective_user.id}. "
        f"File ID: {telegram_media.file_id}, Message ID: {update.message.message_id}, "
        f"Saved to: {file_path}"
    )
    await update.message.reply_text(VOICE_ACK[language])
    await prompt_confirmation(update, session)


async def prompt_confirmation(update: Update, session: UserSession) -> None:
    if not update.message:
        return
    language = session.language or Language.EN
    session.flow = Flow.CONFIRM
    summary_lines = [SUMMARY_HEADER[language]]
    for question in HIRING_QUESTIONS:
        value = session.answers.get(question.key)
        if value is None:
            display = SKIPPED_TEXT[language]
        elif value:
            # Sanitize HTML in summary to prevent XSS
            display = _sanitize_html(str(value))
        else:
            display = "—"
        summary_lines.append(f"- {question.summary_labels[language]}: {display}")
    if session.voice_file_path:
        voice_status = VOICE_STATUS_RECEIVED[language]
    elif session.voice_skipped:
        voice_status = VOICE_STATUS_SKIPPED[language]
    else:
        voice_status = VOICE_STATUS_PENDING[language]
    summary_lines.append(VOICE_STATUS_LINE[language].format(status=voice_status))
    summary_lines.append(CONFIRM_PROMPT[language])
    await update.message.reply_text(
        "\n".join(summary_lines),
        reply_markup=ReplyKeyboardMarkup(yes_no_keyboard(language), resize_keyboard=True),
    )


async def finalize_application(update: Update, context: ContextTypes.DEFAULT_TYPE, session: UserSession) -> None:
    if not update.message:
        return
    language = session.language or Language.EN
    applicant = _applicant_payload(update)
    
    # Generate unique application ID
    application_id = f"APP-{uuid.uuid4().hex[:8].upper()}"
    
    logger.info(f"=== FINALIZING APPLICATION ===")
    logger.info(f"Application ID: {application_id}")
    logger.info(f"User: {applicant.get('username')} (ID: {applicant.get('telegram_id')})")
    logger.info(f"Session answers: {session.answers}")
    logger.info(f"Number of answers: {len(session.answers)}")
    logger.info(f"Voice file_id: {session.voice_file_id}")
    logger.info(f"Voice message_id: {session.voice_message_id}")
    logger.info(f"Voice skipped: {session.voice_skipped}")
    
    storage = _get_storage(context)
    await storage.save_application(
        applicant=applicant,
        answers=session.answers,
        language=language,
        voice_file_path=session.voice_file_path,
        voice_file_id=session.voice_file_id,
        application_id=application_id,
    )
    notifier = _get_application_notifier(context)
    await notifier.post(
        {
            "application_id": application_id,
            "submitted_at": datetime.now(timezone.utc).isoformat(),
            "language": language.value,
            "answers": session.answers,
            "full_name": session.answers.get("full_name"),
            "email": session.answers.get("email"),
            "contact": session.answers.get("contact"),
            "portfolio": session.answers.get("portfolio"),
            "voice_file_path": session.voice_file_path,
            "voice_file_id": session.voice_file_id,
            "voice_skipped": session.voice_skipped,
            "telegram_id": applicant["telegram_id"],
            "telegram_username": applicant["username"],
            "telegram_first_name": applicant["first_name"],
            "telegram_last_name": applicant["last_name"],
        }
    )
    # Store all data BEFORE reset_hiring() clears it!
    answers_copy = dict(session.answers)
    voice_file_id_for_group = session.voice_file_id
    voice_message_id_for_group = session.voice_message_id
    voice_path_for_group = session.voice_file_path
    voice_skipped_for_group = session.voice_skipped
    user_chat_id = session.user_chat_id or update.effective_chat.id
    
    session.is_candidate = True
    session.reset_hiring()  # This clears session.answers, but we have a copy
    
    # Send thank you message with application ID
    await update.message.reply_text(
        THANK_YOU[language].format(app_id=application_id),
        reply_markup=ReplyKeyboardMarkup(main_menu_labels(language), resize_keyboard=True),
        parse_mode="HTML",
    )
    
    # Send confirmation image with CodeX logo
    settings = _get_settings(context)
    # Try both .png and .jpg extensions
    confirmation_logo_path = None
    for ext in [".png", ".jpg", ".jpeg"]:
        path = settings.media_dir / f"codex-logo{ext}"
        if path.exists():
            confirmation_logo_path = path
            break
    
    if confirmation_logo_path:
        try:
            with open(confirmation_logo_path, "rb") as logo_file:
                await update.message.reply_photo(
                    photo=logo_file,
                    caption=CONFIRMATION_IMAGE_CAPTION[language],
                    parse_mode="HTML",
                )
        except Exception as exc:
            logger.warning(f"Failed to send confirmation logo: {exc}")
    else:
        logger.info(f"Confirmation logo not found in {settings.media_dir}. Skipping image.")
    
    # Now announce with the stored data
    await announce_group_submission(
        context, 
        applicant, 
        answers_copy,  # Use the copy, not session.answers (which is now empty)
        voice_path_for_group,
        voice_file_id_for_group,
        voice_message_id_for_group,
        user_chat_id,
        voice_skipped_for_group,
        application_id
    )


def _applicant_payload(update: Update) -> dict:
    user = update.effective_user
    return {
        "telegram_id": user.id,
        "username": user.username,
        "first_name": user.first_name,
        "last_name": user.last_name,
    }


async def save_contact_message(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
    session: UserSession,
    message: str,
) -> None:
    storage = _get_storage(context)
    language = session.language or Language.EN
    applicant = _applicant_payload(update)
    
    await storage.save_contact_message(
        applicant=applicant,
        language=language,
        message=message,
    )
    notifier = _get_contact_notifier(context)
    await notifier.post(
        {
            "submitted_at": datetime.now(timezone.utc).isoformat(),
            "language": language.value,
            "message": message,
            "sender": applicant,
        }
    )
    
    # Send to Telegram group
    await announce_contact_message(context, applicant, message, language)
    
    session.flow = Flow.IDLE
    session.contact_pending = False
    await update.message.reply_text(
        CONTACT_THANKS[language],
        reply_markup=ReplyKeyboardMarkup(main_menu_labels(language), resize_keyboard=True),
    )


def _parse_number(text: str) -> Optional[int]:
    translated = text.strip()
    persian_digits = str.maketrans("۰۱۲۳۴۵۶۷۸۹", "0123456789")
    translated = translated.translate(persian_digits)
    try:
        return int(translated)
    except ValueError:
        return None


async def announce_contact_message(
    context: ContextTypes.DEFAULT_TYPE,
    applicant: dict,
    message: str,
    language: Language,
) -> None:
    """Send contact message notification to the group."""
    chat_id = context.application.bot_data.get("group_chat_id")
    if not chat_id:
        return
    
    lang_label = "🇬🇧 EN" if language == Language.EN else "🇮🇷 FA"
    # Sanitize message content to prevent XSS
    sanitized_message = _sanitize_html(message)
    notification = "\n".join([
        f"{CONTACT_SHARED_NOTIFICATION[language]}",
        f"📝 Language: {lang_label}",
        f"👤 From: {applicant.get('first_name', '')} {applicant.get('last_name', '')}".strip(),
        f"🆔 @{applicant.get('username') or '—'} (ID {applicant.get('telegram_id')})",
        "",
        f"💬 Message:",
        f"{sanitized_message}",
    ])
    
    try:
        await context.bot.send_message(chat_id=chat_id, text=notification)
    except TelegramError as exc:
        logger.warning("Failed to send contact message to group: %s", exc)


async def announce_group_submission(
    context: ContextTypes.DEFAULT_TYPE,
    applicant: dict,
    answers: dict,
    voice_path: Optional[str],
    voice_file_id: Optional[str],
    voice_message_id: Optional[int],
    user_chat_id: Optional[int],
    voice_skipped: bool,
    application_id: Optional[str] = None,
) -> None:
    chat_id = context.application.bot_data.get("group_chat_id")
    if not chat_id:
        return

    def value(key: str) -> str:
        val = answers.get(key)
        if not val:
            return "—"
        # Sanitize HTML to prevent XSS
        return _sanitize_html(str(val))

    voice_status = "✅ <b>Attached below</b>" if voice_file_id else ("⚠️ <b>Skipped</b>" if voice_skipped else "⏳ <b>Pending</b>")
    
    # Format Telegram ID as clickable link
    telegram_username = applicant.get('username')
    telegram_id = applicant.get('telegram_id')
    if telegram_username:
        telegram_link = f"<a href=\"tg://user?id={telegram_id}\">@{telegram_username}</a>"
    else:
        telegram_link = f"<a href=\"tg://user?id={telegram_id}\">User {telegram_id}</a>"
    
    # Redesigned with spacing, separators, and bold formatting
    app_id_line = f"<b>🆔 Application ID:</b> {application_id}\n" if application_id else ""
    message = "\n".join([
        "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━",
        "<b>🚀 NEW CODEXS APPLICATION</b>",
        "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━",
        "",
        app_id_line,
        "<b>👤 Name:</b>",
        f"{value('full_name')}",
        "",
        "<b>📧 Email:</b>",
        f"{value('email')}",
        "",
        "<b>📞 Contact:</b>",
        f"{value('contact')}",
        "",
        "<b>🌍 Location:</b>",
        f"{value('location')}",
        "",
        "<b>💼 Role Focus:</b>",
        f"{value('role_category')}",
        "",
        "<b>🧰 Skills:</b>",
        f"{value('skills')}",
        "",
        "<b>📊 Experience:</b>",
        f"{value('experience')}",
        "",
        "<b>📁 Portfolio:</b>",
        f"{value('portfolio')}",
        "",
        "<b>🧠 Motivation:</b>",
        f"{value('motivation')}",
        "",
        "<b>🗓 Earliest Start:</b>",
        f"{value('start_date')}",
        "",
        "<b>⏱ Preferred Hours:</b>",
        f"{value('working_hours')}",
        "",
        "<b>💰 Salary:</b>",
        f"{value('salary')}",
        "",
        "<b>🎙 Voice Sample:</b>",
        voice_status,
        "",
        "<b>🆔 Telegram:</b>",
        f"{telegram_link} (ID: {telegram_id})",
        "",
        "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━",
    ])

    try:
        await context.bot.send_message(chat_id=chat_id, text=message, parse_mode="HTML")
        logger.info(f"Application summary sent to group {chat_id}")
    except TelegramError as exc:
        logger.error(f"Failed to send application summary to group {chat_id}: {exc}", exc_info=True)
        # Don't fail the application submission - data is already saved
        # Log error but continue with voice forwarding attempt
    
    # Forward the voice message if available (regardless of message send success/failure)
    if voice_message_id and user_chat_id:
        logger.info(f"Attempting to forward voice message {voice_message_id} from chat {user_chat_id} to group {chat_id}")
        try:
            # Forward the original voice message
            await context.bot.forward_message(
                chat_id=chat_id,
                from_chat_id=user_chat_id,
                message_id=voice_message_id
            )
            logger.info(f"Voice message successfully forwarded to group {chat_id}")
            # Add a caption message
            await context.bot.send_message(
                chat_id=chat_id,
                text=f"<b>🎙 English Voice Sample</b>\nFrom: {value('full_name')}",
                parse_mode="HTML"
            )
        except TelegramError as exc:
            logger.error(f"Failed to forward voice message to group: {exc}", exc_info=True)
            # Fallback: try send_voice with file_id
            if voice_file_id:
                try:
                    logger.info(f"Trying fallback: send_voice with file_id {voice_file_id}")
                    await context.bot.send_voice(
                        chat_id=chat_id,
                        voice=voice_file_id,
                        caption=f"🎙 English Voice Sample from {value('full_name')}",
                        parse_mode="HTML"
                    )
                    logger.info(f"Voice file sent via fallback method to group {chat_id}")
                except TelegramError as exc2:
                    logger.error(f"Fallback send_voice also failed: {exc2}", exc_info=True)
                    try:
                        await context.bot.send_message(
                            chat_id=chat_id,
                            text=f"⚠️ Voice file forwarding failed: {str(exc2)[:100]}"
                        )
                    except:
                        pass
    elif voice_file_id:
        # Fallback: use send_voice if we don't have message_id
        logger.info(f"Using fallback: send_voice with file_id {voice_file_id} to group {chat_id}")
        try:
            await context.bot.send_voice(
                chat_id=chat_id,
                voice=voice_file_id,
                caption=f"🎙 English Voice Sample from {value('full_name')}",
                parse_mode="HTML"
            )
            logger.info(f"Voice file sent via file_id to group {chat_id}")
        except TelegramError as exc:
            logger.error(f"Failed to send voice file to group: {exc}", exc_info=True)
    else:
        logger.warning(f"No voice data available for application from {value('full_name')}. Voice skipped: {voice_skipped}")


async def handle_help(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not update.message:
        return
    session = get_session(context.user_data)
    language = session.language or Language.EN
    
    # Context-aware help based on current flow
    if session.waiting_voice:
        help_text = HELP_TEXT_VOICE[language]
    elif session.flow == Flow.APPLY:
        help_text = HELP_TEXT_APPLY[language]
    else:
        help_text = HELP_TEXT[language]
    
    await update.message.reply_text(help_text, parse_mode="HTML")


async def handle_commands(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not update.message:
        return
    session = get_session(context.user_data)
    language = session.language or Language.EN
    await update.message.reply_text(COMMANDS_TEXT[language], parse_mode="HTML")


async def handle_contact_shared(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle when user shares their Telegram contact."""
    if not update.message or not update.message.contact:
        return
    session = get_session(context.user_data)
    if session.flow != Flow.APPLY:
        return
    
    language = session.language or Language.EN
    question = HIRING_QUESTIONS[session.question_index]
    
    if question.input_type != "contact":
        # Not expecting contact at this question
        return
    
    contact = update.message.contact
    
    # Validate contact data
    if not contact.phone_number:
        await update.message.reply_text(
            ERROR_CONTACT_INVALID[language],
            reply_markup=_keyboard_with_back(None, language),
            parse_mode="HTML",
        )
        return
    
    # Format: +1234567890 (Name)
    contact_info = f"+{contact.phone_number}"
    if contact.first_name:
        contact_info += f" ({contact.first_name}"
        if contact.last_name:
            contact_info += f" {contact.last_name}"
        contact_info += ")"
    
    session.answers[question.key] = contact_info
    logger.info(f"Saved contact answer for '{question.key}': '{contact_info}' (Question {session.question_index + 1}/{len(HIRING_QUESTIONS)})")
    await update.message.reply_text(CONTACT_SHARED_ACK[language])
    
    # Move to next question
    session.question_index += 1
    if session.question_index < len(HIRING_QUESTIONS):
        await ask_current_question(update, session)
    else:
        session.mark_voice_wait()
        session.voice_skipped = False
        await update.message.reply_text(
            VOICE_PROMPT[language],
            reply_markup=_keyboard_with_back(None, language),
            parse_mode="HTML",
        )


async def handle_location_shared(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle when user shares their location."""
    if not update.message or not update.message.location:
        return
    session = get_session(context.user_data)
    if session.flow != Flow.APPLY:
        return
    
    language = session.language or Language.EN
    question = HIRING_QUESTIONS[session.question_index]
    
    if question.input_type != "location":
        # Not expecting location at this question
        return
    
    location = update.message.location
    
    # Validate location data
    if location.latitude is None or location.longitude is None:
        await update.message.reply_text(
            ERROR_LOCATION_INVALID[language],
            reply_markup=_keyboard_with_back(None, language),
            parse_mode="HTML",
        )
        return
    
    # Format: Lat 35.6892, Lon 51.3890
    location_info = f"Lat {location.latitude:.4f}, Lon {location.longitude:.4f}"
    
    session.answers[question.key] = location_info
    logger.info(f"Saved location answer for '{question.key}': '{location_info}' (Question {session.question_index + 1}/{len(HIRING_QUESTIONS)})")
    await update.message.reply_text(LOCATION_SHARED_ACK[language])
    
    # Move to next question
    session.question_index += 1
    if session.question_index < len(HIRING_QUESTIONS):
        await ask_current_question(update, session)
    else:
        session.mark_voice_wait()
        session.voice_skipped = False
        await update.message.reply_text(
            VOICE_PROMPT[language],
            reply_markup=_keyboard_with_back(None, language),
            parse_mode="HTML",
        )


def main() -> None:
    logging.basicConfig(
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        level=logging.INFO,
    )
    settings = load_settings()
    storage = DataStorage(settings.applications_file, settings.contact_file)

    application = Application.builder().token(settings.bot_token).build()
    application.bot_data["storage"] = storage
    application.bot_data["settings"] = settings
    application.bot_data["application_notifier"] = WebhookNotifier(
        settings.application_webhook_url,
        settings.application_webhook_token,
        "application",
    )
    application.bot_data["contact_notifier"] = WebhookNotifier(
        settings.contact_webhook_url or settings.application_webhook_url,
        settings.application_webhook_token,
        "contact",
    )
    application.bot_data["group_chat_id"] = settings.group_chat_id
    application.bot_data["ai_responder"] = OpenAIFallback(
        settings.openai_api_key,
        settings.openai_model,
    )

    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("menu", menu_command))
    application.add_handler(CommandHandler("help", handle_help))
    application.add_handler(CommandHandler("commands", handle_commands))
    application.add_handler(MessageHandler(filters.CONTACT, handle_contact_shared))
    application.add_handler(MessageHandler(filters.LOCATION, handle_location_shared))
    application.add_handler(MessageHandler(filters.VOICE | filters.AUDIO, handle_voice))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text))

    logger.info("Codexs Telegram bot started.")
    application.run_polling()


if __name__ == "__main__":
    main()

