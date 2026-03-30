import os
import sys
from unittest.mock import patch, MagicMock

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'scripts'))

from features.banner import generate


def test_generate_returns_claude_response():
    mock_message = MagicMock()
    mock_message.content = [MagicMock(text="```\n  jx4e\n```")]
    mock_client = MagicMock()
    mock_client.messages.create.return_value = mock_message

    with patch("features.banner.anthropic.Anthropic", return_value=mock_client):
        result = generate()

    assert result == "```\n  jx4e\n```"


def test_generate_includes_jx4e_and_date_in_prompt():
    mock_message = MagicMock()
    mock_message.content = [MagicMock(text="```\njx4e\n```")]
    mock_client = MagicMock()
    mock_client.messages.create.return_value = mock_message

    with patch("features.banner.anthropic.Anthropic", return_value=mock_client):
        generate()

    prompt = mock_client.messages.create.call_args[1]["messages"][0]["content"]
    assert "jx4e" in prompt
    assert "2026" in prompt


def test_generate_uses_correct_model():
    mock_message = MagicMock()
    mock_message.content = [MagicMock(text="```\njx4e\n```")]
    mock_client = MagicMock()
    mock_client.messages.create.return_value = mock_message

    with patch("features.banner.anthropic.Anthropic", return_value=mock_client):
        generate()

    assert mock_client.messages.create.call_args[1]["model"] == "claude-sonnet-4-20250514"
