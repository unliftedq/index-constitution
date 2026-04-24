# Index Constitution

[中文](README.zh.md)

## Purpose

This repository was created to make it easier to train quantitative models on major stock indices. Reliable historical index composition data (constituent additions and removals over time) is notoriously hard to obtain — vendors often charge for it, official sources are scattered across PDFs and announcements, and free APIs rarely expose point-in-time membership. Without this data, backtests suffer from survivorship bias and lookahead bias.

This repo collects and normalizes that information into plain CSV files so it can be consumed directly by research and modeling pipelines.

## Datasets

| Index | Description | Source |
| --- | --- | --- |
| CSI 300 | Top 300 A-share stocks listed on the Shanghai and Shenzhen exchanges | Official announcements from China Securities Index Co. (csindex.com.cn) |
| S&P 500 | 500 leading large-cap U.S. companies listed on U.S. exchanges | [Wikipedia: List of S&P 500 companies](https://en.wikipedia.org/wiki/List_of_S%26P_500_companies) |
| NASDAQ-100 | 100 largest non-financial companies listed on the Nasdaq Stock Market | [Wikipedia: NASDAQ-100](https://en.wikipedia.org/wiki/Nasdaq-100) |

## Structure

```text
history/
    csi300.csv
    nasdaq100.csv
    sp500.csv
latest/
    csi300.csv
    nasdaq100.csv
    sp500.csv
```

## Use Cases

- Check the current constituents of an index
- Reconstruct point-in-time index membership for backtesting
- Avoid survivorship bias when training quantitative models
- Keep a consistent structure for adding more indices later