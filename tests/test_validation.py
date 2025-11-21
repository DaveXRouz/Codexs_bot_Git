"""Tests for validation functions."""
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

import pytest
from codexs_bot.bot import _validate_email, _validate_text_length, _sanitize_html


class TestEmailValidation:
    """Test email validation function."""
    
    def test_valid_emails(self):
        """Test valid email addresses."""
        valid_emails = [
            "test@example.com",
            "user.name@domain.co.uk",
            "user+tag@example.org",
            "test123@test-domain.com",
        ]
        for email in valid_emails:
            assert _validate_email(email), f"{email} should be valid"
    
    def test_invalid_emails(self):
        """Test invalid email addresses."""
        invalid_emails = [
            "notanemail",
            "@example.com",
            "user@",
            "user@domain",
            "user @domain.com",
            "user@domain .com",
        ]
        for email in invalid_emails:
            assert not _validate_email(email), f"{email} should be invalid"
    
    def test_empty_email(self):
        """Test empty email."""
        assert not _validate_email("")
        assert not _validate_email("   ")


class TestTextLengthValidation:
    """Test text length validation function."""
    
    def test_valid_length(self):
        """Test text within limit."""
        short_text = "This is a short text"
        assert _validate_text_length(short_text, max_length=1000)
    
    def test_exact_length(self):
        """Test text at exact limit."""
        exact_text = "a" * 1000
        assert _validate_text_length(exact_text, max_length=1000)
    
    def test_too_long(self):
        """Test text exceeding limit."""
        long_text = "a" * 1001
        assert not _validate_text_length(long_text, max_length=1000)
    
    def test_empty_text(self):
        """Test empty text."""
        assert _validate_text_length("", max_length=1000)
        assert _validate_text_length("   ", max_length=1000)  # Stripped
    
    def test_custom_limit(self):
        """Test custom length limit."""
        text = "a" * 500
        assert _validate_text_length(text, max_length=500)
        assert not _validate_text_length(text, max_length=499)


class TestHTMLSanitization:
    """Test HTML sanitization function."""
    
    def test_basic_sanitization(self):
        """Test basic HTML escaping."""
        text = "<script>alert('xss')</script>"
        sanitized = _sanitize_html(text)
        assert "<script>" not in sanitized
        assert "&lt;script&gt;" in sanitized
    
    def test_html_tags(self):
        """Test HTML tag escaping."""
        text = "<b>bold</b> <i>italic</i>"
        sanitized = _sanitize_html(text)
        assert "<b>" not in sanitized
        assert "<i>" not in sanitized
        assert "&lt;b&gt;" in sanitized
    
    def test_quotes(self):
        """Test quote escaping."""
        text = 'Text with "quotes" and \'apostrophes\''
        sanitized = _sanitize_html(text)
        assert "&quot;" in sanitized or "&#x27;" in sanitized
    
    def test_safe_text(self):
        """Test that safe text is unchanged."""
        text = "This is safe text without HTML"
        sanitized = _sanitize_html(text)
        assert sanitized == text
    
    def test_ampersand(self):
        """Test ampersand escaping."""
        text = "A & B"
        sanitized = _sanitize_html(text)
        assert "&amp;" in sanitized
    
    def test_empty_string(self):
        """Test empty string."""
        assert _sanitize_html("") == ""
        assert _sanitize_html("   ") == "   "

