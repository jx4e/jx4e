import os
import sys
import pytest
from unittest.mock import patch, MagicMock

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'scripts'))

from features.roast import fetch_commits, generate

MOCK_EVENTS = [
    {
        "type": "PushEvent",
        "repo": {"name": "jx4e/myrepo"},
        "payload": {
            "commits": [
                {"message": "fix"},
                {"message": "wip: stuff"},
            ]
        }
    },
    {
        "type": "IssuesEvent",  # should be ignored
        "repo": {"name": "jx4e/myrepo"},
        "payload": {}
    }
]


def _mock_github_response(events):
    mock_response = MagicMock()
    mock_response.json.return_value = events
    mock_response.raise_for_status = MagicMock()
    return mock_response


def test_fetch_commits_extracts_push_events_only():
    with patch("features.roast.requests.get", return_value=_mock_github_response(MOCK_EVENTS)):
        commits = fetch_commits("jx4e")
    assert len(commits) == 2
    assert commits[0] == {"message": "fix", "repo": "jx4e/myrepo"}
    assert commits[1] == {"message": "wip: stuff", "repo": "jx4e/myrepo"}


def test_fetch_commits_respects_count_limit():
    many_events = [
        {
            "type": "PushEvent",
            "repo": {"name": "jx4e/repo"},
            "payload": {"commits": [{"message": f"commit {i}"} for i in range(20)]}
        }
        for _ in range(5)
    ]
    with patch("features.roast.requests.get", return_value=_mock_github_response(many_events)):
        commits = fetch_commits("jx4e", count=30)
    assert len(commits) == 30


def test_generate_returns_placeholder_when_no_commits():
    with patch("features.roast.requests.get", return_value=_mock_github_response([])):
        result = generate()
    assert "Suspiciously quiet" in result


def test_generate_calls_claude_and_returns_response():
    mock_claude_message = MagicMock()
    mock_claude_message.content = [MagicMock(text="## Roast\nYour commit messages are a cry for help.")]

    mock_client = MagicMock()
    mock_client.messages.create.return_value = mock_claude_message

    with patch("features.roast.requests.get", return_value=_mock_github_response(MOCK_EVENTS)), \
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

    with patch("features.roast.requests.get", return_value=_mock_github_response(MOCK_EVENTS)), \
         patch("features.roast.anthropic.Anthropic", return_value=mock_client):
        generate()

    prompt = mock_client.messages.create.call_args[1]["messages"][0]["content"]
    assert "fix" in prompt
    assert "wip: stuff" in prompt
