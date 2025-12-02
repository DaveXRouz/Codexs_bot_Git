from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional

from .localization import Language, main_menu_labels


def _normalize_content_payload(content_payload: Any) -> Dict[str, Dict[str, Optional[str]]]:
    """
    Ensure content blocks are stored as {slug: {en_body, fa_body}} regardless of
    whether Supabase returned a dict or list.
    """
    if not content_payload:
        return {}
    if isinstance(content_payload, dict):
        return {
            slug: {
                "en_body": (data or {}).get("en_body"),
                "fa_body": (data or {}).get("fa_body"),
            }
            for slug, data in content_payload.items()
            if isinstance(data, dict)
        }
    if isinstance(content_payload, list):
        normalized: Dict[str, Dict[str, Optional[str]]] = {}
        for entry in content_payload:
            if not isinstance(entry, dict):
                continue
            slug = entry.get("slug")
            if not slug:
                continue
            normalized[slug] = {
                "en_body": entry.get("en_body"),
                "fa_body": entry.get("fa_body"),
            }
        return normalized
    return {}


def _ensure_dict_by_key(items: Any, key_name: str) -> Dict[str, Dict[str, Any]]:
    if not isinstance(items, list):
        return {}
    mapped: Dict[str, Dict[str, Any]] = {}
    for entry in items:
        if not isinstance(entry, dict):
            continue
        key_value = entry.get(key_name)
        if not key_value:
            continue
        mapped[key_value] = entry
    return mapped


@dataclass
class RemoteConfig:
    menu_buttons: List[Dict[str, Any]] = field(default_factory=list)
    flows: Dict[str, Dict[str, Any]] = field(default_factory=dict)
    questions: Dict[str, Dict[str, Any]] = field(default_factory=dict)
    content_blocks: Dict[str, Dict[str, Optional[str]]] = field(default_factory=dict)
    settings: Dict[str, Any] = field(default_factory=dict)
    commands: List[Dict[str, Any]] = field(default_factory=list)
    buttons: List[Dict[str, Any]] = field(default_factory=list)
    exams: List[Dict[str, Any]] = field(default_factory=list)
    last_refresh: Optional[str] = None

    def update_from_payload(self, payload: Dict[str, Any]) -> None:
        self.menu_buttons = payload.get("menu_buttons", []) or []
        self.flows = _ensure_dict_by_key(payload.get("flows") or [], "flow_key")
        self.questions = _ensure_dict_by_key(payload.get("questions") or [], "question_key")
        self.content_blocks = _normalize_content_payload(payload.get("content"))
        self.settings = payload.get("settings", {}) or {}
        self.commands = payload.get("commands", []) or []
        self.buttons = payload.get("buttons", []) or []
        self.exams = payload.get("exams", []) or []
        self.last_refresh = payload.get("fetched_at")

    def has_menu(self) -> bool:
        return bool(self.menu_buttons)

    def build_menu_rows(self, language: Language) -> List[List[str]]:
        if not self.menu_buttons:
            return []
        sorted_buttons = sorted(
            self.menu_buttons,
            key=lambda btn: btn.get("order_index", 999),
        )
        keyboard: List[List[str]] = []
        row: List[str] = []
        for button in sorted_buttons:
            label = self._button_label(button, language)
            if not label:
                continue
            row.append(label)
            if len(row) == 2:
                keyboard.append(row)
                row = []
        if row:
            keyboard.append(row)
        return keyboard

    def find_menu_button(self, text: str, language: Language) -> Optional[Dict[str, Any]]:
        normalized = text.strip()
        for button in self.menu_buttons:
            labels = {
                self._button_label(button, Language.EN),
                self._button_label(button, Language.FA),
                (button.get("en_text") or "").strip(),
                (button.get("fa_text") or "").strip(),
            }
            if normalized in {label for label in labels if label}:
                return button
        return None

    def get_flow(self, flow_key: Optional[str]) -> Optional[Dict[str, Any]]:
        if not flow_key:
            return None
        return self.flows.get(flow_key)

    def get_question_prompt(self, question_key: Optional[str], language: Language) -> Optional[str]:
        if not question_key:
            return None
        data = self.questions.get(question_key)
        if not data:
            return None
        lang_key = f"{language.value}_text"
        return data.get(lang_key) or data.get("en_text")

    def get_content_text(
        self,
        slug: Optional[str],
        language: Language,
        default: Optional[str] = None,
    ) -> Optional[str]:
        if not slug:
            return default
        block = self.content_blocks.get(slug)
        if not block:
            return default
        lang_key = f"{language.value}_body"
        text = block.get(lang_key)
        if text:
            return text
        fallback = block.get("en_body")
        return fallback or default

    def get_setting(self, key: str, default: Optional[Any] = None) -> Optional[Any]:
        return self.settings.get(key, default) if self.settings else default

    @staticmethod
    def _button_label(button: Dict[str, Any], language: Language) -> Optional[str]:
        text = button.get("fa_text") if language == Language.FA else button.get("en_text")
        if not text:
            text = button.get("en_text")
        if not text:
            return None
        emoji = button.get("emoji") or ""
        label = f"{emoji} {text}".strip()
        return label or None


remote_config = RemoteConfig()


def default_menu_rows(language: Language) -> List[List[str]]:
    """
    Helper that returns remote rows when available, falling back to static labels.
    """
    remote_rows = remote_config.build_menu_rows(language)
    if remote_rows:
        return remote_rows
    return main_menu_labels(language)

