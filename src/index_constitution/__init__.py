"""Index Constitution: point-in-time constituents for major stock indices.

Embedded datasets:

- ``csi300``     — CSI 300 (Shanghai/Shenzhen)
- ``csi500``     — CSI 500 (Shanghai/Shenzhen)
- ``sp500``      — S&P 500
- ``nasdaq100``  — NASDAQ-100
- ``dow30``      — Dow Jones Industrial Average

Two flavors per index:

- ``latest``  — current members (columns: ``symbol``, ``name``, ``opt-in``)
- ``history`` — full history (columns: ``symbol``, ``name``, ``opt-in``,
  ``opt-out``; an empty ``opt-out`` means still a member)
"""

from __future__ import annotations

from datetime import date, datetime
from importlib.resources import files
from typing import Iterable, Literal, Union

import pandas as pd

__all__ = [
    "INDICES",
    "list_indices",
    "load",
    "latest",
    "history",
    "constituents_at",
    "is_member",
    "events",
    "__version__",
]

__version__ = "0.1.0"

INDICES: tuple[str, ...] = ("csi300", "csi500", "sp500", "nasdaq100", "dow30")

Flavor = Literal["latest", "history"]
DateLike = Union[str, date, datetime, pd.Timestamp]


def list_indices() -> list[str]:
    """Return the names of all embedded indices."""
    return list(INDICES)


def _resource_path(flavor: Flavor, index: str):
    if index not in INDICES:
        raise ValueError(
            f"Unknown index {index!r}. Available: {', '.join(INDICES)}"
        )
    if flavor not in ("latest", "history"):
        raise ValueError(f"flavor must be 'latest' or 'history', got {flavor!r}")
    return files(__package__).joinpath("_data", flavor, f"{index}.pkl")


def load(index: str, flavor: Flavor = "latest") -> pd.DataFrame:
    """Load an embedded dataset as a pandas DataFrame.

    Data is stored as pickled DataFrames for fast load times; date columns
    are already parsed to ``datetime64[ns]``.
    """
    path = _resource_path(flavor, index)
    with path.open("rb") as fh:
        return pd.read_pickle(fh)


def latest(index: str) -> pd.DataFrame:
    """Shortcut for ``load(index, 'latest')``."""
    return load(index, "latest")


def history(index: str) -> pd.DataFrame:
    """Shortcut for ``load(index, 'history')``."""
    return load(index, "history")


def constituents_at(index: str, when: DateLike) -> pd.DataFrame:
    """Return constituents that were members of ``index`` on date ``when``.

    A row qualifies if ``opt-in <= when`` and (``opt-out`` is missing
    or ``opt-out > when``).
    """
    ts = pd.Timestamp(when).normalize()
    df = history(index)
    opt_in = df["opt-in"]
    opt_out = df["opt-out"]
    mask = (opt_in <= ts) & (opt_out.isna() | (opt_out > ts))
    return df.loc[mask].reset_index(drop=True)


def is_member(index: str, symbol: str, when: DateLike) -> bool:
    """Return True if ``symbol`` was a constituent of ``index`` on ``when``."""
    members = constituents_at(index, when)
    return bool((members["symbol"] == symbol).any())


def events(index: str | None = None) -> pd.DataFrame:
    """Return ticker/name change events.

    The returned DataFrame has columns ``event_date``, ``event_type``,
    ``old_symbol``, ``new_symbol``, ``old_name``, ``new_name``,
    ``source_url``, and ``notes``. ``event_date`` is parsed to
    ``datetime64[ns]``. ``event_type`` is one of ``"ticker_change"`` or
    ``"name_change"``.

    Events are stored without an ``index`` column because a corporate ticker
    or name change applies to every index that includes the company. If
    ``index`` is provided, the result is filtered to events whose
    ``old_symbol`` or ``new_symbol`` ever appeared in that index's history.

    Note: ``is_member`` and ``constituents_at`` do not automatically resolve
    old tickers via this table; consult ``events`` to map renamed symbols.
    """
    path = files(__package__).joinpath("_data", "events.pkl")
    with path.open("rb") as fh:
        df = pd.read_pickle(fh)
    if index is None:
        return df
    hist_symbols = set(history(index)["symbol"])
    mask = df["old_symbol"].isin(hist_symbols) | df["new_symbol"].isin(hist_symbols)
    return df.loc[mask].reset_index(drop=True)
