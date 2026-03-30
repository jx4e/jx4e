import anthropic
from datetime import date


def generate() -> str:
    """Generate a daily greeting with emojis based on today's date."""
    today = date.today()
    day_name = today.strftime("%A")

    client = anthropic.Anthropic()
    message = client.messages.create(
        model="claude-sonnet-4-20250514",
        max_tokens=128,
        messages=[
            {
                "role": "user",
                "content": (
                    f"Today is {today} ({day_name}). "
                    "Write a single short, fun greeting for a developer's GitHub profile. "
                    "Make it feel relevant to the day of the week. Include 1-3 emojis. "
                    "Return only the greeting line, nothing else."
                ),
            }
        ],
    )
    return message.content[0].text
