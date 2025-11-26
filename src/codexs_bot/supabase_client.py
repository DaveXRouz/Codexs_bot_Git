from __future__ import annotations

import asyncio
import logging
from typing import Any, Dict, Optional

import httpx

from .config import Settings
from .localization import (
    apply_remote_content_blocks,
    apply_remote_questions,
)

logger = logging.getLogger(__name__)


class SupabaseBotClient:
    """Handles communication with Supabase Edge Functions."""

    def __init__(self, settings: Settings) -> None:
        self._config_url = settings.bot_config_url
        self._status_url = settings.bot_status_url
        self._log_url = settings.bot_log_url
        self._api_key = settings.bot_api_key

    @property
    def enabled(self) -> bool:
        return bool(self._api_key)

    def _headers(self) -> Dict[str, str]:
        headers = {"Content-Type": "application/json"}
        if self._api_key:
            headers["x-bot-key"] = self._api_key
        return headers

    async def refresh_remote_content(self) -> bool:
        """Fetch latest question/content config and apply overrides."""
        if not self._config_url or not self.enabled:
            return False

        try:
            async with httpx.AsyncClient(timeout=10) as client:
                response = await client.get(self._config_url, headers=self._headers())
                response.raise_for_status()
                payload = response.json()
        except Exception as exc:  # pylint: disable=broad-except
            logger.warning("Failed to fetch remote bot config: %s", exc)
            return False

        questions = payload.get("questions")
        content = payload.get("content")
        if questions:
            apply_remote_questions(questions)
        if content:
            apply_remote_content_blocks(content)
        return True

    async def fetch_applicant_status(self, telegram_user_id: int) -> Optional[Dict[str, Any]]:
        """Retrieve the applicant's current stage from Supabase."""
        if not self._status_url or not self.enabled:
            return None

        params = {"telegram_user_id": str(telegram_user_id)}
        try:
            async with httpx.AsyncClient(timeout=10) as client:
                response = await client.get(
                    self._status_url,
                    params=params,
                    headers=self._headers(),
                )
                response.raise_for_status()
                return response.json()
        except httpx.HTTPStatusError as exc:
            if exc.response.status_code == 404:
                return None
            logger.warning("Status lookup failed (%s): %s", exc.response.status_code, exc)
        except Exception as exc:  # pylint: disable=broad-except
            logger.warning("Status lookup failed: %s", exc)
        return None

    async def log_message(
        self,
        *,
        telegram_user_id: int,
        username: Optional[str],
        direction: str,
        message_type: str,
        text: Optional[str],
        payload: Optional[Dict[str, Any]] = None,
    ) -> None:
        """Send chat transcript events to Supabase for the CCC conversation log."""
        if not self._log_url or not self.enabled:
            return

        body = {
            "telegram_user_id": telegram_user_id,
            "username": username,
            "direction": direction,
            "message_type": message_type,
            "text": text,
            "payload": payload or {},
        }

        async def _post() -> None:
            try:
                async with httpx.AsyncClient(timeout=10) as client:
                    await client.post(self._log_url, json=body, headers=self._headers())
            except Exception as exc:  # pylint: disable=broad-except
                logger.debug("Failed to push chat log event: %s", exc)

        # Don't block bot replies—schedule logging in the background
        asyncio.create_task(_post())

