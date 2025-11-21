from __future__ import annotations

from dataclasses import dataclass, field
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
    awaiting_view_roles: bool = False

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
        self.awaiting_view_roles = False

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
        self.awaiting_view_roles = False

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


def get_session(user_data: Dict[str, Any]) -> UserSession:
    session = user_data.get("session")
    if not isinstance(session, UserSession):
        session = UserSession()
        user_data["session"] = session
    return session

