from __future__ import annotations

import asyncio
import html
import json
import logging
import re
import time
import uuid
from collections import defaultdict
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Dict, List, Optional

from telegram import KeyboardButton, ReplyKeyboardMarkup, Update
from telegram.constants import ChatType
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
    CONTACT_EDIT_BUTTON,
    CONTACT_INFO,
    CONTACT_MESSAGE_PROMPT,
    CONTACT_MESSAGE_REVIEW,
    CONTACT_SEND_BUTTON,
    CONTACT_SKIP,
    CONTACT_THANKS,
    CONTACT_DECISION_REMINDER,
    CONFIRM_PROMPT,
    CONFIRMATION_IMAGE_CAPTION,
    EDIT_PROMPT,
    ERROR_APPLICATION_SAVE_FAILED,
    ERROR_CONTACT_INVALID,
    ERROR_EMAIL_INVALID,
    ERROR_GENERIC,
    ERROR_GROUP_NOTIFICATION_FAILED,
    ERROR_LOCATION_INVALID,
    ERROR_URL_INVALID,
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
    RESUME_PROMPT,
    RESUME_YES,
    RESUME_NO,
    APPLICATION_HISTORY_HEADER,
    APPLICATION_HISTORY_EMPTY,
    APPLICATION_HISTORY_ITEM,
    APPLICATION_HISTORY_VOICE_RECEIVED,
    APPLICATION_HISTORY_VOICE_SKIPPED,
    ADMIN_ACCESS_DENIED,
    ADMIN_MENU,
    ADMIN_STATUS,
    ADMIN_STATS,
    ADMIN_DEBUG_USER,
    ADMIN_SESSIONS_LIST,
    ADMIN_NO_SESSIONS,
    GROUP_ONLY_COMMAND,
    GROUP_ADMIN_REQUIRED,
    GROUP_HELP_TEXT,
    GROUP_DAILY_REPORT,
    GROUP_STATS_REPORT,
    GROUP_RECENT_APPLICATIONS,
    GROUP_APPLICATION_DETAILS,
    GROUP_APPLICATION_NOT_FOUND,
    GROUP_APPLICATION_ITEM,
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
from .supabase_client import SupabaseBotClient
from .conversation_logger import init_conversation_logger, capture_incoming


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

_QUESTION_KEYWORDS = {
    Language.EN: {"what", "why", "how", "help", "where", "who"},
    Language.FA: {"چی", "چطور", "چرا", "کمک", "کجا", "کی"},
}

