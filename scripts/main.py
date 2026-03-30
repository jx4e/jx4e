import os
from features import banner
from features import roast
from features import greeting
from features import market
import readme

README_PATH = os.environ.get("README_PATH", "README.md")

FEATURES = [
    ("BANNER", banner.generate),
    ("GREETING", greeting.generate),
    ("MARKET", market.generate),
    ("ROAST", roast.generate),
]


def run() -> None:
    for marker, generate_fn in FEATURES:
        content = generate_fn()
        readme.update_section(README_PATH, marker, content)


if __name__ == "__main__":
    run()
