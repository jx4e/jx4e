import anthropic
import requests
import xml.etree.ElementTree as ET
import yfinance as yf

INDICES = [
    ("S&P 500", "^GSPC"),
    ("NASDAQ", "^IXIC"),
    ("Dow", "^DJI"),
    ("FTSE 100", "^FTSE"),
]

RSS_URL = "https://feeds.bbci.co.uk/news/business/rss.xml"


def fetch_prices() -> list[dict]:
    """Fetch current price and daily % change for each index."""
    rows = []
    for name, ticker in INDICES:
        info = yf.Ticker(ticker).fast_info
        price = info.last_price
        prev = info.previous_close
        change_pct = (price - prev) / prev * 100
        rows.append({"name": name, "price": price, "change_pct": change_pct})
    return rows


def fetch_headlines(count: int = 3) -> list[dict]:
    """Fetch top `count` headlines from Yahoo Finance RSS."""
    response = requests.get(RSS_URL)
    response.raise_for_status()
    root = ET.fromstring(response.content)
    items = root.findall(".//item")[:count]
    return [
        {"title": item.findtext("title", ""), "link": item.findtext("link", "")}
        for item in items
    ]


def generate_quip(prices: list[dict]) -> str:
    """Ask Claude for a funny one-liner based on today's market moves."""
    summary = ", ".join(
        f"{r['name']} {'up' if r['change_pct'] >= 0 else 'down'} {abs(r['change_pct']):.2f}%"
        for r in prices
    )
    client = anthropic.Anthropic()
    message = client.messages.create(
        model="claude-sonnet-4-20250514",
        max_tokens=100,
        messages=[{
            "role": "user",
            "content": (
                f"Today's market moves: {summary}. "
                "Write one short funny sentence about this for a developer's GitHub profile. "
                "Be witty, reference the actual numbers. Return only the sentence, no quotes."
            ),
        }],
    )
    return f"*{message.content[0].text}*"


def generate() -> str:
    """Return a markdown price table, funny quip, and headline list."""
    prices = fetch_prices()
    headlines = fetch_headlines()
    quip = generate_quip(prices)

    lines = [
        "| Index | Price | Day |",
        "|---|---|---|",
    ]
    for row in prices:
        indicator = "🟢" if row["change_pct"] >= 0 else "🔴"
        sign = "+" if row["change_pct"] >= 0 else ""
        lines.append(
            f"| {row['name']} | {row['price']:,.2f} | {indicator} {sign}{row['change_pct']:.2f}% |"
        )

    lines.append("")
    lines.append(quip)
    lines.append("")
    lines.append("**Latest headlines:**")
    for h in headlines:
        lines.append(f"- [{h['title']}]({h['link']})")

    return "\n".join(lines)