_STAGE_LABELS = {
    "new": ("🆕 New", "🆕 درخواست جدید"),
    "review": ("🔍 In review", "🔍 در حال بررسی"),
    "interview": ("📞 Interview", "📞 هماهنگی مصاحبه"),
    "hired": ("✅ Hired", "✅ تایید شده"),
    "rejected": ("⚠️ Closed", "⚠️ بسته شده"),
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


def _looks_like_question(text: str, language: Language) -> bool:
    if "?" in text:
        return True
    normalized = _normalize_for_intent(text)
    for keyword in _QUESTION_KEYWORDS[language]:
        if keyword in normalized:
            return True
    return False


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


def _build_edit_summary(session: UserSession, language: Language) -> str:
    """Build a summary of current answers to help user decide what to edit."""
    lines = ["<b>📋 Current Answers:</b>", ""]
    for idx, question in enumerate(HIRING_QUESTIONS, 1):
        value = session.answers.get(question.key)
        if value is None or (isinstance(value, str) and not value.strip()):
            display = f"<i>(skipped)</i>"
        else:
            sanitized = _sanitize_html(str(value))
            # Show first 50 chars for preview
            if len(sanitized) > 50:
                display = sanitized[:47] + "..."
            else:
                display = sanitized
        lines.append(f"{idx}. <b>{question.summary_labels[language]}:</b> {display}")
    lines.append("\n💡 <i>Select a number to edit, or use 'Back to main menu' to cancel.</i>")
    return "\n".join(lines)


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


async def handle_conversation_logging(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Capture all inbound user messages for Supabase logging."""
    await capture_incoming(update)


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
    
    # Try to load saved session
    saved_session = await _load_session(update, context)
    if saved_session and saved_session.language and saved_session.has_incomplete_application():
        # Restore session and offer resume
        session.language = saved_session.language
        session.flow = saved_session.flow
        session.question_index = saved_session.question_index
        # Validate restored question_index
        if not (0 <= session.question_index < len(HIRING_QUESTIONS)):
            logger.warning(f"Invalid question_index {session.question_index} in saved session. Resetting to 0.")
            session.question_index = 0
        session.answers = saved_session.answers.copy()
        # Validate answers dict - ensure all keys are valid question keys
        valid_keys = {q.key for q in HIRING_QUESTIONS}
        session.answers = {k: v for k, v in session.answers.items() if k in valid_keys}
        session.waiting_voice = saved_session.waiting_voice
        session.voice_file_path = saved_session.voice_file_path
        session.voice_file_id = saved_session.voice_file_id
        session.voice_message_id = saved_session.voice_message_id
        session.voice_skipped = saved_session.voice_skipped
        session.user_chat_id = saved_session.user_chat_id
        session.last_menu_choice = saved_session.last_menu_choice
        session.edit_mode = saved_session.edit_mode
        session.awaiting_edit_selection = saved_session.awaiting_edit_selection
        
        language = session.language
        # Count only non-empty answers
        progress = len([v for v in session.answers.values() if v and str(v).strip()])
        # Store original flow before setting to IDLE for resume prompt detection
        original_flow = session.flow
        session.flow = Flow.IDLE  # Set to IDLE so handle_text can detect resume prompt state
        # Store original flow in a dedicated field for resume logic (not exit_confirmation_flow to avoid conflicts)
        session.resume_original_flow = original_flow
        await _send_landing_card(update, context)
        await update.message.reply_text(
            RESUME_PROMPT[language].format(progress=progress),
            reply_markup=ReplyKeyboardMarkup(
                [[RESUME_YES[language], RESUME_NO[language]]],
                resize_keyboard=True,
            ),
            parse_mode="HTML",
        )
        return
    
    # No saved session or no incomplete application - start fresh
    session.reset_hiring()
    session.language = None
    session.flow = Flow.IDLE
    session.contact_pending = False
    await _send_landing_card(update, context)
    await update.message.reply_text(
        BILINGUAL_WELCOME,
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
    
    # Ensure keyboard is shown immediately after language selection
    main_menu_keyboard = ReplyKeyboardMarkup(
        main_menu_labels(language),
        resize_keyboard=True,
    )
    
    if welcome_banner_path and settings.enable_media:
        try:
            with open(welcome_banner_path, "rb") as banner_file:
                await update.message.reply_photo(
                    photo=banner_file,
                    caption=WELCOME_MESSAGE[language],
                    parse_mode="HTML",
                    reply_markup=main_menu_keyboard,
                )
        except Exception as exc:
            logger.warning(f"Failed to send welcome banner: {exc}")
            # Fallback to text only with keyboard
            await update.message.reply_text(
                WELCOME_MESSAGE[language],
                parse_mode="HTML",
                reply_markup=main_menu_keyboard,
            )
    else:
        await update.message.reply_text(
            WELCOME_MESSAGE[language],
            parse_mode="HTML",
            reply_markup=main_menu_keyboard,
        )


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


def _get_supabase_client(context: ContextTypes.DEFAULT_TYPE) -> Optional[SupabaseBotClient]:
    return context.application.bot_data.get("supabase_client")  # type: ignore[return-value]


def _is_group_chat(update: Update) -> bool:
    """Check if the message is from a group chat."""
    if not update.effective_chat:
        return False
    return update.effective_chat.type in {ChatType.GROUP, ChatType.SUPERGROUP}


async def _is_group_admin(update: Update, context: ContextTypes.DEFAULT_TYPE) -> bool:
    """Check if the user is a group administrator."""
    if not update.effective_chat or not update.effective_user:
        return False
    
    # In private chats, check if user is in ADMIN_USER_IDS
    if update.effective_chat.type == ChatType.PRIVATE:
        settings = _get_settings(context)
        return update.effective_user.id in settings.admin_user_ids
    
    # In group chats, check if user is a group admin
    try:
        member = await update.effective_chat.get_member(update.effective_user.id)
        return member.status in {"administrator", "creator"}
    except Exception:
        # If we can't check, fall back to ADMIN_USER_IDS check
        settings = _get_settings(context)
        return update.effective_user.id in settings.admin_user_ids


async def _save_session(update: Update, context: ContextTypes.DEFAULT_TYPE, session: UserSession) -> None:
    """Save session to disk for persistence."""
    if not update.effective_user:
        return
    storage = _get_storage(context)
    session_data = session.to_dict()
    await storage.save_session(update.effective_user.id, session_data)


async def _load_session(update: Update, context: ContextTypes.DEFAULT_TYPE) -> Optional[UserSession]:
    """Load session from disk if available."""
    if not update.effective_user:
        return None
    storage = _get_storage(context)
    session_data = await storage.load_session(update.effective_user.id)
    if session_data:
        return UserSession.from_dict(session_data)
    return None


def _is_admin(update: Update, context: ContextTypes.DEFAULT_TYPE) -> bool:
    """Check if user is an admin."""
    if not update.effective_user:
        return False
    settings = _get_settings(context)
    user_id = update.effective_user.id
    is_admin = user_id in settings.admin_user_ids
    logger.info(f"Admin check for user {user_id}: {is_admin} (Admin IDs: {settings.admin_user_ids})")
    return is_admin


async def _require_admin(update: Update, context: ContextTypes.DEFAULT_TYPE) -> bool:
    """Check admin access and send error if denied."""
    if not update.effective_user:
        return False
    if not _is_admin(update, context):
        if update.message:
            session = get_session(context.user_data)
            language = session.language or Language.EN
            user_id = update.effective_user.id
            error_msg = ADMIN_ACCESS_DENIED[language]
            # Add user ID for debugging
            error_msg += f"\n\nYour User ID: <code>{user_id}</code>"
            await update.message.reply_text(
                error_msg,
                parse_mode="HTML",
            )
        return False
    return True


def _validate_and_fix_session_state(session: UserSession) -> bool:
    """
    Validate session state consistency and fix invalid states.
    Returns True if state was valid, False if it was fixed.
    """
    fixed = False
    
    # Validate question_index bounds when in APPLY flow
    if session.flow == Flow.APPLY:
        if not (0 <= session.question_index < len(HIRING_QUESTIONS)):
            logger.warning(f"Invalid question_index {session.question_index} in APPLY flow. Resetting.")
            session.question_index = 0
            fixed = True
    
    # Validate waiting_voice state - should only be True in APPLY flow
    if session.waiting_voice and session.flow != Flow.APPLY:
        logger.warning(f"Invalid state: waiting_voice=True but flow={session.flow.name}. Fixing.")
        session.waiting_voice = False
        fixed = True
    
    # Validate contact flow state consistency
    if session.flow == Flow.CONTACT_MESSAGE:
        # If contact_review_pending is True, contact_message_draft should exist
        if session.contact_review_pending and not session.contact_message_draft:
            logger.warning("Invalid state: contact_review_pending=True but no draft. Fixing.")
            session.contact_review_pending = False
            fixed = True
    else:
        # If not in contact flow, clear contact-related flags
        if session.contact_pending or session.contact_review_pending or session.contact_message_draft:
            logger.warning(f"Invalid state: contact flags set but flow={session.flow.name}. Clearing.")
            session.contact_pending = False
            session.contact_review_pending = False
            session.contact_message_draft = None
            fixed = True
    
    # Validate edit_mode - should only be True in APPLY or CONFIRM flow
    if session.edit_mode and session.flow not in (Flow.APPLY, Flow.CONFIRM):
        logger.warning(f"Invalid state: edit_mode=True but flow={session.flow.name}. Fixing.")
        session.edit_mode = False
        fixed = True
    
    # Validate awaiting_edit_selection - should only be True in CONFIRM flow
    if session.awaiting_edit_selection and session.flow != Flow.CONFIRM:
        logger.warning(f"Invalid state: awaiting_edit_selection=True but flow={session.flow.name}. Fixing.")
        session.awaiting_edit_selection = False
        fixed = True
    
    return not fixed  # Return True if valid (not fixed), False if fixed


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
    try:
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
    except Exception as exc:
        logger.warning(f"AI fallback failed: {exc}", exc_info=True)
        # Gracefully degrade - don't show error to user, just return False
        # The caller will show the standard fallback message
        return False


async def _maybe_answer_user_question(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
    session: UserSession,
    user_text: str,
) -> None:
    language = session.language or Language.EN
    if not _looks_like_question(user_text, language):
        return
    await _maybe_ai_reply(update, context, session, user_text)


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
        # Clear any pending flags from other flows to prevent cross-flow leakage
        session.awaiting_view_roles = False
        session.flow = Flow.CONTACT_MESSAGE
        session.contact_pending = True
        session.contact_message_draft = None
        session.contact_review_pending = False
        await _save_session(update, context, session)  # Save session when entering contact flow
        await update.message.reply_text(
            CONTACT_INFO[language],
            reply_markup=ReplyKeyboardMarkup(yes_no_keyboard(language), resize_keyboard=True),
        )
        return

    if key == "history":
        await show_application_history(update, context, session, language)
        return


async def handle_exit_confirmation(update: Update, session: UserSession, text: str, context: Optional[ContextTypes.DEFAULT_TYPE] = None) -> None:
    if not update.message:
        return
    language = session.language or Language.EN
    if is_yes(text, language):
        session.cancel_exit_confirmation()
        # Delete saved session if user confirms exit
        if context and update.effective_user:
            storage = _get_storage(context)
            await storage.delete_session(update.effective_user.id)
        # Clear all relevant flags including contact fields
        session.reset_hiring()
        session.contact_pending = False
        session.contact_message_draft = None
        session.contact_review_pending = False
        session.resume_original_flow = None
        session.awaiting_view_roles = False
        await update.message.reply_text(
            EXIT_CONFIRM_DONE[language],
            reply_markup=ReplyKeyboardMarkup(main_menu_labels(language), resize_keyboard=True),
        )
        return
    if is_no(text, language):
        session.cancel_exit_confirmation()
        await _save_session(update, context, session)
        await update.message.reply_text(EXIT_CONFIRM_CANCEL[language])
        await resume_flow_after_cancel(update, session, context)
        return
    await update.message.reply_text(
        EXIT_CONFIRM_PROMPT[language],
        reply_markup=ReplyKeyboardMarkup(yes_no_keyboard(language), resize_keyboard=True),
    )


async def resume_flow_after_cancel(update: Update, session: UserSession, context: Optional[ContextTypes.DEFAULT_TYPE] = None) -> None:
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
    if session.flow == Flow.CONTACT_MESSAGE:
        if session.contact_review_pending:
            # Resume at review step
            review_keyboard = ReplyKeyboardMarkup(
                [[CONTACT_SEND_BUTTON[language], CONTACT_EDIT_BUTTON[language]]],
                resize_keyboard=True,
            )
            await update.message.reply_text(
                CONTACT_MESSAGE_REVIEW[language].format(message=session.contact_message_draft or ""),
                reply_markup=review_keyboard,
                parse_mode="HTML",
            )
            return
        elif session.contact_pending:
            # Resume at Yes/No prompt
            await update.message.reply_text(
                CONTACT_INFO[language],
                reply_markup=ReplyKeyboardMarkup(yes_no_keyboard(language), resize_keyboard=True),
            )
            return
        else:
            # Resume at message typing
            await update.message.reply_text(
            CONTACT_MESSAGE_PROMPT[language],
            reply_markup=_keyboard_with_back(None, language),
        )


async def handle_text(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not update.message or not update.message.text:
        return
    
    # In group chats, ignore non-command messages
    if _is_group_chat(update):
        # Only process commands in groups, ignore regular chat
        return
    
    # Rate limiting check
    if not update.effective_user:
        return  # Cannot rate limit without user ID
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
        # Save any existing session before resetting (in case user had incomplete work)
        if session.has_incomplete_application() and update.effective_user:
            await _save_session(update, context, session)
        session.reset_hiring()
        session.language = choice
        await _save_session(update, context, session)  # Save new language preference
        await send_language_welcome(update, context, session)
        # Show main menu immediately after welcome to ensure keyboard stays visible
        await show_main_menu(update, session)
        return

    language = session.language

    # Handle resume response (check if we have incomplete application and flow is IDLE - resume prompt state)
    if session.flow == Flow.IDLE and session.has_incomplete_application() and session.resume_original_flow:
        # resume_original_flow stores the original flow during resume prompt
        original_flow = session.resume_original_flow
        
        if text == RESUME_YES[language] or is_yes(text, language):
            # Resume application - restore original flow
            session.resume_original_flow = None  # Clear only after processing
            if session.waiting_voice:
                session.flow = Flow.APPLY
                await update.message.reply_text(
                    VOICE_PROMPT[language],
                    reply_markup=_keyboard_with_back(None, language),
                    parse_mode="HTML",
                )
            elif original_flow == Flow.CONTACT_MESSAGE:
                session.flow = Flow.CONTACT_MESSAGE
                if session.contact_review_pending:
                    review_keyboard = ReplyKeyboardMarkup(
                        [[CONTACT_SEND_BUTTON[language], CONTACT_EDIT_BUTTON[language]]],
                        resize_keyboard=True,
                    )
                    await update.message.reply_text(
                        CONTACT_MESSAGE_REVIEW[language].format(message=session.contact_message_draft or ""),
                        reply_markup=review_keyboard,
                        parse_mode="HTML",
                    )
                elif session.contact_pending:
                    await update.message.reply_text(
                        CONTACT_INFO[language],
                        reply_markup=ReplyKeyboardMarkup(yes_no_keyboard(language), resize_keyboard=True),
                    )
                else:
                    await update.message.reply_text(
                        CONTACT_MESSAGE_PROMPT[language],
                        reply_markup=_keyboard_with_back(None, language),
                    )
            elif original_flow == Flow.CONFIRM:
                # Resume at confirmation stage - check if user was in edit mode
                session.flow = Flow.CONFIRM
                if session.awaiting_edit_selection:
                    # User was selecting which question to edit
                    await update.message.reply_text(
                        EDIT_PROMPT[language],
                        reply_markup=ReplyKeyboardMarkup(edit_keyboard(language), resize_keyboard=True),
                        parse_mode="HTML",
                    )
                elif session.edit_mode:
                    # User was editing a question - should not happen, but handle gracefully
                    await ask_current_question(update, session)
                else:
                    # Normal confirmation state
                    await prompt_confirmation(update, session)
            else:
                session.flow = Flow.APPLY
                await ask_current_question(update, session)
            await _save_session(update, context, session)
            return
        elif text == RESUME_NO[language] or is_no(text, language):
            # Start fresh - delete saved session
            session.resume_original_flow = None  # Clear only after processing
            if update.effective_user:
                storage = _get_storage(context)
                await storage.delete_session(update.effective_user.id)
            session.reset_hiring()
            await show_main_menu(update, session)
            return
        else:
            # Remind user to use buttons - DON'T clear resume_original_flow here!
            # Count only non-empty answers for progress
            progress = len([v for v in session.answers.values() if v and str(v).strip()])
            await update.message.reply_text(
                RESUME_PROMPT[language].format(progress=progress),
                reply_markup=ReplyKeyboardMarkup(
                    [[RESUME_YES[language], RESUME_NO[language]]],
                    resize_keyboard=True,
                ),
                parse_mode="HTML",
            )
            return

    # Handle menu/back commands - check resume prompt state first
    if _is_menu_command(text, language) or _is_back_command(text, language):
        # If in resume prompt state, handle specially
        if session.flow == Flow.IDLE and session.has_incomplete_application() and session.resume_original_flow:
            # User wants to go to menu during resume prompt - clear resume state and go to menu
            session.resume_original_flow = None
            if update.effective_user:
                storage = _get_storage(context)
                await storage.delete_session(update.effective_user.id)
            session.reset_hiring()
            await show_main_menu(update, session)
            return
        # Normal exit confirmation check
        if _needs_exit_confirmation(session):
            await _prompt_exit_confirmation(update, session, language)
        else:
            session.reset_hiring()
            await show_main_menu(update, session)
        return

    if session.exit_confirmation_pending:
        await handle_exit_confirmation(update, session, text, context)
        return

    if is_back_button(text, language):
        # Handle back button in edit mode - return to confirmation
        if session.edit_mode:
            session.edit_mode = False
            session.flow = Flow.CONFIRM
            await _save_session(update, context, session)
            await prompt_confirmation(update, session)
            return
        # Handle back button in awaiting_edit_selection - return to confirmation
        if session.awaiting_edit_selection:
            session.awaiting_edit_selection = False
            session.flow = Flow.CONFIRM
            await _save_session(update, context, session)
            await prompt_confirmation(update, session)
            return
        # Normal back button handling
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
            session.edit_mode = False  # Clear edit mode when re-recording voice
            session.mark_voice_wait()
            session.voice_file_path = None
            session.voice_file_id = None
            session.voice_message_id = None
            session.user_chat_id = None
            session.voice_skipped = False
            await _save_session(update, context, session)
            await update.message.reply_text(
                RERECORD_VOICE_PROMPT[language],
                reply_markup=_keyboard_with_back(None, language),
                parse_mode="HTML",
            )
            return
        
        # Otherwise, edit the selected question
        session.edit_mode = True
        session.question_index = number - 1
        # Double-check bounds after assignment (defensive programming)
        if not (0 <= session.question_index < len(HIRING_QUESTIONS)):
            logger.error(f"Invalid question_index {session.question_index} after edit selection. Resetting.")
            session.question_index = 0
            session.edit_mode = False
            session.flow = Flow.IDLE
            await show_main_menu(update, session)
            return
        question = HIRING_QUESTIONS[session.question_index]
        current_answer = session.answers.get(question.key)
        
        # Show current answer before asking for new one
        if current_answer and str(current_answer).strip():
            current_display = _sanitize_html(str(current_answer))
            if len(current_display) > 100:
                current_display = current_display[:97] + "..."
            preview_msg = f"<b>📝 Current answer:</b> <i>{current_display}</i>\n\n"
        else:
            preview_msg = f"<b>📝 Current answer:</b> <i>(skipped)</i>\n\n"
        
        await _save_session(update, context, session)
        # Send preview first, then ask question
        if update.message:
            await update.message.reply_text(
                preview_msg + "<b>Enter your new answer:</b>",
                parse_mode="HTML",
            )
        await ask_current_question(update, session)
        return

    if session.flow == Flow.APPLY:
        await handle_application_answer(update, context, session, text)
        return

    if session.flow == Flow.CONFIRM:
        if is_yes(text, language):
            await finalize_application(update, context, session)
            return
        if is_no(text, language):
            session.awaiting_edit_selection = True
            await _save_session(update, context, session)
            # Show current answers summary to help user decide what to edit
            edit_summary = _build_edit_summary(session, language)
            await update.message.reply_text(
                edit_summary + "\n\n" + EDIT_PROMPT[language],
                reply_markup=ReplyKeyboardMarkup(edit_keyboard(language), resize_keyboard=True),
                parse_mode="HTML",
            )
            return
        await update.message.reply_text(
            CONFIRM_PROMPT[language],
            reply_markup=ReplyKeyboardMarkup(yes_no_keyboard(language), resize_keyboard=True),
        )
        return

    if session.flow == Flow.CONTACT_MESSAGE:
        # Handle contact review step (Send/Edit buttons)
        if session.contact_review_pending:
            if text == CONTACT_SEND_BUTTON[language]:
                # User confirmed - send the message
                session.contact_review_pending = False
                message_to_send = session.contact_message_draft or ""
                session.contact_message_draft = None
                await save_contact_message(update, context, session, message_to_send)
                return
            elif text == CONTACT_EDIT_BUTTON[language]:
                # User wants to edit - clear review state and allow re-typing
                session.contact_review_pending = False
                session.contact_message_draft = None
                await update.message.reply_text(
                    CONTACT_MESSAGE_PROMPT[language],
                    reply_markup=_keyboard_with_back(None, language),
                )
                return
            else:
                # Remind user to use buttons
                review_keyboard = ReplyKeyboardMarkup(
                    [[CONTACT_SEND_BUTTON[language], CONTACT_EDIT_BUTTON[language]]],
                    resize_keyboard=True,
                )
                await update.message.reply_text(
                    CONTACT_MESSAGE_REVIEW[language].format(message=session.contact_message_draft or ""),
                    reply_markup=review_keyboard,
                    parse_mode="HTML",
                )
                return
        
        # Handle Yes/No decision
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
                session.contact_message_draft = None
                session.contact_review_pending = False
                await update.message.reply_text(
                    CONTACT_SKIP[language],
                    reply_markup=ReplyKeyboardMarkup(main_menu_labels(language), resize_keyboard=True),
                )
                await _save_session(update, context, session)
                return
            else:
                # User sent text instead of Yes/No - show clarification
                await update.message.reply_text(
                    CONTACT_DECISION_REMINDER[language],
                    reply_markup=ReplyKeyboardMarkup(yes_no_keyboard(language), resize_keyboard=True),
                )
                return
        else:
            # User is typing the actual message
            if is_back_button(text, language):
                session.flow = Flow.IDLE
                session.contact_pending = False
                session.contact_message_draft = None
                session.contact_review_pending = False
                await _save_session(update, context, session)
                await show_main_menu(update, session)
                return
            # Validate length first
            if not _validate_text_length(text, max_length=1000):
                await update.message.reply_text(
                    ERROR_TEXT_TOO_LONG[language],
                    reply_markup=_keyboard_with_back(None, language),
                    parse_mode="HTML",
                )
                return
            # Store draft and show review
            session.contact_message_draft = text
            session.contact_review_pending = True
            review_keyboard = ReplyKeyboardMarkup(
                [[CONTACT_SEND_BUTTON[language], CONTACT_EDIT_BUTTON[language]]],
                resize_keyboard=True,
            )
            await update.message.reply_text(
                CONTACT_MESSAGE_REVIEW[language].format(message=text),
                reply_markup=review_keyboard,
                parse_mode="HTML",
            )
            await _save_session(update, context, session)
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
    if matched_key in {"apply", "about", "updates", "contact", "history"}:
        await _open_menu_section(matched_key, update, context, session, language)
        return
    if matched_key == "switch":
        # Save session before language switch to preserve any incomplete work
        if session.has_incomplete_application() and update.effective_user:
            await _save_session(update, context, session)
        # Clear contact flow state when switching language
        if session.flow == Flow.CONTACT_MESSAGE:
            session.flow = Flow.IDLE
            session.contact_pending = False
            session.contact_message_draft = None
            session.contact_review_pending = False
        session.language = switch_language(language)
        await _save_session(update, context, session)  # Save new language preference
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
    news_items = UPDATES.get(language, [])
    displayed_content = False

    for card in cards:
        text = f"<b>{card['title']}</b>\n{card['body']}"
        if card.get("cta_url"):
            text += f"\n{card.get('cta_label', 'Link')}: {card['cta_url']}"
        
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
        displayed_content = True

    if news_items:
        news = "\n".join(news_items).strip()
        if news:
            await update.message.reply_text(
                f"{news}\n\nMore: {UPDATES_LINK}",
                reply_markup=ReplyKeyboardMarkup(main_menu_labels(language), resize_keyboard=True),
            )
            displayed_content = True

    if not displayed_content:
        no_updates_msg = (
            "📢 No updates available at the moment.\n\n"
            "Check back later or visit {link} for the latest news."
            if language == Language.EN
            else "📢 در حال حاضر به‌روزرسانی‌ای موجود نیست.\n\n"
            "بعداً بررسی کنید یا برای آخرین اخبار به {link} سر بزنید."
        )
        await update.message.reply_text(
            no_updates_msg.format(link=UPDATES_LINK),
            reply_markup=ReplyKeyboardMarkup(main_menu_labels(language), resize_keyboard=True),
        )
        return

    await update.message.reply_text(
        f"{UPDATES_CTA[language]} {UPDATES_LINK}",
        reply_markup=ReplyKeyboardMarkup(main_menu_labels(language), resize_keyboard=True),
    )


async def show_application_history(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
    session: UserSession,
    language: Language,
) -> None:
    """Display user's application history."""
    if not update.message or not update.effective_user:
        return
    
    storage = _get_storage(context)
    applications = await storage.get_user_applications(update.effective_user.id)
    
    if not applications:
        await update.message.reply_text(
            APPLICATION_HISTORY_EMPTY[language],
            reply_markup=ReplyKeyboardMarkup(main_menu_labels(language), resize_keyboard=True),
            parse_mode="HTML",
        )
        return
    
    # Send header
    await update.message.reply_text(
        APPLICATION_HISTORY_HEADER[language],
        reply_markup=ReplyKeyboardMarkup(main_menu_labels(language), resize_keyboard=True),
        parse_mode="HTML",
    )
    
    # Send each application (limit to last 10 to avoid message length issues)
    for idx, app in enumerate(applications[:10], 1):
        app_id = app.get("application_id", "N/A")
        submitted_at = app.get("submitted_at", "")
        
        # Parse and format date
        try:
            dt = datetime.fromisoformat(submitted_at.replace("Z", "+00:00"))
            date_str = dt.strftime("%Y-%m-%d %H:%M")
        except Exception:
            date_str = submitted_at
        
        answers = app.get("answers", {})
        name = answers.get("full_name", "—")
        email = answers.get("email", "—")
        
        # Determine voice status
        voice_file_id = app.get("voice_file_id")
        voice_skipped = app.get("voice_skipped", False)
        if voice_file_id:
            voice_status = APPLICATION_HISTORY_VOICE_RECEIVED[language]
        elif voice_skipped or (not voice_file_id and app.get("voice_file_path") is None):
            # If no voice_file_id and no voice_file_path, likely skipped
            voice_status = APPLICATION_HISTORY_VOICE_SKIPPED[language]
        else:
            voice_status = "—"
        
        history_text = APPLICATION_HISTORY_ITEM[language].format(
            number=idx,
            app_id=app_id,
            date=date_str,
            name=_sanitize_html(str(name)),
            email=_sanitize_html(str(email)),
            voice_status=voice_status,
        )
        
        await update.message.reply_text(
            history_text,
            parse_mode="HTML",
        )
    
    if len(applications) > 10:
        await update.message.reply_text(
            f"<i>Showing 10 most recent applications. Total: {len(applications)}</i>" if language == Language.EN
            else f"<i>نمایش ۱۰ درخواست اخیر. مجموع: {len(applications)}</i>",
            parse_mode="HTML",
    )


async def ask_current_question(update: Update, session: UserSession) -> None:
    if not update.message:
        return
    language = session.language or Language.EN
    
    # Validate question_index bounds to prevent IndexError crashes
    if not (0 <= session.question_index < len(HIRING_QUESTIONS)):
        logger.warning(f"Invalid question_index {session.question_index} for user {update.effective_user.id if update.effective_user else 'unknown'}. Resetting to safe state.")
        session.question_index = 0
        session.flow = Flow.IDLE
        await show_main_menu(update, session)
        return
    
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
    
    # Enhanced progress indicator with visual bar
    current_q = session.question_index + 1
    total_q = len(HIRING_QUESTIONS)
    percentage = int((current_q / total_q) * 100)
    # Visual progress bar (10 blocks)
    filled = int((current_q / total_q) * 10)
    progress_bar = "█" * filled + "░" * (10 - filled)
    progress = f"{QUESTION_PROGRESS[language].format(current=current_q, total=total_q)} ({percentage}%)\n{progress_bar}"
    
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


def _validate_phone(phone: str) -> bool:
    """Validate phone number format (with country code)."""
    # Remove common separators and spaces
    cleaned = re.sub(r'[\s\-\(\)\+]', '', phone.strip())
    # Should start with + or digits, and have 7-15 digits total
    pattern = r'^(\+?\d{1,4}[\s\-]?)?\(?\d{1,4}\)?[\s\-]?\d{1,4}[\s\-]?\d{1,9}$'
    if not re.match(pattern, cleaned):
        return False
    # Count digits (should be 7-15)
    digits = re.sub(r'\D', '', cleaned)
    return 7 <= len(digits) <= 15


def _validate_location(location: str) -> bool:
    """Validate location format: City, Country (Timezone) or similar."""
    # Should contain at least a comma or parentheses, indicating structure
    has_comma = ',' in location
    has_parens = '(' in location and ')' in location
    # Should have at least 3 words (city, country, timezone or similar)
    words = location.split()
    return (has_comma or has_parens) and len(words) >= 2 and len(location.strip()) >= 5


def _validate_url(url: str) -> bool:
    """Validate URL format (http/https or common domains)."""
    url = url.strip()
    # Check for common URL patterns
    url_pattern = r'^(https?://)?([\da-z\.-]+)\.([a-z\.]{2,6})([/\w \.-]*)*/?$'
    # Also accept common portfolio platforms without full URL
    common_domains = ['github.com', 'behance.net', 'dribbble.com', 'linkedin.com', 
                      'portfolio', 'github', 'behance', 'dribbble']
    if any(domain in url.lower() for domain in common_domains):
        return True
    return bool(re.match(url_pattern, url, re.IGNORECASE))


def _validate_text_length(text: str, max_length: int = 1000) -> bool:
    """Validate text input length."""
    return len(text.strip()) <= max_length


def _sanitize_html(text: str) -> str:
    """Sanitize HTML by escaping special characters."""
    return html.escape(text, quote=True)


async def _warn_and_repeat_question(
    update: Update,
    session: UserSession,
    question,
    language: Language,
    warning_text: str,
) -> None:
    keyboard_rows = question.keyboard[language] if question.keyboard else None
    await update.message.reply_text(
        warning_text,
        reply_markup=_keyboard_with_back(keyboard_rows, language),
    )
    await ask_current_question(update, session)


async def handle_application_answer(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
    session: UserSession,
    text: str,
) -> None:
    if not update.message:
        return
    language = session.language or Language.EN
    
    # Validate question_index bounds
    if not (0 <= session.question_index < len(HIRING_QUESTIONS)):
        logger.warning(f"Invalid question_index {session.question_index} in handle_application_answer. Resetting.")
        session.question_index = 0
        session.flow = Flow.IDLE
        await show_main_menu(update, session)
        return
    
    question = HIRING_QUESTIONS[session.question_index]
    cleaned = text.strip()
    
    # Handle commands and AI replies BEFORE processing as answer
    if cleaned:
        if _is_menu_command(cleaned, language) or _is_back_command(cleaned, language) or is_back_button(cleaned, language):
            await _prompt_exit_confirmation(update, session, language)
            return
        if _is_repeat_command(cleaned, language):
            await ask_current_question(update, session)
            return
        # Check if this looks like a question - if AI replies, don't process as answer
        if _looks_like_question(cleaned, language):
            # This might be a user question - try AI reply
            ai_replied = await _maybe_ai_reply(update, context, session, cleaned)
            if ai_replied:
                # AI replied, so this was a question - don't process as answer
                return
    
    value: Optional[str] = cleaned or None

    if not cleaned:
        if question.optional:
            value = None
        else:
            await _warn_and_repeat_question(update, session, question, language, MISSING_ANSWER[language])
            return

    if not question.optional and cleaned and is_skip(cleaned, language):
        await _warn_and_repeat_question(update, session, question, language, MISSING_ANSWER[language])
        return

    if cleaned and not _validate_text_length(cleaned, max_length=1000):
        await _warn_and_repeat_question(update, session, question, language, ERROR_TEXT_TOO_LONG[language])
        return
    
    if question.key == "email" and cleaned and not _validate_email(cleaned):
        await _warn_and_repeat_question(update, session, question, language, ERROR_EMAIL_INVALID[language])
        return
    
    # Validate contact (phone number) if typed manually
    if question.key == "contact" and cleaned and question.input_type == "contact":
        # Only validate if it's typed text (not from contact button)
        if not _validate_phone(cleaned):
            await _warn_and_repeat_question(update, session, question, language, ERROR_CONTACT_INVALID[language])
            return

    # Validate location if typed manually
    if question.key == "location" and cleaned and question.input_type == "location":
        # Only validate if it's typed text (not from location button)
        if not _validate_location(cleaned):
            await _warn_and_repeat_question(update, session, question, language, ERROR_LOCATION_INVALID[language])
            return

    # Validate portfolio URL
    if question.key == "portfolio" and cleaned:
        if not _validate_url(cleaned):
            await _warn_and_repeat_question(update, session, question, language, ERROR_URL_INVALID[language])
            return

    if question.optional and cleaned and is_skip(cleaned, language):
        value = None
    # Normalize empty strings to None for optional fields to ensure consistent data storage
    if question.optional and value == "":
        value = None
    
    # Validate that question.key is a valid key (defensive programming)
    valid_keys = {q.key for q in HIRING_QUESTIONS}
    if question.key not in valid_keys:
        logger.error(f"Invalid question key '{question.key}' - this should never happen!")
        await update.message.reply_text(
            ERROR_GENERIC[language],
            reply_markup=ReplyKeyboardMarkup(main_menu_labels(language), resize_keyboard=True),
        )
        return
    
    session.answers[question.key] = value
    logger.info(f"Saved answer for '{question.key}': '{value}' (Question {session.question_index + 1}/{len(HIRING_QUESTIONS)})")
    await _save_session(update, context, session)
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
    
    # Validate and fix session state consistency
    _validate_and_fix_session_state(session)
    
    # Validate voice state - must be waiting for voice AND in APPLY flow
    if not session.waiting_voice or session.language is None or session.flow != Flow.APPLY:
        await update.message.reply_text(
            ERROR_GENERIC[language],
            reply_markup=ReplyKeyboardMarkup(main_menu_labels(language), resize_keyboard=True),
        )
        return

    if not update.effective_user:
        await update.message.reply_text(
            ERROR_GENERIC[language],
            reply_markup=ReplyKeyboardMarkup(main_menu_labels(language), resize_keyboard=True),
        )
        return

    voice_message = update.message.voice
    audio_message = update.message.audio
    telegram_media = voice_message or audio_message
    
    if telegram_media is None:
        await update.message.reply_text(
            ERROR_VOICE_INVALID[language],
            reply_markup=_keyboard_with_back(None, language),
            parse_mode="HTML",
        )
        return

    # Validate file size (max 20MB for Telegram voice messages)
    MAX_VOICE_SIZE = 20 * 1024 * 1024  # 20MB in bytes
    if telegram_media.file_size is not None and telegram_media.file_size > MAX_VOICE_SIZE:
        await update.message.reply_text(
            ERROR_VOICE_TOO_LARGE[language],
            reply_markup=_keyboard_with_back(None, language),
            parse_mode="HTML",
        )
        return

    try:
        file = await telegram_media.get_file()
    except TelegramError as exc:
        logger.error(f"Failed to get voice file: {exc}", exc_info=True)
        await update.message.reply_text(
            ERROR_VOICE_INVALID[language],
            reply_markup=_keyboard_with_back(None, language),
            parse_mode="HTML",
        )
        return
    
    try:
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
    await _save_session(update, context, session)
    await prompt_confirmation(update, session)


async def prompt_confirmation(update: Update, session: UserSession) -> None:
    if not update.message:
        return
    language = session.language or Language.EN
    session.flow = Flow.CONFIRM
    
    def _truncate_text(text: str, max_length: int = 150) -> str:
        """Truncate long text with ellipsis. Increased to 150 for better visibility."""
        if len(text) <= max_length:
            return text
        return text[:max_length - 3] + "..."
    
    def _format_answer_for_summary(value: Optional[str], max_length: int = 150) -> str:
        """Format answer for summary display with better truncation."""
        if value is None or (isinstance(value, str) and not value.strip()):
            return f"<i>{SKIPPED_TEXT[language]}</i>"
        sanitized = _sanitize_html(str(value))
        # Show more characters (150 instead of 80) for better context
        return _truncate_text(sanitized, max_length=max_length)
    
    summary_lines = [f"<b>{SUMMARY_HEADER[language]}</b>", ""]
    for question in HIRING_QUESTIONS:
        value = session.answers.get(question.key)
        display = _format_answer_for_summary(value)
        summary_lines.append(f"<b>{question.summary_labels[language]}:</b> {display}")
    
    summary_lines.append("")  # Add spacing before voice status
    if session.voice_file_path:
        voice_status = VOICE_STATUS_RECEIVED[language]
    elif session.voice_skipped:
        voice_status = VOICE_STATUS_SKIPPED[language]
    else:
        voice_status = VOICE_STATUS_PENDING[language]
    summary_lines.append(VOICE_STATUS_LINE[language].format(status=voice_status))
    summary_lines.append("")  # Add spacing before confirmation prompt
    summary_lines.append(CONFIRM_PROMPT[language])
    
    await update.message.reply_text(
        "\n".join(summary_lines),
        reply_markup=ReplyKeyboardMarkup(yes_no_keyboard(language), resize_keyboard=True),
        parse_mode="HTML",
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
    try:
        await storage.save_application(
            applicant=applicant,
            answers=session.answers,
            language=language,
            voice_file_path=session.voice_file_path,
            voice_file_id=session.voice_file_id,
            application_id=application_id,
            voice_skipped=session.voice_skipped,
        )
    except Exception as exc:
        # CRITICAL: If save fails, don't clear session and inform user
        logger.error(f"CRITICAL: Failed to save application {application_id}: {exc}", exc_info=True)
        await update.message.reply_text(
            ERROR_APPLICATION_SAVE_FAILED[language].format(app_id=application_id),
            parse_mode="HTML",
            reply_markup=ReplyKeyboardMarkup(main_menu_labels(language), resize_keyboard=True),
        )
        # Don't clear session - user can try again
        return
    
    voice_file_url: Optional[str] = None
    if session.voice_file_id:
        try:
            telegram_file = await context.bot.get_file(session.voice_file_id)
            voice_file_url = telegram_file.file_path
        except TelegramError as exc:
            logger.warning("Unable to fetch Telegram voice file URL: %s", exc)
    
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
             "voice_file_url": voice_file_url,
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
    
    # Delete saved session since application is complete
    if update.effective_user:
        storage = _get_storage(context)
        await storage.delete_session(update.effective_user.id)
    
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
    await _save_session(update, context, session)


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
        logger.warning(f"GROUP_CHAT_ID not configured. Application {application_id} saved but not sent to group.")
        return
    
    logger.info(f"Attempting to send application {application_id} to group chat {chat_id}")

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
        logger.info(f"✅ Application summary sent to group {chat_id} for application {application_id}")
    except TelegramError as exc:
        logger.error(f"❌ Failed to send application summary to group {chat_id}: {exc}", exc_info=True)
        logger.error(f"Application {application_id} was saved but group notification failed!")
        # Don't fail the application submission - data is already saved
        # Log error but continue with voice forwarding attempt
    except Exception as exc:
        logger.error(f"❌ Unexpected error sending application to group: {exc}", exc_info=True)
    
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
    await _save_session(update, context, session)
    await update.message.reply_text(CONTACT_SHARED_ACK[language])
    
    # If in edit mode, go to confirmation instead of next question
    if session.edit_mode:
        session.edit_mode = False
        session.flow = Flow.CONFIRM
        await _save_session(update, context, session)
        await prompt_confirmation(update, session)
        return
    
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
    
    # Validate and fix session state consistency
    _validate_and_fix_session_state(session)
    
    if session.flow != Flow.APPLY:
        return
    
    language = session.language or Language.EN
    
    # Validate question_index bounds
    if not (0 <= session.question_index < len(HIRING_QUESTIONS)):
        logger.warning(f"Invalid question_index {session.question_index} in location handler. Resetting.")
        session.question_index = 0
        session.flow = Flow.IDLE
        await show_main_menu(update, session)
        return
    
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
    await _save_session(update, context, session)
    await update.message.reply_text(LOCATION_SHARED_ACK[language])
    
    # If in edit mode, go to confirmation instead of next question
    if session.edit_mode:
        session.edit_mode = False
        session.flow = Flow.CONFIRM
        await _save_session(update, context, session)
        await prompt_confirmation(update, session)
        return
    
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


async def handle_test_admin(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Test command to verify handlers work."""
    if update.message:
        await update.message.reply_text("✅ Command handler is working!")


async def handle_admin(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Admin panel menu."""
    try:
        if not update.message or not update.effective_user:
            logger.warning("Admin command: missing message or user")
            return
        
        user_id = update.effective_user.id
        logger.info(f"Admin command received from user {user_id}")
        
        # Always show debug info first to help troubleshoot
        try:
            settings = _get_settings(context)
            admin_ids = settings.admin_user_ids
            is_admin = user_id in admin_ids
        except Exception as e:
            logger.error(f"Error getting settings: {e}", exc_info=True)
            await update.message.reply_text(
                f"❌ Error checking admin status: {str(e)}",
                parse_mode="HTML",
            )
            return
        
        if not is_admin:
            debug_msg = (
                f"🔍 <b>Debug Info</b>\n\n"
                f"Your User ID: <code>{user_id}</code>\n"
                f"Configured Admin IDs: <code>{admin_ids}</code>\n"
                f"Admin Check: ❌ Failed\n\n"
                f"{ADMIN_ACCESS_DENIED[Language.EN]}"
            )
            await update.message.reply_text(debug_msg, parse_mode="HTML")
            return
        
        session = get_session(context.user_data)
        language = session.language or Language.EN
        await update.message.reply_text(
            ADMIN_MENU[language],
            parse_mode="HTML",
        )
    except Exception as e:
        logger.error(f"Error in handle_admin: {e}", exc_info=True)
        if update.message:
            await update.message.reply_text(
                f"❌ Error: {str(e)}\n\nPlease check bot logs.",
                parse_mode="HTML",
            )


async def handle_user_status(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Allow applicants to check their Supabase status via /status."""
    if not update.message or not update.effective_user:
        return
    supabase_client = _get_supabase_client(context)
    session = get_session(context.user_data)
    language = session.language or Language.EN

    if not supabase_client or not supabase_client.enabled:
        await update.message.reply_text(
            "📡 Status tracking isn't enabled yet. Please try again later."
            if language == Language.EN
            else "📡 پیگیری وضعیت هنوز فعال نشده است. لطفاً بعداً دوباره امتحان کنید.",
            parse_mode="HTML",
        )
        return

    status_payload = await supabase_client.fetch_applicant_status(update.effective_user.id)
    if not status_payload or status_payload.get("status") in {None, "unknown"}:
        await update.message.reply_text(
            "I couldn't find an application linked to this Telegram account. "
            "Submit a new application from the main menu."
            if language == Language.EN
            else "درخواستی مرتبط با این حساب تلگرام پیدا نشد. از منوی اصلی می‌توانید درخواست جدید ارسال کنید.",
            parse_mode="HTML",
        )
        return

    stage_key = status_payload.get("status", "review")
    stage_label_en, stage_label_fa = _STAGE_LABELS.get(stage_key, ("⏳ In review", "⏳ در حال بررسی"))
    stage_label = stage_label_en if language == Language.EN else stage_label_fa
    submitted_at = status_payload.get("submitted_at")
    earliest_start = status_payload.get("earliest_start")
    working_hours = status_payload.get("working_hours")

    lines = [
        "📊 <b>Application Status</b>" if language == Language.EN else "📊 <b>وضعیت درخواست</b>",
        "",
        f"{'Status' if language == Language.EN else 'وضعیت'}: {stage_label}",
    ]
    if submitted_at:
        lines.append(
            f"{'Submitted' if language == Language.EN else 'ارسال شده'}: {submitted_at}"
        )
    if earliest_start:
        lines.append(
            f"{'Earliest start' if language == Language.EN else 'شروع پیشنهادی'}: {earliest_start}"
        )
    if working_hours:
        lines.append(
            f"{'Preferred hours' if language == Language.EN else 'ساعات ترجیحی'}: {working_hours}"
        )
    lines.append("")
    lines.append(
        "We'll reach out inside Telegram once the next step is ready."
        if language == Language.EN
        else "به محض آماده شدن مرحله بعدی از طریق تلگرام با شما تماس می‌گیریم."
    )

    await update.message.reply_text("\n".join(lines), parse_mode="HTML")


async def handle_admin_status(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Show bot status."""
    if not await _require_admin(update, context) or not update.message:
        return
    session = get_session(context.user_data)
    language = session.language or Language.EN
    storage = _get_storage(context)
    settings = _get_settings(context)
    
    # Count applications
    app_count = 0
    if settings.applications_file.exists():
        with settings.applications_file.open("r", encoding="utf-8") as f:
            app_count = sum(1 for line in f if line.strip())
    
    # Count contact messages
    contact_count = 0
    if settings.contact_file.exists():
        with settings.contact_file.open("r", encoding="utf-8") as f:
            contact_count = sum(1 for line in f if line.strip())
    
    # Count active sessions
    session_count = 0
    if settings.sessions_dir.exists():
        session_count = len(list(settings.sessions_dir.glob("session_*.json")))
    
    # Count voice samples
    voice_count = 0
    if settings.voice_dir.exists():
        voice_count = len(list(settings.voice_dir.glob("*")))
    
    timestamp = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")
    
    await update.message.reply_text(
        ADMIN_STATUS[language].format(
            app_count=app_count,
            contact_count=contact_count,
            session_count=session_count,
            voice_count=voice_count,
            timestamp=timestamp,
        ),
        parse_mode="HTML",
    )


async def handle_admin_stats(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Show detailed statistics."""
    if not await _require_admin(update, context) or not update.message:
        return
    session = get_session(context.user_data)
    language = session.language or Language.EN
    storage = _get_storage(context)
    settings = _get_settings(context)
    
    # Read all applications
    total_apps = 0
    completed_apps = 0
    incomplete_apps = 0
    en_count = 0
    fa_count = 0
    unique_users = set()
    
    if settings.applications_file.exists():
        with settings.applications_file.open("r", encoding="utf-8") as f:
            for line in f:
                if not line.strip():
                    continue
                try:
                    app = json.loads(line)
                    total_apps += 1
                    unique_users.add(app.get("applicant", {}).get("telegram_id"))
                    
                    # Check if completed (has application_id)
                    if app.get("application_id"):
                        completed_apps += 1
                    else:
                        incomplete_apps += 1
                    
                    # Count languages
                    app_lang = app.get("language", "en")
                    if app_lang == "en":
                        en_count += 1
                    elif app_lang == "fa":
                        fa_count += 1
                except json.JSONDecodeError:
                    continue
    
    # Count contact messages
    contact_count = 0
    if settings.contact_file.exists():
        with settings.contact_file.open("r", encoding="utf-8") as f:
            contact_count = sum(1 for line in f if line.strip())
    
    await update.message.reply_text(
        ADMIN_STATS[language].format(
            total_apps=total_apps,
            completed_apps=completed_apps,
            incomplete_apps=incomplete_apps,
            contact_count=contact_count,
            unique_users=len(unique_users),
            en_count=en_count,
            fa_count=fa_count,
        ),
        parse_mode="HTML",
    )


async def handle_admin_debug(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Debug a specific user's session."""
    if not await _require_admin(update, context) or not update.message:
        return
    session = get_session(context.user_data)
    language = session.language or Language.EN
    
    if not context.args or len(context.args) == 0:
        await update.message.reply_text(
            "Usage: /debug &lt;user_id&gt;" if language == Language.EN
            else "استفاده: /debug &lt;user_id&gt;",
            parse_mode="HTML",
        )
        return
    
    try:
        user_id = int(context.args[0])
    except ValueError:
        await update.message.reply_text(
            "Invalid user ID. Use: /debug &lt;user_id&gt;" if language == Language.EN
            else "شناسه کاربر نامعتبر. استفاده: /debug &lt;user_id&gt;",
            parse_mode="HTML",
        )
        return
    
    storage = _get_storage(context)
    
    # Load user session
    session_data = await storage.load_session(user_id)
    user_session = None
    if session_data:
        user_session = UserSession.from_dict(session_data)
    
    # Get user applications
    user_apps = await storage.get_user_applications(user_id)
    
    # Try to get user info from bot (if possible)
    try:
        bot = context.bot
        user = await bot.get_chat(user_id)
        username = user.username or "N/A"
        name = f"{user.first_name or ''} {user.last_name or ''}".strip() or "N/A"
    except Exception:
        username = "N/A"
        name = "N/A"
    
    # Format session info
    if user_session:
        session_lang = user_session.language.value if user_session.language else "N/A"
        session_flow = user_session.flow.name if user_session.flow else "N/A"
        question_idx = user_session.question_index
        answer_count = len([v for v in user_session.answers.values() if v])
        waiting_voice = "Yes" if user_session.waiting_voice else "No"
        voice_skipped = "Yes" if user_session.voice_skipped else "No"
        edit_mode = "Yes" if user_session.edit_mode else "No"
    else:
        session_lang = "N/A"
        session_flow = "N/A"
        question_idx = 0
        answer_count = 0
        waiting_voice = "No"
        voice_skipped = "No"
        edit_mode = "No"
    
    await update.message.reply_text(
        ADMIN_DEBUG_USER[language].format(
            user_id=user_id,
            username=username,
            name=name,
            language=session_lang,
            flow=session_flow,
            question_index=question_idx,
            answer_count=answer_count,
            waiting_voice=waiting_voice,
            voice_skipped=voice_skipped,
            edit_mode=edit_mode,
            app_count=len(user_apps),
        ),
        parse_mode="HTML",
    )


async def handle_admin_test_group(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Test sending a message to the group."""
    if not await _require_admin(update, context) or not update.message:
        return
    
    chat_id = context.application.bot_data.get("group_chat_id")
    if not chat_id:
        await update.message.reply_text(
            "❌ GROUP_CHAT_ID not configured in settings.",
            parse_mode="HTML",
        )
        return
    
    try:
        test_message = (
            "🧪 <b>Test Message from Admin</b>\n\n"
            f"Group Chat ID: <code>{chat_id}</code>\n"
            "If you see this, group notifications are working!"
        )
        await context.bot.send_message(
            chat_id=chat_id,
            text=test_message,
            parse_mode="HTML",
        )
        await update.message.reply_text(
            f"✅ Test message sent to group {chat_id}",
            parse_mode="HTML",
        )
    except TelegramError as exc:
        error_msg = (
            f"❌ Failed to send test message to group {chat_id}\n\n"
            f"Error: {str(exc)}\n\n"
            "Possible issues:\n"
            "• Bot is not a member of the group\n"
            "• Bot doesn't have permission to send messages\n"
            "• GROUP_CHAT_ID is incorrect"
        )
        await update.message.reply_text(error_msg, parse_mode="HTML")
        logger.error(f"Failed to send test message to group: {exc}", exc_info=True)


async def handle_group_help(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Show group commands help."""
    if not update.message:
        return
    
    # Check if user is group admin
    if not await _is_group_admin(update, context):
        # Try to get language from session or default to EN
        session = get_session(context.user_data)
        language = session.language or Language.EN
        await update.message.reply_text(
            GROUP_ADMIN_REQUIRED[language],
            parse_mode="HTML",
        )
        return
    
    session = get_session(context.user_data)
    language = session.language or Language.EN
    await update.message.reply_text(
        GROUP_HELP_TEXT[language],
        parse_mode="HTML",
    )


async def handle_group_daily_report(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Generate and send daily report."""
    if not update.message:
        return
    
    # Check if user is group admin
    if not await _is_group_admin(update, context):
        session = get_session(context.user_data)
        language = session.language or Language.EN
        await update.message.reply_text(
            GROUP_ADMIN_REQUIRED[language],
            parse_mode="HTML",
        )
        return
    
    session = get_session(context.user_data)
    language = session.language or Language.EN
    storage = _get_storage(context)
    
    now = datetime.now(timezone.utc)
    today_start = datetime(now.year, now.month, now.day, tzinfo=timezone.utc)
    week_start = now - timedelta(days=7)
    month_start = now - timedelta(days=30)
    
    # Get applications
    today_apps = await storage.get_applications_by_date_range(today_start, now)
    week_apps = await storage.get_applications_by_date_range(week_start, now)
    month_apps = await storage.get_applications_by_date_range(month_start, now)
    
    # Get contact messages
    today_contacts = await storage.get_contact_messages_by_date_range(today_start, now)
    week_contacts = await storage.get_contact_messages_by_date_range(week_start, now)
    month_contacts = await storage.get_contact_messages_by_date_range(month_start, now)
    
    # Count voice samples
    today_voices = sum(1 for app in today_apps if app.get("voice_file_path") or app.get("voice_file_id"))
    today_skipped = sum(1 for app in today_apps if app.get("voice_skipped", False))
    
    # Language breakdown
    en_count = sum(1 for app in today_apps if app.get("language") == "en")
    fa_count = sum(1 for app in today_apps if app.get("language") == "fa")
    
    # Recent applications list (last 5)
    recent_apps = today_apps[:5]
    recent_list = ""
    if recent_apps:
        recent_items = []
        for app in recent_apps:
            applicant = app.get("applicant", {})
            name = applicant.get("first_name", "") + " " + applicant.get("last_name", "")
            name = name.strip() or "Unknown"
            answers = app.get("answers", {})
            email = answers.get("email", applicant.get("username", "N/A"))
            app_id = app.get("application_id", "N/A")
            app_lang = "EN" if app.get("language") == "en" else "FA"
            voice_status = "✅ Voice" if (app.get("voice_file_path") or app.get("voice_file_id")) else "⏭️ Skipped"
            submitted_at = app.get("submitted_at", "")
            try:
                dt = datetime.fromisoformat(submitted_at.replace("Z", "+00:00"))
                date_str = dt.strftime("%H:%M")
            except:
                date_str = "N/A"
            recent_items.append(
                GROUP_APPLICATION_ITEM[language].format(
                    name=name,
                    email=email,
                    application_id=app_id,
                    date=date_str,
                    language=app_lang,
                    voice_status=voice_status,
                )
            )
        recent_list = "\n".join(recent_items)
    else:
        recent_list = "No applications today." if language == Language.EN else "هیچ درخواستی امروز نیست."
    
    date_str = now.strftime("%Y-%m-%d")
    
    await update.message.reply_text(
        GROUP_DAILY_REPORT[language].format(
            date=date_str,
            today_apps=len(today_apps),
            today_contacts=len(today_contacts),
            today_voices=today_voices,
            today_skipped=today_skipped,
            en_count=en_count,
            fa_count=fa_count,
            week_apps=len(week_apps),
            week_contacts=len(week_contacts),
            month_apps=len(month_apps),
            month_contacts=len(month_contacts),
            recent_list=recent_list,
        ),
        parse_mode="HTML",
    )


async def handle_group_stats(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Generate and send detailed statistics."""
    if not update.message:
        return
    
    # Check if user is group admin
    if not await _is_group_admin(update, context):
        session = get_session(context.user_data)
        language = session.language or Language.EN
        await update.message.reply_text(
            GROUP_ADMIN_REQUIRED[language],
            parse_mode="HTML",
        )
        return
    
    session = get_session(context.user_data)
    language = session.language or Language.EN
    storage = _get_storage(context)
    
    now = datetime.now(timezone.utc)
    today_start = datetime(now.year, now.month, now.day, tzinfo=timezone.utc)
    week_start = now - timedelta(days=7)
    month_start = now - timedelta(days=30)
    
    # Get all applications
    all_apps = await storage.get_all_applications()
    today_apps = await storage.get_applications_by_date_range(today_start, now)
    week_apps = await storage.get_applications_by_date_range(week_start, now)
    month_apps = await storage.get_applications_by_date_range(month_start, now)
    
    # Get all contact messages
    all_contacts = await storage.get_all_contact_messages()
    
    # Count unique users
    unique_users = set()
    for app in all_apps:
        applicant = app.get("applicant", {})
        user_id = applicant.get("telegram_id")
        if user_id:
            unique_users.add(user_id)
    
    # Voice samples
    total_voices = sum(1 for app in all_apps if app.get("voice_file_path") or app.get("voice_file_id"))
    total_skipped = sum(1 for app in all_apps if app.get("voice_skipped", False))
    
    # Language breakdown
    en_count = sum(1 for app in all_apps if app.get("language") == "en")
    fa_count = sum(1 for app in all_apps if app.get("language") == "fa")
    total_lang = en_count + fa_count
    en_percent = round((en_count / total_lang * 100) if total_lang > 0 else 0, 1)
    fa_percent = round((fa_count / total_lang * 100) if total_lang > 0 else 0, 1)
    
    await update.message.reply_text(
        GROUP_STATS_REPORT[language].format(
            total_apps=len(all_apps),
            total_contacts=len(all_contacts),
            unique_users=len(unique_users),
            total_voices=total_voices,
            total_skipped=total_skipped,
            en_count=en_count,
            en_percent=en_percent,
            fa_count=fa_count,
            fa_percent=fa_percent,
            today_apps=len(today_apps),
            week_apps=len(week_apps),
            month_apps=len(month_apps),
        ),
        parse_mode="HTML",
    )


async def handle_group_recent(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """List recent applications."""
    if not update.message:
        return
    
    # Check if user is group admin
    if not await _is_group_admin(update, context):
        session = get_session(context.user_data)
        language = session.language or Language.EN
        await update.message.reply_text(
            GROUP_ADMIN_REQUIRED[language],
            parse_mode="HTML",
        )
        return
    
    session = get_session(context.user_data)
    language = session.language or Language.EN
    storage = _get_storage(context)
    
    # Get recent applications (last 10)
    recent_apps = await storage.get_recent_applications(limit=10)
    all_apps = await storage.get_all_applications()
    
    if not recent_apps:
        await update.message.reply_text(
            "No applications found." if language == Language.EN else "هیچ درخواستی یافت نشد.",
            parse_mode="HTML",
        )
        return
    
    # Format applications list
    app_items = []
    for app in recent_apps:
        applicant = app.get("applicant", {})
        name = applicant.get("first_name", "") + " " + applicant.get("last_name", "")
        name = name.strip() or "Unknown"
        answers = app.get("answers", {})
        email = answers.get("email", applicant.get("username", "N/A"))
        app_id = app.get("application_id", "N/A")
        app_lang = "EN" if app.get("language") == "en" else "FA"
        voice_status = "✅ Voice" if (app.get("voice_file_path") or app.get("voice_file_id")) else "⏭️ Skipped"
        submitted_at = app.get("submitted_at", "")
        try:
            dt = datetime.fromisoformat(submitted_at.replace("Z", "+00:00"))
            date_str = dt.strftime("%Y-%m-%d %H:%M")
        except:
            date_str = "N/A"
        app_items.append(
            GROUP_APPLICATION_ITEM[language].format(
                name=name,
                email=email,
                application_id=app_id,
                date=date_str,
                language=app_lang,
                voice_status=voice_status,
            )
        )
    
    await update.message.reply_text(
        GROUP_RECENT_APPLICATIONS[language].format(
            applications_list="\n".join(app_items),
            count=len(recent_apps),
            total=len(all_apps),
        ),
        parse_mode="HTML",
    )


async def handle_group_app_details(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Show details of a specific application."""
    if not update.message:
        return
    
    # Check if user is group admin
    if not await _is_group_admin(update, context):
        session = get_session(context.user_data)
        language = session.language or Language.EN
        await update.message.reply_text(
            GROUP_ADMIN_REQUIRED[language],
            parse_mode="HTML",
        )
        return
    
    session = get_session(context.user_data)
    language = session.language or Language.EN
    storage = _get_storage(context)
    
    # Get application ID from command arguments
    text = update.message.text or ""
    parts = text.split()
    if len(parts) < 2:
        await update.message.reply_text(
            "Usage: /app <application_id>" if language == Language.EN else "استفاده: /app <application_id>",
            parse_mode="HTML",
        )
        return
    
    application_id = parts[1]
    app = await storage.get_application_by_id(application_id)
    
    if not app:
        await update.message.reply_text(
            GROUP_APPLICATION_NOT_FOUND[language],
            parse_mode="HTML",
        )
        return
    
    # Format application details
    applicant = app.get("applicant", {})
    name = applicant.get("first_name", "") + " " + applicant.get("last_name", "")
    name = name.strip() or "Unknown"
    telegram_id = applicant.get("telegram_id", "N/A")
    username = applicant.get("username", "N/A") or "N/A"
    
    answers = app.get("answers", {})
    email = answers.get("email", "N/A")
    contact = answers.get("contact", "N/A")
    location = answers.get("location", "N/A")
    portfolio = answers.get("portfolio", "N/A")
    
    # Format answers
    answer_lines = []
    for key, value in answers.items():
        if value:
            answer_lines.append(f"• {key}: {value}")
    answers_text = "\n".join(answer_lines) if answer_lines else "No answers provided."
    
    # Voice status
    if app.get("voice_file_path") or app.get("voice_file_id"):
        voice_status = "✅ Voice sample received"
    elif app.get("voice_skipped", False):
        voice_status = "⏭️ Voice sample skipped"
    else:
        voice_status = "❌ No voice sample"
    
    # Format date
    submitted_at = app.get("submitted_at", "")
    try:
        dt = datetime.fromisoformat(submitted_at.replace("Z", "+00:00"))
        date_str = dt.strftime("%Y-%m-%d %H:%M UTC")
    except:
        date_str = submitted_at
    
    app_lang = "English" if app.get("language") == "en" else "Farsi"
    
    await update.message.reply_text(
        GROUP_APPLICATION_DETAILS[language].format(
            application_id=app.get("application_id", "N/A"),
            submitted_at=date_str,
            language=app_lang,
            name=name,
            email=email,
            contact=contact,
            location=location,
            portfolio=portfolio,
            username=username,
            telegram_id=telegram_id,
            answers=answers_text,
            voice_status=voice_status,
        ),
        parse_mode="HTML",
    )


async def handle_admin_cleanup(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Clean up old session files."""
    if not await _require_admin(update, context) or not update.message:
        return
    session = get_session(context.user_data)
    language = session.language or Language.EN
    storage = _get_storage(context)
    
    try:
        deleted_count = await storage.cleanup_old_sessions(days_old=30)
        await update.message.reply_text(
            f"✅ <b>Cleanup Complete</b>\n\nDeleted {deleted_count} old session files (older than 30 days).",
            parse_mode="HTML",
        )
        logger.info(f"Admin cleanup: {deleted_count} sessions deleted")
    except Exception as exc:
        logger.error(f"Failed to cleanup sessions: {exc}", exc_info=True)
        await update.message.reply_text(
            f"❌ <b>Cleanup Failed</b>\n\nError: {str(exc)[:100]}",
            parse_mode="HTML",
        )


async def handle_admin_reload_config(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Force-refresh remote question/content config from Supabase."""
    if not await _require_admin(update, context) or not update.message:
        return
    supabase_client = _get_supabase_client(context)
    session = get_session(context.user_data)
    language = session.language or Language.EN

    if not supabase_client or not supabase_client.enabled:
        await update.message.reply_text(
            "Supabase integration is not configured." if language == Language.EN else "اتصال Supabase پیکربندی نشده است.",
            parse_mode="HTML",
        )
        return

    await update.message.reply_text(
        "Refreshing remote configuration…" if language == Language.EN else "در حال به‌روزرسانی تنظیمات…",
        parse_mode="HTML",
    )

    success = await supabase_client.refresh_remote_content()
    if success:
        await update.message.reply_text(
            "✅ Remote questions and content updated."
            if language == Language.EN
            else "✅ سوالات و محتوا با موفقیت به‌روزرسانی شد.",
            parse_mode="HTML",
        )
    else:
        await update.message.reply_text(
            "⚠️ Failed to fetch config. Check logs."
            if language == Language.EN
            else "⚠️ دریافت تنظیمات با خطا مواجه شد. لاگ‌ها را بررسی کنید.",
            parse_mode="HTML",
        )


async def handle_admin_sessions(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """List all active sessions."""
    if not await _require_admin(update, context) or not update.message:
        return
    session = get_session(context.user_data)
    language = session.language or Language.EN
    settings = _get_settings(context)
    storage = _get_storage(context)
    
    # Get all session files
    session_files = list(settings.sessions_dir.glob("session_*.json"))
    
    if not session_files:
        await update.message.reply_text(
            ADMIN_NO_SESSIONS[language],
            parse_mode="HTML",
        )
        return
    
    sessions_list = []
    for session_file in session_files[:20]:  # Limit to 20 sessions
        try:
            user_id = int(session_file.stem.split("_")[1])
            session_data = await storage.load_session(user_id)
            if session_data:
                user_session = UserSession.from_dict(session_data)
                if user_session.has_incomplete_application():
                    progress = len([v for v in user_session.answers.values() if v])
                    lang = user_session.language.value if user_session.language else "N/A"
                    sessions_list.append(f"• User {user_id}: {progress} answers, {lang}")
        except Exception:
            continue
    
    if not sessions_list:
        await update.message.reply_text(
            ADMIN_NO_SESSIONS[language],
            parse_mode="HTML",
        )
        return
    
    sessions_text = "\n".join(sessions_list)
    if len(session_files) > 20:
        sessions_text += f"\n\n... and {len(session_files) - 20} more"
    
    await update.message.reply_text(
        ADMIN_SESSIONS_LIST[language].format(
            count=len(session_files),
            sessions_list=sessions_text,
        ),
            parse_mode="HTML",
        )


def main() -> None:
    logging.basicConfig(
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        level=logging.INFO,
    )
    settings = load_settings()
    storage = DataStorage(settings.applications_file, settings.contact_file, settings.sessions_dir)

    supabase_client = SupabaseBotClient(settings)
    if supabase_client.enabled:
        try:
            asyncio.run(supabase_client.refresh_remote_content())
        except Exception as exc:  # pylint: disable=broad-except
            logger.warning("Failed to bootstrap remote config: %s", exc)

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
    application.bot_data["supabase_client"] = supabase_client
    init_conversation_logger(supabase_client if supabase_client.enabled else None)

    # Log every incoming update (group -1 ensures it's first)
    application.add_handler(MessageHandler(filters.ALL, handle_conversation_logging), group=-1)
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("menu", menu_command))
    application.add_handler(CommandHandler("help", handle_help))
    application.add_handler(CommandHandler("commands", handle_commands))
    application.add_handler(CommandHandler("status", handle_user_status))
    application.add_handler(CommandHandler("botstatus", handle_admin_status))
    application.add_handler(CommandHandler("adminstatus", handle_admin_status))
    # Admin commands
    application.add_handler(CommandHandler("testadmin", handle_test_admin))
    application.add_handler(CommandHandler("admin", handle_admin))
    application.add_handler(CommandHandler("stats", handle_admin_stats))
    application.add_handler(CommandHandler("debug", handle_admin_debug))
    application.add_handler(CommandHandler("sessions", handle_admin_sessions))
    application.add_handler(CommandHandler("cleanup", handle_admin_cleanup))
    application.add_handler(CommandHandler("reloadconfig", handle_admin_reload_config))
    application.add_handler(CommandHandler("testgroup", handle_admin_test_group))
    # Group commands (work in both private and group chats, but require admin in groups)
    application.add_handler(CommandHandler("daily", handle_group_daily_report))
    application.add_handler(CommandHandler("report", handle_group_daily_report))
    application.add_handler(CommandHandler("gstats", handle_group_stats))
    application.add_handler(CommandHandler("recent", handle_group_recent))
    application.add_handler(CommandHandler("app", handle_group_app_details))
    application.add_handler(CommandHandler("ghelp", handle_group_help))
    application.add_handler(MessageHandler(filters.CONTACT, handle_contact_shared))
    application.add_handler(MessageHandler(filters.LOCATION, handle_location_shared))
    application.add_handler(MessageHandler(filters.VOICE | filters.AUDIO, handle_voice))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text))

    logger.info("Codexs Telegram bot started.")
    logger.info(f"Admin User IDs configured: {settings.admin_user_ids}")
    logger.info(f"Group Chat ID configured: {settings.group_chat_id}")
    logger.info(f"Total admin commands registered: 7 (admin, status, stats, debug, sessions, cleanup, testgroup)")
    if not settings.group_chat_id:
        logger.warning("⚠️ GROUP_CHAT_ID not set! Application notifications will not be sent to group.")
    application.run_polling()


if __name__ == "__main__":
    main()

