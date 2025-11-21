from __future__ import annotations

import asyncio
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional

from .localization import Language


class DataStorage:
    """Handles persistence for applications, contact messages, sessions, and metadata."""

    def __init__(self, applications_file: Path, contact_file: Path, sessions_dir: Path) -> None:
        self._applications_file = applications_file
        self._contact_file = contact_file
        self._sessions_dir = sessions_dir
        self._application_lock = asyncio.Lock()
        self._contact_lock = asyncio.Lock()
        self._sessions_dir.mkdir(parents=True, exist_ok=True)

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

    def _session_file(self, user_id: int) -> Path:
        """Get session file path for a user."""
        return self._sessions_dir / f"session_{user_id}.json"

    async def save_session(self, user_id: int, session_data: Dict[str, Any]) -> None:
        """Save user session to disk."""
        session_file = self._session_file(user_id)
        await asyncio.to_thread(self._write_session, session_file, session_data)

    @staticmethod
    def _write_session(session_file: Path, session_data: Dict[str, Any]) -> None:
        """Write session data to file."""
        session_file.parent.mkdir(parents=True, exist_ok=True)
        with session_file.open("w", encoding="utf-8") as handle:
            json.dump(session_data, handle, ensure_ascii=False, indent=2)

    async def load_session(self, user_id: int) -> Optional[Dict[str, Any]]:
        """Load user session from disk."""
        session_file = self._session_file(user_id)
        if not session_file.exists():
            return None
        try:
            return await asyncio.to_thread(self._read_session, session_file)
        except Exception:
            return None

    @staticmethod
    def _read_session(session_file: Path) -> Dict[str, Any]:
        """Read session data from file."""
        with session_file.open("r", encoding="utf-8") as handle:
            return json.load(handle)

    async def delete_session(self, user_id: int) -> None:
        """Delete user session file."""
        session_file = self._session_file(user_id)
        if session_file.exists():
            await asyncio.to_thread(session_file.unlink)

    async def get_user_applications(self, user_id: int) -> List[Dict[str, Any]]:
        """Get all applications submitted by a user."""
        if not self._applications_file.exists():
            return []
        try:
            return await asyncio.to_thread(self._read_user_applications, self._applications_file, user_id)
        except Exception:
            return []

    @staticmethod
    def _read_user_applications(applications_file: Path, user_id: int) -> List[Dict[str, Any]]:
        """Read and filter applications by user ID."""
        applications = []
        with applications_file.open("r", encoding="utf-8") as handle:
            for line in handle:
                line = line.strip()
                if not line:
                    continue
                try:
                    app = json.loads(line)
                    applicant = app.get("applicant", {})
                    if applicant.get("telegram_id") == user_id:
                        applications.append(app)
                except json.JSONDecodeError:
                    continue
        # Sort by submission date (newest first)
        applications.sort(key=lambda x: x.get("submitted_at", ""), reverse=True)
        return applications

