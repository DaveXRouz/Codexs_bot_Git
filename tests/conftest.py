"""Pytest configuration and fixtures."""
import pytest
from unittest.mock import MagicMock
from telegram import Update, Message, User, Chat
from telegram.ext import ContextTypes


@pytest.fixture
def mock_update():
    """Create a mock Telegram Update."""
    update = MagicMock(spec=Update)
    update.message = MagicMock(spec=Message)
    update.message.text = "test"
    update.message.message_id = 123
    update.message.reply_text = MagicMock()
    update.message.reply_photo = MagicMock()
    update.effective_user = MagicMock(spec=User)
    update.effective_user.id = 12345
    update.effective_user.username = "testuser"
    update.effective_user.first_name = "Test"
    update.effective_user.last_name = "User"
    update.effective_chat = MagicMock(spec=Chat)
    update.effective_chat.id = 12345
    return update


@pytest.fixture
def mock_context():
    """Create a mock Telegram Context."""
    context = MagicMock(spec=ContextTypes.DEFAULT_TYPE)
    context.user_data = {}
    context.application = MagicMock()
    context.application.bot_data = {}
    context.bot = MagicMock()
    context.bot.send_message = MagicMock()
    context.bot.forward_message = MagicMock()
    context.bot.send_voice = MagicMock()
    return context

