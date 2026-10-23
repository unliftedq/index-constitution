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
    assert set(df["event_type"]) <= {"ticker_change", "name_change", "merger", "delisting"}


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

    # Baotou Aluminum was absorbed by Aluminum Corporation of China.
    baotou = csi300_events[
        (csi300_events["event_type"] == "merger")
        & (csi300_events["old_symbol"] == "SH600472")
        & (csi300_events["new_symbol"] == "SH601600")
    ]
    assert len(baotou) == 1

    csi500_events = ic.events("csi500")
    avic = csi500_events[
        (csi500_events["event_type"] == "merger")
        & (csi500_events["old_symbol"] == "SZ002013")
        & (csi500_events["new_symbol"] == "SH600372")
    ]
    assert len(avic) == 1


def test_cn_delisting_uses_exchange_date():
    status = ic.symbol_status("csi300", "SH600200")

    assert status["event_type"] == "delisting"
    assert status["event_date"] == pd.Timestamp("2025-12-31")


def test_cn_current_names_are_canonical():
    csi300 = ic.latest("csi300").set_index("symbol")
    csi500 = ic.latest("csi500").set_index("symbol")

    assert csi300.at["SH601006", "name"] == "大秦铁路"
    assert csi300.at["SH601211", "name"] == "国泰海通"
    assert csi500.at["SH688347", "name"] == "华虹宏力"


def test_us_merger_events():
    sp_events = ic.events("sp500")

    ace = sp_events[
        (sp_events["event_type"] == "delisting")
        & (sp_events["old_symbol"] == "ACE")
    ]
    assert len(ace) == 1
    row = ace.iloc[0]
    assert pd.isna(row["new_symbol"])
    assert pd.isna(row["new_name"])

    abmd = sp_events[
        (sp_events["event_type"] == "delisting")
        & (sp_events["old_symbol"] == "ABMD")
    ]
    assert len(abmd) == 1
    row = abmd.iloc[0]
    assert pd.isna(row["new_symbol"])
    assert pd.isna(row["new_name"])


def test_symbol_status_active_symbol():
    status = ic.symbol_status("sp500", "AAPL")

    assert status["found"] is True
    assert status["is_current"] is True
    assert status["resolved_symbol"] == "AAPL"
    assert status["reason"] == "active"


def test_symbol_status_merger_successors():
    ace = ic.symbol_status("sp500", "ACE")
    assert ace["found"] is True
    assert ace["is_current"] is False
    assert ace["resolved_symbol"] is None
    assert ace["resolved_name"] is None
    assert ace["event_type"] == "delisting"
    assert ace["reason"] == "delisted"



def test_symbol_status_delisted_symbol():
    abmd = ic.symbol_status("sp500", "ABMD")
    assert abmd["found"] is True
    assert abmd["is_current"] is False
    assert abmd["resolved_symbol"] is None
    assert abmd["resolved_name"] is None
    assert abmd["event_type"] == "delisting"
    assert abmd["reason"] == "delisted"


def test_symbol_status_unknown_symbol():
    status = ic.symbol_status("sp500", "NOTASYMBOL")

    assert status["found"] is False
    assert status["is_current"] is False
    assert status["resolved_symbol"] is None
    assert status["reason"] == "unknown"


def test_psky_to_skyd_canonicalization():
    history = ic.history("sp500").set_index("symbol")
    latest = ic.latest("sp500").set_index("symbol")

    assert "PSKY" not in history.index
    assert "PSKY" not in latest.index
    assert history.at["SKYD", "name"] == "Skydance Corporation"
    assert latest.at["SKYD", "opt-in"] == pd.Timestamp("1994-09-30")
    assert ic.is_member("sp500", "SKYD", "2026-10-05") is True
    assert ic.is_member("sp500", "PSKY", "2026-10-05") is False

    status = ic.symbol_status("sp500", "PSKY")
    assert status["resolved_symbol"] == "SKYD"
    assert status["resolved_name"] == "Skydance Corporation"
    assert status["event_type"] == "ticker_change"
    assert status["event_date"] == pd.Timestamp("2026-10-06")


