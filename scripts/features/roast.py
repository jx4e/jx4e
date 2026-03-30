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
