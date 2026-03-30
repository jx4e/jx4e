import os
import requests
import anthropic


def fetch_commits(username: str, count: int = 30) -> list[dict]:
    """Fetch the last `count` commits authored by `username` via the Search API."""
    token = os.environ.get("GH_PAT") or os.environ.get("GITHUB_TOKEN")
    headers = {
        "Authorization": f"Bearer {token}",
        "Accept": "application/vnd.github+json",
    } if token else {}
    url = "https://api.github.com/search/commits"
    response = requests.get(url, params={
        "q": f"author:{username}",
        "sort": "author-date",
        "order": "desc",
        "per_page": count,
    }, headers=headers)
    response.raise_for_status()

    commits = []
    for item in response.json().get("items", []):
        commits.append({
            "message": item["commit"]["message"].splitlines()[0],  # first line only
            "repo": item["repository"]["full_name"],
        })
    return commits


def generate() -> str:
    """Fetch recent commits and return a Claude-generated roast as markdown."""
    username = os.environ.get("GITHUB_USERNAME", "jx4e")
    commits = fetch_commits(username)

    if not commits:
        return "_No recent commits to roast. I must be really lazy..._"

    commit_list = "\n".join(
        f"- [{c['repo']}] {c['message']}" for c in commits
    )

    client = anthropic.Anthropic()
    message = client.messages.create(
        model="claude-sonnet-4-20250514",
        max_tokens=256,
        messages=[
            {
                "role": "user",
                "content": (
                    "Here are my recent GitHub commit messages. Write 1-2 sentences brutally summarising "
                    "how bad my commit message hygiene is. Be blunt and specific — call out lazy messages "
                    "like 'fix', 'wip', 'update' by name if you see them. Plain text only, no markdown.\n\n"
                    f"Commits:\n{commit_list}"
                ),
            }
        ],
    )
    return message.content[0].text
