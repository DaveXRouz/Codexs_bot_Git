from __future__ import annotations

import asyncio
import logging
from typing import Any, Dict, List, Optional

import httpx

from .config import Settings
from .localization import (
    apply_remote_content_blocks,
    apply_remote_questions,
)
from .remote_config import remote_config

SUPABASE_ANON_KEY = (
    "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImVtYmN6b2x2anFuYmFxZXdsc2xjIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NjM3MzkxNTcsImV4cCI6MjA3OTMxNTE1N30.5LIjzPpSR-scoYhzrfqF_6ab4l165U0dlUOjEa3W5J4"
)

logger = logging.getLogger(__name__)

# Constants for retry logic
MAX_RETRIES = 3
RETRY_DELAY_SECONDS = 1


class SupabaseBotClient:
    """Handles communication with Supabase Edge Functions."""

    def __init__(self, settings: Settings) -> None:
        self._supabase_url = settings.supabase_url
        self._config_url = settings.bot_config_url
        self._status_url = settings.bot_status_url
        self._log_url = settings.bot_log_url
        self._api_key = settings.supabase_bot_key
        self._webhook_secret = settings.bot_webhook_secret or settings.bot_api_key
        
        # Construct application submission URL
        if self._supabase_url:
            self._applications_url = f"{self._supabase_url}/functions/v1/telegram-applications"
        else:
            self._applications_url = None

    @property
    def enabled(self) -> bool:
        return bool(self._api_key)

    @property
    def supabase_enabled(self) -> bool:
        """Check if full Supabase integration is enabled."""
        return bool(self._supabase_url and self._api_key)

    def _headers(self) -> Dict[str, str]:
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {SUPABASE_ANON_KEY}",
        }
        if self._api_key:
            headers["x-bot-key"] = self._api_key
        return headers

    def _application_headers(self) -> Dict[str, str]:
        """Headers for application submission (standardized to x-bot-key)."""
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {SUPABASE_ANON_KEY}",
        }
        if self._api_key:
            headers["x-bot-key"] = self._api_key
        return headers

    async def fetch_bot_config(self) -> Optional[Dict[str, Any]]:
        """Fetch the complete bot configuration payload from Supabase."""
        if not self._config_url or not self.enabled:
            return None
        try:
            async with httpx.AsyncClient(timeout=10) as client:
                headers = {
                    "Authorization": f"Bearer {SUPABASE_ANON_KEY}",
                    "x-bot-key": self._api_key or "",
                    "Content-Type": "application/json",
                }
                response = await client.get(self._config_url, headers=headers)
                response.raise_for_status()
                return response.json()
        except Exception as exc:  # pylint: disable=broad-except
            logger.warning("Failed to fetch remote bot config: %s", exc)
            return None

    async def refresh_remote_content(self) -> bool:
        """Fetch latest Supabase config and update localization/menus."""
        payload = await self.fetch_bot_config()
        if not payload:
            return False

        remote_config.update_from_payload(payload)

        questions = payload.get("questions")
        content = payload.get("content")
        if questions:
            apply_remote_questions(questions)
            logger.info("Applied %d remote questions from Supabase", len(questions))
        if content:
            apply_remote_content_blocks(content)
            logger.info(
                "Applied %d remote content blocks from Supabase",
                len(content) if isinstance(content, (list, tuple)) else len(content.keys()),
            )
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

    async def submit_application(
        self,
        applicant_data: Dict[str, Any],
    ) -> Optional[Dict[str, Any]]:
        """
        Submit a completed application to Supabase with retry logic.
        
        Returns the response dict on success, None on failure.
        """
        if not self._applications_url or not self.supabase_enabled:
            logger.debug("Supabase application submission not configured, skipping")
            return None

        for attempt in range(1, MAX_RETRIES + 1):
            try:
                async with httpx.AsyncClient(timeout=15) as client:
                    response = await client.post(
                        self._applications_url,
                        headers=self._application_headers(),
                        json=applicant_data,
                    )
                    response.raise_for_status()
                    result = response.json()
                    logger.info(
                        "Application submitted to Supabase successfully (attempt %d): %s",
                        attempt,
                        result.get("applicant_id", "unknown"),
                    )
                    return result
            except httpx.HTTPStatusError as exc:
                logger.warning(
                    "Supabase application submission failed (attempt %d/%d) - HTTP %s: %s",
                    attempt,
                    MAX_RETRIES,
                    exc.response.status_code,
                    exc.response.text[:200] if exc.response.text else "no body",
                )
            except Exception as exc:  # pylint: disable=broad-except
                logger.warning(
                    "Supabase application submission failed (attempt %d/%d): %s",
                    attempt,
                    MAX_RETRIES,
                    exc,
                )

            if attempt < MAX_RETRIES:
                await asyncio.sleep(RETRY_DELAY_SECONDS * attempt)

        logger.error("All %d Supabase submission attempts failed", MAX_RETRIES)
        return None

    async def get_bot_status(self) -> Optional[Dict[str, Any]]:
        """
        Get bot status and statistics from Supabase.
        
        Returns response like:
        {
            "status": "healthy",
            "timestamp": "2024-01-15T10:30:00Z",
            "stats": {
                "total_applicants": 45,
                "total_logs": 1250,
                "questions_count": 12,
                "content_count": 5
            }
        }
        """
        if not self._status_url or not self.enabled:
            return None

        try:
            async with httpx.AsyncClient(timeout=10) as client:
                response = await client.get(
                    self._status_url,
                    headers=self._headers(),
                )
                response.raise_for_status()
                return response.json()
        except Exception as exc:  # pylint: disable=broad-except
            logger.warning("Failed to fetch bot status: %s", exc)
            return None

    async def log_outgoing_message(
        self,
        telegram_user_id: int,
        username: Optional[str],
        text: str,
        message_type: str = "text",
    ) -> None:
        """Convenience method to log an outgoing bot message."""
        await self.log_message(
            telegram_user_id=telegram_user_id,
            username=username,
            direction="outgoing",
            message_type=message_type,
            text=text,
        )

    async def log_incoming_message(
        self,
        telegram_user_id: int,
        username: Optional[str],
        text: Optional[str],
        message_type: str = "text",
        payload: Optional[Dict[str, Any]] = None,
    ) -> None:
        """Convenience method to log an incoming user message."""
        await self.log_message(
            telegram_user_id=telegram_user_id,
            username=username,
            direction="incoming",
            message_type=message_type,
            text=text,
            payload=payload,
        )
