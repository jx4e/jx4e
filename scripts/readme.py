import re


def update_section(filepath: str, marker: str, content: str) -> None:
    """Replace content between <!-- MARKER_START --> and <!-- MARKER_END --> markers."""
    with open(filepath, 'r') as f:
        text = f.read()

    pattern = rf'(<!-- {re.escape(marker)}_START -->).*?(<!-- {re.escape(marker)}_END -->)'
    replacement = rf'\1\n{content}\n\2'

    new_text, count = re.subn(pattern, replacement, text, flags=re.DOTALL)
    if count == 0:
        raise ValueError(
            f"Markers <!-- {marker}_START --> and <!-- {marker}_END --> not found in {filepath}"
        )

    with open(filepath, 'w') as f:
        f.write(new_text)
