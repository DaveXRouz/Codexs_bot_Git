from __future__ import annotations

import asyncio
import logging
from typing import Any, Dict, Optional

from telegram import Bot, Message, Update

from .supabase_client import SupabaseBotClient

logger = logging.getLogger(__name__)

_supabase_client: Optional[SupabaseBotClient] = None
_usernames: Dict[int, Optional[str]] = {}
_patched = False


def init_conversation_logger(client: Optional[SupabaseBotClient]) -> None:
    """Store Supabase client reference and patch bot senders."""
    global _supabase_client  # pylint: disable=global-statement
    _supabase_client = client
    if client and not _patched:
        _patch_bot_methods()


async def capture_incoming(update: Update) -> None:
    """Log inbound Telegram messages to Supabase."""
    if not _supabase_client or not update.effective_user:
        return

    message = update.effective_message
    if not message:
        return

    user = update.effective_user
    _usernames[user.id] = user.username or _usernames.get(user.id)
    text = message.text or message.caption or ""
    message_type = _infer_message_type(message)
    payload = _build_payload_from_message(message)

    try:
        await _supabase_client.log_message(
            telegram_user_id=user.id,
            username=user.username,
            direction="incoming",
            message_type=message_type,
            text=text,
            payload=payload,
        )
    except Exception as exc:  # pylint: disable=broad-except
        logger.debug("Failed to log incoming message: %s", exc)


def _patch_bot_methods() -> None:
    global _patched  # pylint: disable=global-statement
    if _patched:
        return
    _patched = True

    def _wrap(method_name: str, message_type: str, text_arg_index: Optional[int] = None, text_kw: Optional[str] = None):
        original = getattr(Bot, method_name)

        async def wrapped(self: Bot, *args, **kwargs):
            result = await original(self, *args, **kwargs)
            try:
                chat_id = kwargs.get("chat_id") or (args[0] if args else None)
                text = None
                if text_kw and text_kw in kwargs:
                    text = kwargs[text_kw]
                elif text_arg_index is not None and len(args) > text_arg_index:
                    text = args[text_arg_index]
                if not text:
                    text = f"[{message_type}]"
                username = _usernames.get(chat_id) if isinstance(chat_id, int) else None
                _schedule_outgoing_log(chat_id, username, text, message_type)
            except Exception as exc:  # pylint: disable=broad-except
                logger.debug("Failed to log outgoing %s: %s", method_name, exc)
            return result

        setattr(Bot, method_name, wrapped)

    _wrap("send_message", "text", text_arg_index=1, text_kw="text")
    _wrap("send_photo", "photo", text_kw="caption")
    _wrap("send_video", "video", text_kw="caption")
    _wrap("send_audio", "audio", text_kw="caption")
    _wrap("send_voice", "voice", text_kw="caption")
    _wrap("send_document", "document", text_kw="caption")
    _wrap("send_location", "location")
    _wrap("send_contact", "contact", text_kw="first_name")


def _schedule_outgoing_log(chat_id: Optional[int], username: Optional[str], text: str, message_type: str) -> None:
    if not _supabase_client or chat_id is None:
        return

    async def _log() -> None:
        try:
            await _supabase_client.log_message(
                telegram_user_id=chat_id,
                username=username,
                direction="outgoing",
                message_type=message_type,
                text=text,
                payload={},
            )
        except Exception as exc:  # pylint: disable=broad-except
            logger.debug("Failed to log outgoing message: %s", exc)

    asyncio.create_task(_log())


def _infer_message_type(message: Message) -> str:
    if message.voice:
        return "voice"
    if message.audio:
        return "audio"
    if message.photo:
        return "photo"
    if message.video:
        return "video"
    if message.location:
        return "location"
    if message.contact:
        return "contact"
    if message.document:
        return "document"
    return "text"


def _build_payload_from_message(message: Message) -> Dict[str, Any]:
    payload: Dict[str, Any] = {}
    if message.voice:
        payload["duration"] = message.voice.duration
    if message.location:
        payload["latitude"] = message.location.latitude
        payload["longitude"] = message.location.longitude
    if message.contact:
        payload["contact"] = {
            "phone_number": message.contact.phone_number,
            "first_name": message.contact.first_name,
            "last_name": message.contact.last_name,
        }
    return payload

