# Index Constitution

[中文](README.zh.md)

## Purpose

This repository was created to make it easier to train quantitative models on major stock indices. Reliable historical index composition data (constituent additions and removals over time) is notoriously hard to obtain — vendors often charge for it, official sources are scattered across PDFs and announcements, and free APIs rarely expose point-in-time membership. Without this data, backtests suffer from survivorship bias and lookahead bias.

This repo collects and normalizes that information into plain CSV files so it can be consumed directly by research and modeling pipelines.

## Datasets

| Index | Description | Source |
| --- | --- | --- |
| CSI 300 | Top 300 A-share stocks listed on the Shanghai and Shenzhen exchanges | Official announcements from China Securities Index Co. (csindex.com.cn) |
| CSI 500 | 500 mid-cap A-share stocks listed on the Shanghai and Shenzhen exchanges | Official announcements from China Securities Index Co. (csindex.com.cn) |
| S&P 500 | 500 leading large-cap U.S. companies listed on U.S. exchanges | [Wikipedia: List of S&P 500 companies](https://en.wikipedia.org/wiki/List_of_S%26P_500_companies) |
| NASDAQ-100 | 100 largest non-financial companies listed on the Nasdaq Stock Market | [Wikipedia: NASDAQ-100](https://en.wikipedia.org/wiki/Nasdaq-100) |
| Dow Jones Industrial Average | 30 large U.S. blue-chip companies in the Dow Jones Industrial Average | [Wikipedia: Dow Jones Industrial Average](https://en.wikipedia.org/wiki/Dow_Jones_Industrial_Average) and [Wikipedia: Historical components of the Dow Jones Industrial Average](https://en.wikipedia.org/wiki/Historical_components_of_the_Dow_Jones_Industrial_Average) |

## Python package

This repo also ships a small Python library that embeds the CSVs and exposes
them as pandas DataFrames.

Install:

```bash
pip install index-constitution
```

Usage:

```python
import index_constitution as ic

ic.list_indices()                    # ['csi300', 'csi500', 'sp500', 'nasdaq100', 'dow30']

ic.latest("sp500")                   # current S&P 500 members
ic.latest("dow30")                   # current Dow 30 members
ic.history("csi300")                 # full CSI 300 history with opt-in/opt-out
ic.constituents_at("sp500", "2015-06-30")   # point-in-time membership
ic.is_member("sp500", "AAPL", "2020-01-02") # True
ic.events("sp500")                   # ticker/name change audit trail
```

### Ticker and name changes

`history/*.csv` and `latest/*.csv` use the current canonical ticker and name
for each company across the full membership span. For example, S&P 500 history
lists Meta Platforms only as `META`, even for the period when it traded as
`FB`. The `history/event.csv` file is the audit trail for those changes.

Events are not scoped to a single index — a corporate ticker or name change
applies to every index that includes the company. `ic.events("sp500")`
filters the table to events whose old or new symbol ever appeared in S&P 500
history.

`is_member()` and `constituents_at()` are strict — they do not resolve old
tickers automatically. Use `ic.events("sp500")` to map renamed symbols.

## Use Cases

- Check the current constituents of an index
- Reconstruct point-in-time index membership for backtesting
- Avoid survivorship bias when training quantitative models
- Keep a consistent structure for adding more indices later
