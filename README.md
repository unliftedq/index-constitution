# Index Constitution

[中文](README.zh.md)

This repository stores constituent data and historical composition records for major stock indices.

At the moment, the dataset only includes the CSI 300 index. The structure is intended to support additional indices over time.

## Structure

```text
history/
    csi300.csv
latest/
    csi300.csv
```

## Current Dataset

- `latest/csi300.csv`: latest snapshot of CSI 300 constituents
- `history/csi300.csv`: historical additions and removals for CSI 300

## Use Cases

- Check the current constituents of an index
- Review historical index composition changes
- Keep a consistent structure for adding more indices later