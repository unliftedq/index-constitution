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
    "REGIONS",
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
REGIONS: tuple[str, ...] = ("us", "cn")
_INDEX_REGION: dict[str, str] = {
    "csi300": "cn",
    "csi500": "cn",
    "sp500": "us",
    "nasdaq100": "us",
    "dow30": "us",
}

Flavor = Literal["latest", "history"]
Region = Literal["us", "cn"]
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


def events(
    index: str | None = None,
    region: Region | None = None,
) -> pd.DataFrame:
    """Return ticker/name change events.

    The returned DataFrame has columns ``event_date``, ``event_type``,
    ``old_symbol``, ``new_symbol``, ``old_name``, ``new_name``,
    ``source_url``, and ``notes``. ``event_date`` is parsed to
    ``datetime64[ns]``. ``event_type`` is one of ``"ticker_change"``,
    ``"name_change"``, or ``"merger"`` (used for absorption/share-swap
    mergers where the old symbol is delisted and shareholders receive
    shares of the surviving symbol).

    Events are stored per region (``"us"`` or ``"cn"``) without an
    ``index`` column because a corporate ticker or name change applies
    to every index that includes the company.

    - If ``region`` is given, only events for that region are returned.
    - If ``index`` is given, ``region`` defaults to that index's region
      and the result is further filtered to events whose ``old_symbol``
      or ``new_symbol`` ever appeared in that index's history.
    - If neither is given, events from all regions are concatenated and
      sorted by ``event_date``.

    Note: ``is_member`` and ``constituents_at`` do not automatically resolve
    old tickers via this table; consult ``events`` to map renamed symbols.
    """
    if region is not None and region not in REGIONS:
        raise ValueError(
            f"Unknown region {region!r}. Available: {', '.join(REGIONS)}"
        )
    if index is not None and index not in INDICES:
        raise ValueError(
            f"Unknown index {index!r}. Available: {', '.join(INDICES)}"
        )

    if index is not None and region is None:
        region = _INDEX_REGION[index]  # type: ignore[assignment]

    regions_to_load = (region,) if region is not None else REGIONS
    frames = [_load_events_pkl(r) for r in regions_to_load]
    df = (
        pd.concat(frames, ignore_index=True)
        .sort_values("event_date", kind="stable")
        .reset_index(drop=True)
    )

    if index is None:
        return df
    hist_symbols = set(history(index)["symbol"])
    mask = df["old_symbol"].isin(hist_symbols) | df["new_symbol"].isin(hist_symbols)
    return df.loc[mask].reset_index(drop=True)


def _load_events_pkl(region: str) -> pd.DataFrame:
    path = files(__package__).joinpath("_data", "event", f"{region}.pkl")
    with path.open("rb") as fh:
        return pd.read_pickle(fh)
