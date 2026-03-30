import requests
import xml.etree.ElementTree as ET
import yfinance as yf

INDICES = [
    ("S&P 500", "^GSPC"),
    ("NASDAQ", "^IXIC"),
    ("Dow", "^DJI"),
    ("FTSE 100", "^FTSE"),
]

RSS_URL = "https://feeds.reuters.com/reuters/businessNews"


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


def generate() -> str:
    """Return a markdown price table and headline list."""
    prices = fetch_prices()
    headlines = fetch_headlines()

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
    lines.append("**Latest headlines:**")
    for h in headlines:
        lines.append(f"- [{h['title']}]({h['link']})")

    return "\n".join(lines)
