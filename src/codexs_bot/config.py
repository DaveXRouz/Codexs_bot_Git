from __future__ import annotations

import logging
import os
from dataclasses import dataclass
from pathlib import Path
from typing import List, Optional

from dotenv import load_dotenv

logger = logging.getLogger(__name__)


@dataclass(slots=True)
class Settings:
    bot_token: str
    data_dir: Path
    applications_file: Path
    contact_file: Path
    voice_dir: Path
    sessions_dir: Path
    application_webhook_url: Optional[str]
    application_webhook_token: Optional[str]
    contact_webhook_url: Optional[str]
    enable_media: bool
    group_chat_id: Optional[int]
    media_dir: Path
    openai_api_key: Optional[str]
    openai_model: str
    admin_user_ids: List[int]
    bot_config_url: Optional[str]
    bot_status_url: Optional[str]
    bot_log_url: Optional[str]
    bot_api_key: Optional[str]


def load_settings() -> Settings:
    """Load environment configuration and ensure data directories exist."""
    load_dotenv()

    token_raw = os.getenv("BOT_TOKEN")
    token = ""
    if token_raw:
        sanitized_token = "".join(ch for ch in token_raw if ch.isprintable()).strip()
        if sanitized_token != token_raw:
            logger.warning(
                "BOT_TOKEN contained leading/trailing or non-printable characters. "
                "Sanitizing value before use."
            )

        if sanitized_token.lower().startswith("bot="):
            logger.warning("BOT_TOKEN started with 'bot='. Removing prefix.")
            sanitized_token = sanitized_token[4:]
        elif sanitized_token.startswith("="):
            logger.warning("BOT_TOKEN started with '='. Removing leading '='.")
            sanitized_token = sanitized_token.lstrip("=")

        token = sanitized_token

    if not token:
        raise RuntimeError("BOT_TOKEN is missing. Set it in your environment or .env file.")

    project_root = Path(__file__).resolve().parents[2]
    data_dir_value = os.getenv("DATA_DIR")
    data_dir = (
        Path(data_dir_value).expanduser()
        if data_dir_value
        else project_root / "data"
    )
    data_dir.mkdir(parents=True, exist_ok=True)

    voice_dir = data_dir / "voice_samples"
    voice_dir.mkdir(parents=True, exist_ok=True)

    sessions_dir = data_dir / "sessions"
    sessions_dir.mkdir(parents=True, exist_ok=True)

    media_dir = project_root / "media"
    media_dir.mkdir(parents=True, exist_ok=True)

    application_webhook_url = os.getenv("APPLICATION_WEBHOOK_URL")
    application_webhook_token = os.getenv("APPLICATION_WEBHOOK_TOKEN")
    contact_webhook_url = os.getenv("CONTACT_WEBHOOK_URL")
    enable_media = os.getenv("ENABLE_MEDIA", "false").lower() in {"1", "true", "yes", "on"}
    group_chat_id = os.getenv("GROUP_CHAT_ID")
    group_chat_id_value: Optional[int] = None
    if group_chat_id:
        try:
            group_chat_id_value = int(group_chat_id)
        except ValueError:
            logger.warning(f"Invalid GROUP_CHAT_ID: {group_chat_id}. Must be an integer.")
    openai_api_key = os.getenv("OPENAI_API_KEY")
    openai_model = os.getenv("OPENAI_MODEL", "gpt-4o-mini")
    bot_config_url = os.getenv("BOT_CONFIG_URL")
    bot_status_url = os.getenv("BOT_STATUS_URL")
    bot_log_url = os.getenv("BOT_LOG_URL")
    bot_api_key = os.getenv("BOT_API_KEY")
    
    # Load admin user IDs (comma-separated)
    admin_ids_str = os.getenv("ADMIN_USER_IDS", "")
    admin_user_ids: List[int] = []
    if admin_ids_str:
        for admin_id_str in admin_ids_str.split(","):
            admin_id_str = admin_id_str.strip()
            if admin_id_str:
                try:
                    admin_user_ids.append(int(admin_id_str))
                except ValueError:
                    logger.warning(f"Invalid admin user ID: {admin_id_str}")

    return Settings(
        bot_token=token,
        data_dir=data_dir,
        applications_file=data_dir / "applications.jsonl",
        contact_file=data_dir / "contact_messages.jsonl",
        voice_dir=voice_dir,
        sessions_dir=sessions_dir,
        application_webhook_url=application_webhook_url,
        application_webhook_token=application_webhook_token,
        contact_webhook_url=contact_webhook_url,
        enable_media=enable_media,
        group_chat_id=group_chat_id_value,
        media_dir=media_dir,
        openai_api_key=openai_api_key,
        openai_model=openai_model,
        admin_user_ids=admin_user_ids,
        bot_config_url=bot_config_url,
        bot_status_url=bot_status_url,
        bot_log_url=bot_log_url,
        bot_api_key=bot_api_key,
    )

