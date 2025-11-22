from __future__ import annotations

import asyncio
import json
import logging
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional

from .localization import Language

logger = logging.getLogger(__name__)


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
        voice_skipped: bool = False,
    ) -> None:
        payload = {
            "application_id": application_id,
            "submitted_at": self._timestamp(),
            "language": language.value,
            "applicant": applicant,
            "answers": answers,
            "voice_file_path": voice_file_path,
            "voice_file_id": voice_file_id,
            "voice_skipped": voice_skipped,
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
        """Write JSONL entry with error handling."""
        try:
            file_path.parent.mkdir(parents=True, exist_ok=True)
            with file_path.open("a", encoding="utf-8") as handle:
                json.dump(payload, handle, ensure_ascii=False)
                handle.write("\n")
        except (OSError, IOError, json.JSONEncodeError) as exc:
            # Log error but re-raise to be handled by caller
            logger.error(f"Failed to write JSONL to {file_path}: {exc}", exc_info=True)
            raise

    def _session_file(self, user_id: int) -> Path:
        """Get session file path for a user."""
        return self._sessions_dir / f"session_{user_id}.json"

    async def save_session(self, user_id: int, session_data: Dict[str, Any]) -> None:
        """Save user session to disk with error handling."""
        session_file = self._session_file(user_id)
        try:
            await asyncio.to_thread(self._write_session, session_file, session_data)
        except Exception as exc:
            # Log error but don't crash - session will be lost but bot continues
            logger.error(f"Failed to save session for user {user_id}: {exc}", exc_info=True)

    @staticmethod
    def _write_session(session_file: Path, session_data: Dict[str, Any]) -> None:
        """Write session data to file with error handling."""
        try:
            session_file.parent.mkdir(parents=True, exist_ok=True)
            # Use atomic write: write to temp file, then rename
            temp_file = session_file.with_suffix(session_file.suffix + ".tmp")
            with temp_file.open("w", encoding="utf-8") as handle:
                json.dump(session_data, handle, ensure_ascii=False, indent=2)
            # Atomic rename (works on most filesystems)
            temp_file.replace(session_file)
        except (OSError, IOError, json.JSONEncodeError) as exc:
            # Re-raise to be caught by save_session
            raise

    async def load_session(self, user_id: int) -> Optional[Dict[str, Any]]:
        """Load user session from disk with error handling."""
        session_file = self._session_file(user_id)
        if not session_file.exists():
            return None
        try:
            return await asyncio.to_thread(self._read_session, session_file)
        except Exception as exc:
            # Log error but don't crash - session will be lost but bot continues
            logger.warning(f"Failed to load session for user {user_id}: {exc}", exc_info=True)
            return None

    @staticmethod
    def _read_session(session_file: Path) -> Dict[str, Any]:
        """Read session data from file with error handling."""
        try:
            with session_file.open("r", encoding="utf-8") as handle:
                return json.load(handle)
        except (json.JSONDecodeError, IOError, OSError) as exc:
            # Re-raise to be caught by load_session
            raise

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
    
    async def cleanup_old_sessions(self, days_old: int = 30) -> int:
        """Clean up session files older than specified days. Returns number of files deleted."""
        if not self._sessions_dir.exists():
            return 0
        
        from datetime import timedelta
        cutoff_time = (datetime.now(timezone.utc) - timedelta(days=days_old)).timestamp()
        deleted_count = 0
        
        def _cleanup_sessions():
            nonlocal deleted_count
            for session_file in self._sessions_dir.glob("session_*.json"):
                try:
                    if session_file.stat().st_mtime < cutoff_time:
                        session_file.unlink()
                        deleted_count += 1
                except Exception:
                    continue
            return deleted_count
        
        return await asyncio.to_thread(_cleanup_sessions)

