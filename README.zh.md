# Index Constitution

[English](README.md)

这个仓库用于维护主要股指的成分股数据及其历史构成记录。

当前仓库中的数据仍以沪深 300 为主，后续可继续扩展到更多指数。

## 目录结构

```text
history/
    csi300.csv
latest/
    csi300.csv
```

## 当前数据

- `latest/csi300.csv`：沪深 300 当前成分股快照
- `history/csi300.csv`：沪深 300 历史纳入与剔除记录

## 使用场景

- 查询主要股指的当前成分股名单
- 回溯指数成分调整历史
- 为后续扩展更多指数成分数据提供统一结构