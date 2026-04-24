"""Hatch custom build hook: regenerate embedded pickle data from top-level CSVs."""

from __future__ import annotations

import sys
from pathlib import Path

from hatchling.builders.hooks.plugin.interface import BuildHookInterface


class PickleDataBuildHook(BuildHookInterface):
    PLUGIN_NAME = "pickle-data"

    def initialize(self, version: str, build_data: dict) -> None:  # noqa: D401
        root = Path(self.root)
        # Make build_data.py importable without polluting sys.path globally.
        sys.path.insert(0, str(root))
        try:
            from build_data import build_pickles  # type: ignore
        finally:
            sys.path.pop(0)

        out_dir = root / "src" / "index_constitution" / "_data"
        written = build_pickles(root, out_dir)

        # Force-include each generated pickle into the wheel under the package.
        force_include = build_data.setdefault("force_include", {})
        pkg_prefix = Path("index_constitution") / "_data"
        for pkl in written:
            rel = pkl.relative_to(out_dir)
            force_include[str(pkl)] = str(pkg_prefix / rel)
