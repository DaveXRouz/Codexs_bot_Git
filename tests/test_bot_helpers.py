"""Additional tests for bot helpers and storage utilities."""
import asyncio
from datetime import datetime, timedelta, timezone

import pytest

from codexs_bot.bot import (
    RATE_LIMIT_MAX_REQUESTS,
    _build_edit_summary,
    _check_rate_limit,
    _collapse_intent_token,
    _format_question_box,
    _infer_menu_choice,
    _is_back_command,
    _is_menu_command,
    _is_repeat_command,
    _normalize_for_intent,
    _validate_and_fix_session_state,
    _validate_location,
    _validate_phone,
    _validate_url,
)
from codexs_bot.localization import HIRING_QUESTIONS, Language
from codexs_bot.session import Flow, UserSession
from codexs_bot.storage import DataStorage


def test_validation_helpers():
    """Validate phone/location/url helpers handle common cases."""
    assert _validate_phone("+1 (415) 555-1234")
    assert not _validate_phone("invalid-number")
    assert _validate_location("San Francisco, USA (PST)")
    assert not _validate_location("Somewhere")
    assert _validate_url("https://example.com/portfolio")
    assert _validate_url("github.com/user")
    assert not _validate_url("not a url")


def test_intent_detection():
    """Ensure intent helpers normalize and detect menu/back/repeat keywords."""
    text = " Menu! "
    assert _normalize_for_intent(text).strip() == "menu"
    assert _collapse_intent_token("Main Menu") == "mainmenu"
    assert _is_menu_command("menu", Language.EN)
    assert _is_back_command("back", Language.EN)
    assert _is_repeat_command("?", Language.EN)
    assert _infer_menu_choice("Can I apply for a role?", Language.EN) == "apply"


def test_question_box_and_edit_summary():
    """Render question box and edit summary with populated answers."""
    formatted = _format_question_box(
        "Q1/12",
        "Title line\nInstruction line",
        Language.EN,
    )
    assert "Q1/12" in formatted
    assert "Instruction line" in formatted

    session = UserSession(language=Language.EN, flow=Flow.APPLY)
    # Populate a couple of answers to verify rendering and skipping
    session.answers = {
        HIRING_QUESTIONS[0].key: "Alice Example",
        HIRING_QUESTIONS[1].key: "",
    }
    summary = _build_edit_summary(session, Language.EN)
    assert "Alice Example" in summary
    assert "(skipped)" in summary


def test_rate_limit_window_reset():
    """Rate limiter should allow up to the configured max, then block."""
    user_id = 999_123
    # Clear any prior state for this user
    from codexs_bot.bot import _rate_limit_store

    _rate_limit_store.pop(user_id, None)
    for _ in range(RATE_LIMIT_MAX_REQUESTS):
        assert _check_rate_limit(user_id)
    assert not _check_rate_limit(user_id)


def test_validate_and_fix_session_state():
    """Invalid session states should be corrected defensively."""
    session = UserSession(language=Language.EN, flow=Flow.CONFIRM, question_index=99)
    session.waiting_voice = True  # Invalid for CONFIRM flow
    session.contact_pending = True
    session.contact_review_pending = True
    session.contact_message_draft = None
    session.edit_mode = True
    session.awaiting_edit_selection = True

    was_valid = _validate_and_fix_session_state(session)
    assert not was_valid
    # waiting_voice cleared because flow is not APPLY
    assert session.waiting_voice is False
    assert session.contact_pending is False
    # awaiting_edit_selection stays True because CONFIRM flow is valid for edits
    assert session.awaiting_edit_selection is True


@pytest.mark.asyncio
async def test_storage_application_and_contact_roundtrip(tmp_path):
    """Exercise DataStorage JSONL persistence helpers."""
    storage = DataStorage(
        applications_file=tmp_path / "applications.jsonl",
        contact_file=tmp_path / "contacts.jsonl",
        sessions_dir=tmp_path / "sessions",
    )

    applicant = {"telegram_id": 42, "username": "user42"}
    answers = {"full_name": "Test User", "email": "user@example.com"}

    await storage.save_application(
        applicant=applicant,
        answers=answers,
        language=Language.EN,
        voice_file_path="voice.ogg",
        voice_file_id="file123",
        application_id="APP-42",
        voice_skipped=False,
    )
    await storage.save_contact_message(applicant, Language.EN, "Hello there")

    apps = await storage.get_user_applications(applicant["telegram_id"])
    assert len(apps) == 1
    assert apps[0]["application_id"] == "APP-42"

    app_by_id = await storage.get_application_by_id("APP-42")
    assert app_by_id["answers"]["email"] == "user@example.com"

    recent = await storage.get_recent_applications(limit=1)
    assert len(recent) == 1

    now = datetime.now(timezone.utc)
    in_range = await storage.get_applications_by_date_range(
        now - timedelta(minutes=1),
        now + timedelta(minutes=1),
    )
    assert len(in_range) == 1

    contacts = await storage.get_all_contact_messages()
    assert contacts and contacts[0]["message"] == "Hello there"

    contact_range = await storage.get_contact_messages_by_date_range(
        now - timedelta(minutes=1),
        now + timedelta(minutes=1),
    )
    assert len(contact_range) == 1


@pytest.mark.asyncio
async def test_storage_sessions_roundtrip(tmp_path):
    """Verify session save/load/delete lifecycle."""
    storage = DataStorage(
        applications_file=tmp_path / "applications.jsonl",
        contact_file=tmp_path / "contacts.jsonl",
        sessions_dir=tmp_path / "sessions",
    )
    await storage.save_session(7, {"foo": "bar"})
    loaded = await storage.load_session(7)
    assert loaded == {"foo": "bar"}

    await storage.delete_session(7)
    assert await storage.load_session(7) is None

    # Ensure cleanup_old_sessions doesn't error when directory is empty
    deleted = await storage.cleanup_old_sessions(days_old=0)
    assert deleted >= 0
