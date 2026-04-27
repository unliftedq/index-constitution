# Index Constitution

[English](README.md)

## 项目目的

本仓库的初衷是为训练量化模型提供方便、可靠的指数成分股数据。可靠的指数历史仓位（即各时点的成分纳入与剔除记录）通常很难获取——商业数据厂商往往收费昂贵，官方来源分散在各类 PDF 和公告中，免费 API 也极少提供按时点回溯的成分股名单。缺少这类数据，量化回测就容易受到幸存者偏差和前视偏差的影响。

本仓库将这些信息整理为统一格式的 CSV 文件，方便研究和建模流程直接使用。

## 数据说明

| 指数 | 说明 | 来源 |
| --- | --- | --- |
| 沪深 300 | 沪深两市规模最大、流动性最好的 300 只 A 股 | 中证指数有限公司官方公告（csindex.com.cn） |
| 中证 500 | 沪深两市中盘 A 股代表性 500 只样本股 | 中证指数有限公司官方公告（csindex.com.cn） |
| 标普 500 | 美股市场 500 家大型上市公司 | [维基百科：List of S&P 500 companies](https://en.wikipedia.org/wiki/List_of_S%26P_500_companies) |
| 纳斯达克 100 | 纳斯达克交易所 100 家最大的非金融上市公司 | [维基百科：NASDAQ-100](https://en.wikipedia.org/wiki/Nasdaq-100) |
| 道琼斯工业平均指数 | 道琼斯工业平均指数中的 30 家美国蓝筹公司 | [维基百科：Dow Jones Industrial Average](https://en.wikipedia.org/wiki/Dow_Jones_Industrial_Average) 与 [维基百科：Historical components of the Dow Jones Industrial Average](https://en.wikipedia.org/wiki/Historical_components_of_the_Dow_Jones_Industrial_Average) |

## Python 包

本仓库同时提供一个小型 Python 库，将 CSV 数据嵌入包中并以 pandas DataFrame 形式提供。

安装：

```bash
pip install index-constitution
```

使用：

```python
import index_constitution as ic

ic.list_indices()                    # ['csi300', 'csi500', 'sp500', 'nasdaq100', 'dow30']

ic.latest("sp500")                   # 当前标普 500 成分股
ic.latest("dow30")                   # 当前道琼斯 30 成分股
ic.history("csi300")                 # 完整的沪深 300 历史，含 opt-in / opt-out
ic.constituents_at("sp500", "2015-06-30")   # 任意时点成分股
ic.is_member("sp500", "AAPL", "2020-01-02") # True
ic.events("sp500")                   # 股票代码 / 名称变更审计记录
ic.symbol_status("sp500", "ABMD")   # 历史 symbol 今天是否还能直接使用
```

### 股票代码与公司名称变更

`history/*.csv` 与 `latest/*.csv` 在整个成分期跨度内统一使用各公司当前的规范代码与名称。例如，标普 500 的历史记录中 Meta Platforms 始终以 `META` 出现，即使其曾以 `FB` 交易。`event/us.csv` 与 `event/cn.csv` 是这些变更的审计记录。

这种规范化对纯代码变更、名称变更最有效。当事件行填写了 `new_symbol`时，表示本数据集将该新代码视为可继续查询历史的后继 ticker。例如`FB -> META` 表示在本数据集中可以用 `META` 取得该公司的完整历史。

`delisting` 则表示旧 ticker 已被废弃、不再可直接使用。这种情况下`new_symbol` 与 `new_name` 留空，因为本数据集不把任何其他 ticker 视为
它的直接后继。例如，`ABMD` 作为历史标普 500 成分是有效的，但该代码在Johnson & Johnson 收购 Abiomed 后已不再单独交易。

变更事件不局限于单一指数——某家公司的代码或名称变更会同时影响包含该公司的所有指数。`ic.events("sp500")` 会筛选出那些新旧代码曾出现在标普 500 历史中的事件。

`is_member()` 与 `constituents_at()` 采用严格匹配——不会自动解析旧代码。可使用 `ic.events("sp500")` 或 `ic.symbol_status()` 判断旧代码是否映射到仍可用的后继 ticker，或只是已经退市。

## 使用场景

- 查询主要股指的当前成分股名单
- 还原任意时点的指数成分，用于量化回测
- 在训练量化模型时规避幸存者偏差
- 为后续扩展更多指数成分数据提供统一结构
