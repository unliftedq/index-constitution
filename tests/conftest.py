"""Ensure embedded pickles exist before tests run (covers editable installs)."""

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from build_data import build_pickles  # noqa: E402

build_pickles(ROOT, ROOT / "src" / "index_constitution" / "_data")
