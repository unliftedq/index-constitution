import pandas as pd
import pytest

import index_constitution as ic


@pytest.mark.parametrize("index", ic.INDICES)
def test_latest_loads(index):
    df = ic.latest(index)
    assert {"symbol", "name", "opt-in"} <= set(df.columns)
    assert len(df) > 0
    assert pd.api.types.is_datetime64_any_dtype(df["opt-in"])


@pytest.mark.parametrize("index", ic.INDICES)
def test_history_loads(index):
    df = ic.history(index)
    assert {"symbol", "name", "opt-in", "opt-out"} <= set(df.columns)
    assert len(df) > 0


def test_constituents_at_matches_latest_for_today():
    today = pd.Timestamp.today().normalize()
    hist_today = set(ic.constituents_at("sp500", today)["symbol"])
    latest_syms = set(ic.latest("sp500")["symbol"])
    # Latest should be a subset of those active "now" per history.
    assert latest_syms <= hist_today


def test_is_member_known_case():
    # Apple has been an S&P 500 member since 1982-11-30.
    assert ic.is_member("sp500", "AAPL", "2020-01-02") is True
    assert ic.is_member("sp500", "AAPL", "1980-01-01") is False


def test_unknown_index():
    with pytest.raises(ValueError):
        ic.load("dax")


def test_list_indices():
    assert set(ic.list_indices()) == set(ic.INDICES)
