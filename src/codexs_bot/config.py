from __future__ import annotations

import logging
import os
from dataclasses import dataclass
from pathlib import Path
from typing import Optional

from dotenv import load_dotenv

logger = logging.getLogger(__name__)


@dataclass(slots=True)
class Settings:
    bot_token: str
    data_dir: Path
    applications_file: Path
    contact_file: Path
    voice_dir: Path
    application_webhook_url: Optional[str]
    application_webhook_token: Optional[str]
    contact_webhook_url: Optional[str]
    enable_media: bool
    group_chat_id: Optional[int]
    media_dir: Path


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

    media_dir = project_root / "media"
    media_dir.mkdir(parents=True, exist_ok=True)

    application_webhook_url = os.getenv("APPLICATION_WEBHOOK_URL")
    application_webhook_token = os.getenv("APPLICATION_WEBHOOK_TOKEN")
    contact_webhook_url = os.getenv("CONTACT_WEBHOOK_URL")
    enable_media = os.getenv("ENABLE_MEDIA", "false").lower() in {"1", "true", "yes", "on"}
    group_chat_id = os.getenv("GROUP_CHAT_ID")
    group_chat_id_value = int(group_chat_id) if group_chat_id else None

    return Settings(
        bot_token=token,
        data_dir=data_dir,
        applications_file=data_dir / "applications.jsonl",
        contact_file=data_dir / "contact_messages.jsonl",
        voice_dir=voice_dir,
        application_webhook_url=application_webhook_url,
        application_webhook_token=application_webhook_token,
        contact_webhook_url=contact_webhook_url,
        enable_media=enable_media,
        group_chat_id=group_chat_id_value,
        media_dir=media_dir,
    )

