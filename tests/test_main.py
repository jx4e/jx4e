import os
import sys
import tempfile
import pytest
from unittest.mock import patch

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'scripts'))


def _make_readme(content: str) -> str:
    f = tempfile.NamedTemporaryFile(mode='w', suffix='.md', delete=False)
    f.write(content)
    f.close()
    return f.name


def test_main_injects_roast_into_readme():
    path = _make_readme("<!-- ROAST_START -->\n<!-- ROAST_END -->\n")
    try:
        with patch.dict(os.environ, {"README_PATH": path}), \
             patch("features.roast.generate", return_value="## Roast\nYou suck at naming."):
            import main
            import importlib
            importlib.reload(main)  # ensure env var is picked up fresh
            main.run()

        with open(path) as f:
            content = f.read()
        assert "You suck at naming." in content
        assert "<!-- ROAST_START -->" in content
        assert "<!-- ROAST_END -->" in content
    finally:
        os.unlink(path)
