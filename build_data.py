"""Convert top-level CSVs into pickled DataFrames embedded in the package.

Used both by the Hatch build hook (during ``uv build`` / ``pip install``) and
by the test suite (via ``conftest.py``) to materialize ``_data/*.pkl`` files
inside the installed package.
"""

from __future__ import annotations

from pathlib import Path

import pandas as pd

INDICES = ("csi300", "sp500", "nasdaq100")
FLAVORS = ("latest", "history")
PKL_PROTOCOL = 4  # readable by Python 3.4+


def _load_csv(csv_path: Path) -> pd.DataFrame:
    df = pd.read_csv(csv_path)
    for col in ("opt-in", "opt-out"):
        if col in df.columns:
            df[col] = pd.to_datetime(df[col], errors="coerce")
    return df


def build_pickles(project_root: Path, out_dir: Path) -> list[Path]:
    """Read CSVs from ``project_root/{flavor}/{index}.csv`` and write pickles
    to ``out_dir/{flavor}/{index}.pkl``. Returns the list of written paths.
    """
    written: list[Path] = []
    for flavor in FLAVORS:
        flavor_out = out_dir / flavor
        flavor_out.mkdir(parents=True, exist_ok=True)
        for index in INDICES:
            csv_path = project_root / flavor / f"{index}.csv"
            if not csv_path.exists():
                raise FileNotFoundError(f"Missing source CSV: {csv_path}")
            df = _load_csv(csv_path)
            pkl_path = flavor_out / f"{index}.pkl"
            df.to_pickle(pkl_path, protocol=PKL_PROTOCOL)
            written.append(pkl_path)
    return written


if __name__ == "__main__":
    root = Path(__file__).resolve().parent
    out = root / "src" / "index_constitution" / "_data"
    paths = build_pickles(root, out)
    for p in paths:
        print(p.relative_to(root))
