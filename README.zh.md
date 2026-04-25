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

## 使用场景

- 查询主要股指的当前成分股名单
- 还原任意时点的指数成分，用于量化回测
- 在训练量化模型时规避幸存者偏差
- 为后续扩展更多指数成分数据提供统一结构
