# StockAnalysis Based On Dual Thrust Strategy
This project is to analyse the 3520 stocks of A shares.

> Environment: python 3.5.3

## 1. Install Required third-party Package
```commandline
    python3 -m pip install tushare //财经数据接口
    python3 -m pip install requests //简单爬虫
    python3 -m pip install BeautifulSoup //html页面解析 如果Python3下不行就下BeautifulSoup4这个包
    python3 -m pip install multiprocessing //单核多线程处理一些流程
    python3 -m pip install matplotlib  //画图分析
    python3 -m pip install pandas  //数据统计与处理
    python3 -m pip install stockstats  //通过股价源数据生成17种股价指标
    python3 -m pip install pyalgotrade    //策略分析接口python2.7版本
    python3 -m pip install pyalgotrade-python3    //策略分析接口python3版本
    python3 -m pip install slippage   //pyalgotrade依赖的库
    python3 -m pip install DataAPI   //暂时没有用到  今后做数据的精准评测可以用
```

## 2. Generate Data of stocks
- 股票代码，名称及所属行业（来源：tushare）
- 每支股票的三大财报数据（来源：网易财经个股财务报表）
- 每支股票近七年股价数据【供策略分析】（来源：tushare）
- 每支股票近三年的股价历史数据（来源：tushare）
- 每支股票的财务统计数据（来源：东方财富网个股页面）

```commandline
python3 preprocess.py
```

## 3.Sort Stocks

```commandline
python3 process.py
```

## 4.Metrics Analysis

```commandline
python3 Stock.py
```

## 5.DualThrust Strategy Analyze And backtest

```commandline
python3 DualTrustStrategy.py
```

> 通过PyAlgo官网教程提供的API进行Dual Thrust策略的实现并进行回测（backtest）

> 输入：第四步筛选出来的股票代码以及他们近7年的股价数据

> 输出：通过Dual Thrust策略进行回测得出每支股票的回测指标（包括夏普率、累计收益率、最大回撤比例、最长回撤周期、最终收益、交易次数占比等等）
