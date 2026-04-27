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


def test_events_loads():
    df = ic.events()
    expected = {
        "event_date",
        "event_type",
        "old_symbol",
        "new_symbol",
        "old_name",
        "new_name",
        "source_url",
        "notes",
    }
    assert expected <= set(df.columns)
    assert "index" not in df.columns
    assert len(df) > 0
    assert pd.api.types.is_datetime64_any_dtype(df["event_date"])
    assert set(df["event_type"]) <= {"ticker_change", "name_change", "merger"}


def test_events_filter_by_index():
    sp = ic.events("sp500")
    assert len(sp) > 0
    sp_symbols = set(ic.history("sp500")["symbol"])
    for _, row in sp.iterrows():
        assert row["old_symbol"] in sp_symbols or row["new_symbol"] in sp_symbols


def test_events_unknown_index():
    with pytest.raises(ValueError):
        ic.events("dax")


def test_fb_to_meta_canonicalization():
    sp_history = ic.history("sp500")
    assert "FB" not in set(sp_history["symbol"])
    assert "META" in set(sp_history["symbol"])

    members_2020 = ic.constituents_at("sp500", "2020-01-02")
    assert "META" in set(members_2020["symbol"])

    # Old ticker is not auto-resolved.
    assert ic.is_member("sp500", "FB", "2020-01-02") is False
    assert ic.is_member("sp500", "META", "2020-01-02") is True

    sp_events = ic.events("sp500")
    fb_to_meta = sp_events[
        (sp_events["event_type"] == "ticker_change")
        & (sp_events["old_symbol"] == "FB")
        & (sp_events["new_symbol"] == "META")
    ]
    assert len(fb_to_meta) == 1


def test_cn_merger_events():
    csi300_events = ic.events("csi300")
    # CNR (SH601299) merged into CRRC (SH601766) on 2015-06-01.
    cnr = csi300_events[
        (csi300_events["event_type"] == "merger")
        & (csi300_events["old_symbol"] == "SH601299")
        & (csi300_events["new_symbol"] == "SH601766")
    ]
    assert len(cnr) == 1

    # China Merchants Property (SZ000024) absorbed by China Merchants Shekou
    # (SZ001979) on 2015-12-30.
    cmsk = csi300_events[
        (csi300_events["event_type"] == "merger")
        & (csi300_events["old_symbol"] == "SZ000024")
        & (csi300_events["new_symbol"] == "SZ001979")
    ]
    assert len(cmsk) == 1
