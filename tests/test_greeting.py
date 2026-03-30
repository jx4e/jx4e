import os
import sys
from datetime import date
from unittest.mock import patch, MagicMock

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'scripts'))

from features.greeting import generate


def test_generate_returns_claude_response():
    mock_message = MagicMock()
    mock_message.content = [MagicMock(text="Happy Monday! Let's ship something that doesn't break prod 🚀💻")]

    mock_client = MagicMock()
    mock_client.messages.create.return_value = mock_message

    with patch("features.greeting.anthropic.Anthropic", return_value=mock_client):
        result = generate()

    assert result == "Happy Monday! Let's ship something that doesn't break prod 🚀💻"


def test_generate_includes_date_in_prompt():
    mock_message = MagicMock()
    mock_message.content = [MagicMock(text="Hello! 👋")]

    mock_client = MagicMock()
    mock_client.messages.create.return_value = mock_message

    fixed_date = date(2026, 3, 30)  # Monday
    with patch("features.greeting.anthropic.Anthropic", return_value=mock_client), \
         patch("features.greeting.date") as mock_date:
        mock_date.today.return_value = fixed_date
        generate()

    prompt = mock_client.messages.create.call_args[1]["messages"][0]["content"]
    assert "2026-03-30" in prompt
    assert "Monday" in prompt


def test_generate_uses_correct_model():
    mock_message = MagicMock()
    mock_message.content = [MagicMock(text="Hey! 👋")]

    mock_client = MagicMock()
    mock_client.messages.create.return_value = mock_message

    with patch("features.greeting.anthropic.Anthropic", return_value=mock_client):
        generate()

    assert mock_client.messages.create.call_args[1]["model"] == "claude-sonnet-4-20250514"
