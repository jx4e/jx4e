import anthropic
from datetime import datetime
from zoneinfo import ZoneInfo


def generate() -> str:
    """Ask Claude to generate a creative ASCII art banner for today."""
    today = datetime.now(ZoneInfo("America/Vancouver")).date()

    client = anthropic.Anthropic()
    message = client.messages.create(
        model="claude-sonnet-4-20250514",
        max_tokens=2048,
        messages=[{
            "role": "user",
            "content": (
                f"Today is {today}. Create ASCII art for a developer's GitHub profile. "
                "It must include large bold block letters spelling 'jx4e' (use a different figlet-style font each day). "
                "Also include a small ASCII art scene or character alongside or below the letters — "
                "could be a tiny person at a computer, a robot, a rocket, a monster, a cat, anything fun and creative. "
                "No borders or boxes. No emojis (they break monospace alignment). ASCII characters only. "
                "Keep it under 20 lines tall. "
                "Return only the ASCII art wrapped in a markdown code block (```). Nothing else."
            ),
        }],
    )
    return message.content[0].text
