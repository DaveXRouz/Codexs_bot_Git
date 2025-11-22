from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum, auto
from typing import Any, Dict, Optional

from .localization import Language


class Flow(Enum):
    IDLE = auto()
    APPLY = auto()
    CONTACT_MESSAGE = auto()
    CONFIRM = auto()


@dataclass
class UserSession:
    language: Optional[Language] = None
    flow: Flow = Flow.IDLE
    question_index: int = 0
    answers: Dict[str, Optional[str]] = field(default_factory=dict)
    waiting_voice: bool = False
    voice_file_path: Optional[str] = None
    voice_file_id: Optional[str] = None
    voice_message_id: Optional[int] = None
    user_chat_id: Optional[int] = None
    is_candidate: bool = False
    edit_mode: bool = False
    contact_pending: bool = False
    awaiting_edit_selection: bool = False
    voice_skipped: bool = False
    exit_confirmation_pending: bool = False
    exit_confirmation_flow: Optional[Flow] = None
    resume_original_flow: Optional[Flow] = None  # Store original flow during resume prompt
    awaiting_view_roles: bool = False
    last_menu_choice: Optional[str] = None
    ai_reply_count: int = 0
    ai_window_start: Optional[datetime] = None

    def reset_hiring(self) -> None:
        self.flow = Flow.IDLE
        self.question_index = 0
        self.answers.clear()
        self.waiting_voice = False
        self.voice_file_path = None
        self.voice_file_id = None
        self.voice_message_id = None
        self.user_chat_id = None
        self.edit_mode = False
        self.awaiting_edit_selection = False
        self.voice_skipped = False
        self.exit_confirmation_pending = False
        self.exit_confirmation_flow = None
        self.resume_original_flow = None
        self.awaiting_view_roles = False
        self.last_menu_choice = None

    def start_hiring(self) -> None:
        self.flow = Flow.APPLY
        self.question_index = 0
        self.answers.clear()
        self.waiting_voice = False
        self.voice_file_path = None
        self.voice_file_id = None
        self.voice_message_id = None
        self.user_chat_id = None
        self.edit_mode = False
        self.awaiting_edit_selection = False
        self.voice_skipped = False
        self.exit_confirmation_pending = False
        self.exit_confirmation_flow = None
        self.resume_original_flow = None
        self.awaiting_view_roles = False
        self.last_menu_choice = "apply"

    def mark_voice_wait(self) -> None:
        self.waiting_voice = True

    def finish_voice_wait(self) -> None:
        self.waiting_voice = False

    def request_exit_confirmation(self, flow: Flow) -> None:
        self.exit_confirmation_pending = True
        self.exit_confirmation_flow = flow

    def cancel_exit_confirmation(self) -> None:
        self.exit_confirmation_pending = False
        self.exit_confirmation_flow = None

    def to_dict(self) -> Dict[str, Any]:
        """Serialize session to dictionary for persistence."""
        return {
            "language": self.language.value if self.language else None,
            "flow": self.flow.name if self.flow else None,
            "question_index": self.question_index,
            "answers": self.answers,
            "waiting_voice": self.waiting_voice,
            "voice_file_path": self.voice_file_path,
            "voice_file_id": self.voice_file_id,
            "voice_message_id": self.voice_message_id,
            "user_chat_id": self.user_chat_id,
            "is_candidate": self.is_candidate,
            "edit_mode": self.edit_mode,
            "contact_pending": self.contact_pending,
            "awaiting_edit_selection": self.awaiting_edit_selection,
            "voice_skipped": self.voice_skipped,
            "exit_confirmation_pending": self.exit_confirmation_pending,
            "exit_confirmation_flow": self.exit_confirmation_flow.name if self.exit_confirmation_flow else None,
            "awaiting_view_roles": self.awaiting_view_roles,
            "last_menu_choice": self.last_menu_choice,
            "ai_reply_count": self.ai_reply_count,
            "ai_window_start": self.ai_window_start.isoformat() if self.ai_window_start else None,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "UserSession":
        """Deserialize session from dictionary with defensive error handling."""
        session = cls()
        try:
            if data.get("language"):
                try:
                    session.language = Language(data["language"])
                except (ValueError, KeyError):
                    # Invalid language value - use None (will prompt for language)
                    session.language = None
            if data.get("flow"):
                try:
                    session.flow = Flow[data["flow"]]
                except (ValueError, KeyError):
                    # Invalid flow value - default to IDLE
                    session.flow = Flow.IDLE
            session.question_index = data.get("question_index", 0)
            # Validate answers is a dict
            answers = data.get("answers", {})
            if isinstance(answers, dict):
                session.answers = answers
            else:
                session.answers = {}
            session.waiting_voice = data.get("waiting_voice", False)
            session.voice_file_path = data.get("voice_file_path")
            session.voice_file_id = data.get("voice_file_id")
            session.voice_message_id = data.get("voice_message_id")
            session.user_chat_id = data.get("user_chat_id")
            session.is_candidate = data.get("is_candidate", False)
            session.edit_mode = data.get("edit_mode", False)
            session.contact_pending = data.get("contact_pending", False)
            session.awaiting_edit_selection = data.get("awaiting_edit_selection", False)
            session.voice_skipped = data.get("voice_skipped", False)
            session.exit_confirmation_pending = data.get("exit_confirmation_pending", False)
            if data.get("exit_confirmation_flow"):
                try:
                    session.exit_confirmation_flow = Flow[data["exit_confirmation_flow"]]
                except (ValueError, KeyError):
                    session.exit_confirmation_flow = None
            session.awaiting_view_roles = data.get("awaiting_view_roles", False)
            session.last_menu_choice = data.get("last_menu_choice")
            session.ai_reply_count = data.get("ai_reply_count", 0)
            if data.get("ai_window_start"):
                try:
                    session.ai_window_start = datetime.fromisoformat(data["ai_window_start"])
                except (ValueError, TypeError):
                    session.ai_window_start = None
        except Exception:
            # If anything goes wrong, return a fresh session
            return cls()
        return session

    def has_incomplete_application(self) -> bool:
        """Check if session has an incomplete application that can be resumed."""
        return (
            self.flow == Flow.APPLY
            and self.question_index > 0
            and len(self.answers) > 0
        ) or (
            self.flow == Flow.CONFIRM
            and len(self.answers) > 0
        ) or (
            self.waiting_voice
            and len(self.answers) > 0
        )


def get_session(user_data: Dict[str, Any]) -> UserSession:
    session = user_data.get("session")
    if not isinstance(session, UserSession):
        session = UserSession()
        user_data["session"] = session
    return session

