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
                f"Today is {today}. Create ASCII art that makes 'jx4e' look visually impressive. "
                "Use a different large figlet-style font or block letter design each day — the letters should be big and bold. "
                "You can add a simple border or minimal decoration but keep the focus on the letters looking great. "
                "Rules: no emojis (they break monospace alignment), ASCII characters only, "
                "keep it under 12 lines tall, under 70 characters wide. "
                "Return only the ASCII art wrapped in a markdown code block (```). Nothing else."
            ),
        }],
    )
    return message.content[0].text
