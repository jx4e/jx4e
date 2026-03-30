import os
import sys
import pytest
from unittest.mock import patch, MagicMock

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'scripts'))

from features.roast import fetch_commits, generate

MOCK_SEARCH_RESPONSE = {
    "items": [
        {
            "commit": {"message": "fix: broken thing\n\nmore details"},
            "repository": {"full_name": "jx4e/myrepo"},
        },
        {
            "commit": {"message": "wip: stuff"},
            "repository": {"full_name": "jx4e/myrepo"},
        },
    ]
}

EMPTY_SEARCH_RESPONSE = {"items": []}


def _mock_response(data):
    mock = MagicMock()
    mock.json.return_value = data
    mock.raise_for_status = MagicMock()
    return mock


def test_fetch_commits_returns_commits():
    with patch("features.roast.requests.get", return_value=_mock_response(MOCK_SEARCH_RESPONSE)):
        commits = fetch_commits("jx4e")
    assert len(commits) == 2
    assert commits[0] == {"message": "fix: broken thing", "repo": "jx4e/myrepo"}
    assert commits[1] == {"message": "wip: stuff", "repo": "jx4e/myrepo"}


def test_fetch_commits_uses_first_line_of_message():
    data = {"items": [{"commit": {"message": "feat: title\n\nbody text"}, "repository": {"full_name": "jx4e/repo"}}]}
    with patch("features.roast.requests.get", return_value=_mock_response(data)):
        commits = fetch_commits("jx4e")
    assert commits[0]["message"] == "feat: title"


def test_generate_returns_placeholder_when_no_commits():
    with patch("features.roast.requests.get", return_value=_mock_response(EMPTY_SEARCH_RESPONSE)):
        result = generate()
    assert "lazy" in result


def test_generate_calls_claude_and_returns_response():
    mock_claude_message = MagicMock()
    mock_claude_message.content = [MagicMock(text="## Roast\nYour commit messages are a cry for help.")]

    mock_client = MagicMock()
    mock_client.messages.create.return_value = mock_claude_message

    with patch("features.roast.requests.get", return_value=_mock_response(MOCK_SEARCH_RESPONSE)), \
         patch("features.roast.anthropic.Anthropic", return_value=mock_client):
        result = generate()

    assert result == "## Roast\nYour commit messages are a cry for help."
    mock_client.messages.create.assert_called_once()
    call_kwargs = mock_client.messages.create.call_args[1]
    assert call_kwargs["model"] == "claude-sonnet-4-20250514"


def test_generate_includes_commit_messages_in_prompt():
    mock_claude_message = MagicMock()
    mock_claude_message.content = [MagicMock(text="terrible")]

    mock_client = MagicMock()
    mock_client.messages.create.return_value = mock_claude_message

    with patch("features.roast.requests.get", return_value=_mock_response(MOCK_SEARCH_RESPONSE)), \
         patch("features.roast.anthropic.Anthropic", return_value=mock_client):
        generate()

    prompt = mock_client.messages.create.call_args[1]["messages"][0]["content"]
    assert "fix: broken thing" in prompt
    assert "wip: stuff" in prompt
