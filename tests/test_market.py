import os
import sys
from unittest.mock import patch, MagicMock

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'scripts'))

from features.market import fetch_prices, fetch_headlines, generate

MOCK_RSS = b"""<?xml version="1.0" encoding="UTF-8"?>
<rss><channel>
  <item><title>Fed signals rate cut pause</title><link>https://example.com/1</link></item>
  <item><title>UK inflation falls to 3.2%</title><link>https://example.com/2</link></item>
  <item><title>Tech earnings beat expectations</title><link>https://example.com/3</link></item>
  <item><title>Fourth headline ignored</title><link>https://example.com/4</link></item>
</channel></rss>"""


def _mock_ticker(last_price, previous_close):
    ticker = MagicMock()
    ticker.fast_info.last_price = last_price
    ticker.fast_info.previous_close = previous_close
    return ticker


def _mock_rss_response():
    mock = MagicMock()
    mock.content = MOCK_RSS
    mock.raise_for_status = MagicMock()
    return mock


def test_fetch_prices_returns_all_four_indices():
    with patch("features.market.yf.Ticker", return_value=_mock_ticker(5234.12, 5191.05)):
        prices = fetch_prices()
    assert len(prices) == 4
    assert prices[0]["name"] == "S&P 500"
    assert prices[1]["name"] == "NASDAQ"
    assert prices[2]["name"] == "Dow"
    assert prices[3]["name"] == "FTSE 100"


def test_fetch_prices_calculates_change_pct():
    with patch("features.market.yf.Ticker", return_value=_mock_ticker(5234.12, 5191.05)):
        prices = fetch_prices()
    expected = (5234.12 - 5191.05) / 5191.05 * 100
    assert abs(prices[0]["change_pct"] - expected) < 0.001


def test_fetch_headlines_returns_top_3_only():
    with patch("features.market.requests.get", return_value=_mock_rss_response()):
        headlines = fetch_headlines()
    assert len(headlines) == 3
    assert headlines[0] == {"title": "Fed signals rate cut pause", "link": "https://example.com/1"}
    assert headlines[2] == {"title": "Tech earnings beat expectations", "link": "https://example.com/3"}


def test_generate_contains_price_table_headers():
    with patch("features.market.yf.Ticker", return_value=_mock_ticker(5234.12, 5191.05)), \
         patch("features.market.requests.get", return_value=_mock_rss_response()):
        result = generate()
    assert "| Index | Price | Day |" in result
    assert "S&P 500" in result
    assert "FTSE 100" in result


def test_generate_uses_green_for_positive_change():
    with patch("features.market.yf.Ticker", return_value=_mock_ticker(5234.12, 5191.05)), \
         patch("features.market.requests.get", return_value=_mock_rss_response()):
        result = generate()
    assert "🟢" in result


def test_generate_uses_red_for_negative_change():
    with patch("features.market.yf.Ticker", return_value=_mock_ticker(5100.00, 5191.05)), \
         patch("features.market.requests.get", return_value=_mock_rss_response()):
        result = generate()
    assert "🔴" in result


def test_generate_contains_headlines():
    with patch("features.market.yf.Ticker", return_value=_mock_ticker(5234.12, 5191.05)), \
         patch("features.market.requests.get", return_value=_mock_rss_response()):
        result = generate()
    assert "**Latest headlines:**" in result
    assert "[Fed signals rate cut pause](https://example.com/1)" in result