@pytest.mark.parametrize(
    "index,removed,added,effective_date",
    [
        ("sp500", "AVB", "RDDT", "2026-08-18"),
        ("sp500", "TAP", "BE", "2026-09-21"),
        ("sp500", "TTD", "P", "2026-09-21"),
        ("sp500", "BLDR", "ILMN", "2026-09-21"),
        ("sp500", "WBD", "TWLO", "2026-10-06"),
        ("nasdaq100", "WBD", "MRNA", "2026-10-09"),
        ("csi300", "SH601059", "SZ002294", "2026-10-19"),
        ("csi500", "SH600363", "SZ301297", "2026-10-09"),
        ("csi500", "SH601198", "SH603083", "2026-10-19"),
    ],
)
def test_recent_membership_changes(index, removed, added, effective_date):
    effective = pd.Timestamp(effective_date)
    before = effective - pd.Timedelta(days=1)

    assert ic.is_member(index, removed, before) is True
    assert ic.is_member(index, removed, effective) is False
    assert ic.is_member(index, added, before) is False
    assert ic.is_member(index, added, effective) is True


def test_vylor_spinoff_temporary_membership():
    assert ic.is_member("sp500", "VYLR", "2026-09-30") is False
    assert ic.is_member("sp500", "VYLR", "2026-10-01") is True
    assert ic.is_member("sp500", "CTVA", "2026-10-05") is True
    assert ic.is_member("sp500", "CTVA", "2026-10-06") is False
    assert len(ic.constituents_at("sp500", "2026-10-01")) == 504
    assert len(ic.constituents_at("sp500", "2026-10-06")) == 503


@pytest.mark.parametrize("index", ["sp500", "nasdaq100"])
def test_wbd_retirement_is_not_an_index_removal_date(index):
    status = ic.symbol_status(index, "WBD")
    assert status["event_type"] == "delisting"
    assert status["event_date"] == pd.Timestamp("2026-10-06")
    assert status["resolved_symbol"] is None
    assert status["reason"] == "delisted"


def test_qorvo_retirement_preserves_historical_identity():
    status = ic.symbol_status("sp500", "QRVO")
    assert status["event_date"] == pd.Timestamp("2026-10-05")
    assert status["reason"] == "delisted"
    assert status["resolved_symbol"] is None
    assert ic.is_member("sp500", "QRVO", "2024-01-02") is True


def test_lianchuang_name_change_preserves_symbol():
    history = ic.history("csi500").set_index("symbol")
    assert history.at["SH600363", "name"] == "ST联光"
    events = ic.events("csi500")
    event = events.loc[
        (events["old_symbol"] == "SH600363")
        & (events["event_type"] == "name_change")
    ].iloc[0]
    assert event["event_date"] == pd.Timestamp("2026-09-30")
    assert event["new_name"] == "ST联光"
    assert pd.isna(event["new_symbol"])


@pytest.mark.parametrize(
    "index,count",
    [
        ("csi300", 300),
        ("csi500", 500),
        ("sp500", 503),
        ("nasdaq100", 102),
        ("dow30", 30),
    ],
)
def test_latest_matches_active_history(index, count):
    latest = ic.latest(index)
    active = ic.history(index).loc[lambda df: df["opt-out"].isna()]

    assert len(latest) == count
    assert latest["symbol"].is_unique
    assert active["symbol"].is_unique
    assert set(latest["symbol"]) == set(active["symbol"])


@pytest.mark.parametrize(
    "index,symbols",
    [
        ("sp500", ["SKYD", "RDDT", "BE", "P", "ILMN", "VYLR", "TWLO"]),
        ("nasdaq100", ["MRNA"]),
        ("csi300", ["SZ002294"]),
        ("csi500", ["SZ301297", "SH603083"]),
    ],
)
def test_updated_latest_rows_match_history(index, symbols):
    latest = ic.latest(index).loc[lambda df: df["symbol"].isin(symbols)]
    active = ic.history(index).loc[
        lambda df: df["symbol"].isin(symbols) & df["opt-out"].isna()
    ]

    assert set(latest["symbol"]) == set(symbols)
    columns = ["symbol", "name", "opt-in"]
    pd.testing.assert_frame_equal(
        latest[columns].sort_values("symbol").reset_index(drop=True),
        active[columns].sort_values("symbol").reset_index(drop=True),
    )
