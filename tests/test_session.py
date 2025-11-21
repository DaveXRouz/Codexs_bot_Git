"""Tests for session management."""
import pytest
from codexs_bot.session import UserSession, Flow
from codexs_bot.localization import Language


class TestUserSession:
    """Test UserSession class."""
    
    def test_initial_state(self):
        """Test initial session state."""
        session = UserSession()
        assert session.language is None
        assert session.flow == Flow.IDLE
        assert session.question_index == 0
        assert session.answers == {}
        assert session.waiting_voice is False
        assert session.voice_file_path is None
    
    def test_reset_hiring(self):
        """Test reset_hiring method."""
        session = UserSession()
        session.language = Language.EN
        session.flow = Flow.APPLY
        session.question_index = 5
        session.answers = {"name": "Test"}
        session.waiting_voice = True
        
        session.reset_hiring()
        
        assert session.flow == Flow.IDLE
        assert session.question_index == 0
        assert session.answers == {}
        assert session.waiting_voice is False
        assert session.voice_file_path is None
        assert session.user_chat_id is None
    
    def test_start_hiring(self):
        """Test start_hiring method."""
        session = UserSession()
        session.start_hiring()
        
        assert session.flow == Flow.APPLY
        assert session.question_index == 0
        assert session.answers == {}
        assert session.waiting_voice is False
    
    def test_mark_voice_wait(self):
        """Test mark_voice_wait method."""
        session = UserSession()
        session.mark_voice_wait()
        assert session.waiting_voice is True
    
    def test_finish_voice_wait(self):
        """Test finish_voice_wait method."""
        session = UserSession()
        session.waiting_voice = True
        session.finish_voice_wait()
        assert session.waiting_voice is False
    
    def test_exit_confirmation(self):
        """Test exit confirmation methods."""
        session = UserSession()
        session.request_exit_confirmation(Flow.APPLY)
        
        assert session.exit_confirmation_pending is True
        assert session.exit_confirmation_flow == Flow.APPLY
        
        session.cancel_exit_confirmation()
        
        assert session.exit_confirmation_pending is False
        assert session.exit_confirmation_flow is None

