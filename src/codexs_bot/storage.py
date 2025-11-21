from __future__ import annotations

import asyncio
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Optional

from .localization import Language


class DataStorage:
    """Handles persistence for applications, contact messages, and metadata."""

    def __init__(self, applications_file: Path, contact_file: Path) -> None:
        self._applications_file = applications_file
        self._contact_file = contact_file
        self._application_lock = asyncio.Lock()
        self._contact_lock = asyncio.Lock()

    @staticmethod
    def _timestamp() -> str:
        return datetime.now(timezone.utc).isoformat()

    async def save_application(
        self,
        applicant: Dict[str, Any],
        answers: Dict[str, Optional[str]],
        language: Language,
        voice_file_path: Optional[str],
        voice_file_id: Optional[str],
        application_id: Optional[str] = None,
    ) -> None:
        payload = {
            "application_id": application_id,
            "submitted_at": self._timestamp(),
            "language": language.value,
            "applicant": applicant,
            "answers": answers,
            "voice_file_path": voice_file_path,
            "voice_file_id": voice_file_id,
        }
        await self._append_jsonl(self._applications_file, payload, self._application_lock)

    async def save_contact_message(
        self,
        applicant: Dict[str, Any],
        language: Language,
        message: str,
    ) -> None:
        payload = {
            "submitted_at": self._timestamp(),
            "language": language.value,
            "sender": applicant,
            "message": message,
        }
        await self._append_jsonl(self._contact_file, payload, self._contact_lock)

    async def _append_jsonl(self, file_path: Path, payload: Dict[str, Any], lock: asyncio.Lock) -> None:
        async with lock:
            await asyncio.to_thread(self._write_jsonl, file_path, payload)

    @staticmethod
    def _write_jsonl(file_path: Path, payload: Dict[str, Any]) -> None:
        file_path.parent.mkdir(parents=True, exist_ok=True)
        with file_path.open("a", encoding="utf-8") as handle:
            json.dump(payload, handle, ensure_ascii=False)
            handle.write("\n")

