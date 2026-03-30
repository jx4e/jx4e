import os
import tempfile
import pytest

import sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'scripts'))

from readme import update_section


def _make_readme(content: str) -> str:
    f = tempfile.NamedTemporaryFile(mode='w', suffix='.md', delete=False)
    f.write(content)
    f.close()
    return f.name


def test_replaces_content_between_markers():
    path = _make_readme(
        "# Title\n<!-- ROAST_START -->\nold content\n<!-- ROAST_END -->\n## Footer\n"
    )
    try:
        update_section(path, "ROAST", "new roast content")
        with open(path) as f:
            result = f.read()
        assert "new roast content" in result
        assert "old content" not in result
        assert "# Title" in result
        assert "## Footer" in result
    finally:
        os.unlink(path)


def test_preserves_markers_in_output():
    path = _make_readme("<!-- ROAST_START -->\nold\n<!-- ROAST_END -->\n")
    try:
        update_section(path, "ROAST", "new")
        with open(path) as f:
            result = f.read()
        assert "<!-- ROAST_START -->" in result
        assert "<!-- ROAST_END -->" in result
    finally:
        os.unlink(path)


def test_raises_on_missing_markers():
    path = _make_readme("# Title\nNo markers here\n")
    try:
        with pytest.raises(ValueError, match="not found"):
            update_section(path, "ROAST", "content")
    finally:
        os.unlink(path)


def test_empty_content_clears_section():
    path = _make_readme("<!-- ROAST_START -->\nsome stuff\n<!-- ROAST_END -->\n")
    try:
        update_section(path, "ROAST", "")
        with open(path) as f:
            result = f.read()
        assert "some stuff" not in result
    finally:
        os.unlink(path)
