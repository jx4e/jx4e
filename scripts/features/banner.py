import anthropic
from datetime import datetime
from zoneinfo import ZoneInfo


def generate() -> str:
    """Ask Claude to generate a creative ASCII art banner for today."""
    today = datetime.now(ZoneInfo("America/Vancouver")).date()

    client = anthropic.Anthropic()
    message = client.messages.create(
        model="claude-sonnet-4-20250514",
        max_tokens=1024,
        messages=[{
            "role": "user",
            "content": (
                f"Today is {today}. Create a unique, creative ASCII art banner for a developer's GitHub profile. "
                "The banner should prominently feature 'jx4e' but you have complete creative freedom on the style — "
                "it could be a large figlet-style font, a box design, surrounded by a scene, geometric patterns, "
                "a themed design based on the time of year, or anything else creative. "
                "Make it different and interesting every day. "
                "Return only the ASCII art wrapped in a markdown code block (```). Nothing else."
            ),
        }],
    )
    return message.content[0].text
