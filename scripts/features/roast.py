import os
import requests
import anthropic


def fetch_commits(username: str, count: int = 30) -> list[dict]:
    """Fetch the last `count` commit messages from a user's GitHub events."""
    token = os.environ.get("GH_PAT") or os.environ.get("GITHUB_TOKEN")
    headers = {"Authorization": f"Bearer {token}"} if token else {}
    # GH_PAT (user PAT) required to see private repo events.
    # GITHUB_TOKEN fallback only sees public events.
    url = f"https://api.github.com/users/{username}/events"
    response = requests.get(url, params={"per_page": 100}, headers=headers)
    response.raise_for_status()

    events = response.json()
    event_types = [e["type"] for e in events]
    print(f"[debug] total events: {len(events)}")
    print(f"[debug] event types: {event_types[:20]}")
    for e in events[:3]:
        print(f"[debug] payload keys: {list(e['payload'].keys())}, commits: {e['payload'].get('commits')}")

    commits = []
    for event in events:
        if event["type"] != "PushEvent":
            continue
        repo = event["repo"]["name"]
        for commit in event["payload"].get("commits", []):
            commits.append({"message": commit["message"], "repo": repo})
            if len(commits) >= count:
                return commits
    return commits


def generate() -> str:
    """Fetch recent commits and return a Claude-generated roast as markdown."""
    username = os.environ.get("GITHUB_USERNAME", "jx4e")
    commits = fetch_commits(username)

    if not commits:
        return "_No recent commits to roast. Suspiciously quiet..._"

    commit_list = "\n".join(
        f"- [{c['repo']}] {c['message']}" for c in commits
    )

    client = anthropic.Anthropic()
    message = client.messages.create(
        model="claude-sonnet-4-20250514",
        max_tokens=1024,
        messages=[
            {
                "role": "user",
                "content": (
                    "Here are my recent GitHub commit messages. Please roast them.\n\n"
                    "Rate the overall commit message quality out of 10. Call out the lazy ones "
                    "(single words like 'fix', 'wip', 'update', 'stuff', 'changes'). "
                    "Write a short snarky summary of my commit hygiene. "
                    "Format the output as markdown with a header, ratings, and a summary section.\n\n"
                    f"Commits:\n{commit_list}"
                ),
            }
        ],
    )
    return message.content[0].text
