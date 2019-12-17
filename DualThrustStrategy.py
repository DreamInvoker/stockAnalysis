import collections

import pandas as pd
from pyalgotrade import plotter
from pyalgotrade import strategy
from pyalgotrade import technical
from pyalgotrade.barfeed import yahoofeed
from pyalgotrade.broker import backtesting
from pyalgotrade.stratanalyzer import drawdown
from pyalgotrade.stratanalyzer import returns
from pyalgotrade.stratanalyzer import sharpe
from pyalgotrade.stratanalyzer import trades

from Stock import *
from preprocess import getStockCodeAndName
from process import stockCode2NameAndIndustry
from pandas.plotting import register_matplotlib_converters

register_matplotlib_converters()
"""
    通过PyAlgo官网教程提供的API进行策略的实现并进行回测（backtest）
    官方教程：http://gbeced.github.io/pyalgotrade/docs/v0.18/html/index.html
    Dual Thrust策略实现依据参考:
        https://xueqiu.com/5256769224/32429363
        https://www.joinquant.com/post/274
    @Author: zengshuang61@gmail.com 
"""


class CustomEventWindow(object):
    """
    来源:PyAlgo  官网关于策略实现的基类
    An EventWindow class is responsible for making calculation over a moving window of values.

    :param windowSize: The size of the window. Must be greater than 0.
    :type windowSize: int.

    .. note::
        This is a base class and should not be used directly.

    """

    def __init__(self, windowSize):
        assert (windowSize > 0)
        assert (isinstance(windowSize, int))
        self.__values = collections.deque([], windowSize)
        self.__windowSize = windowSize

    def onNewValue(self, dateTime, value):
        self.__values.append(value)

    def getValues(self):
        return self.__values

    def getWindowSize(self):
        """Returns the window size."""
        return self.__windowSize

    def windowFull(self):
        return len(self.__values) == self.__windowSize

    def getValue(self):
        """Override to calculate a value using the values in the window."""
        raise NotImplementedError()


class DualEventWindow(CustomEventWindow):
    def __init__(self, period):
        assert (period > 0)
        super(DualEventWindow, self).__init__(period)
        self.__value = None

    def _calculateTrueRange(self, value):
        ret = None
        values = self.getValues()
        HH = max([bar.getHigh() for bar in values])
        LC = min([bar.getClose() for bar in values])
        HC = max([bar.getClose() for bar in values])
        LL = min([bar.getLow() for bar in values])
        ret = max((HH - LC), (HC - LL))
        return ret

    def onNewValue(self, dateTime, value):
        super(DualEventWindow, self).onNewValue(dateTime, value)

        if self.windowFull():
            self.__value = self._calculateTrueRange(value)

    def getValue(self):
        return self.__value


class Dual(technical.EventBasedFilter):
    def __init__(self, bardataSeries, period=15, maxLen=None):
        super(Dual, self).__init__(bardataSeries, DualEventWindow(period), maxLen)


class MyStrategy(strategy.BacktestingStrategy):
    """
        实现Dual Thrust策略，继承自PyAlgo的回测策略基类
    """

    def __init__(self, feed, instrument):
        # 起始金额100万刀
        super(MyStrategy, self).__init__(feed, 1000000)
        self.__broker = self.getBroker()
        self.__broker.setCommission(backtesting.TradePercentage(0.0005))
        self.__instrument = instrument
        self.__position = None

        # 如果想用修正后的收盘价，也就是股票数据csv文件中的Adj Close这一列的数据，那么需要使用这一行配置
        # self.setUseAdjustedValues(True)
        self.__k = 0.08
        self.__bars = feed[self.__instrument]
        self.__dual = Dual(self.__bars)

    def onEnterCanceled(self, position):
        self.__position = None

    def onEnterOk(self, position):
        """
            输出入仓股票金额
        :param position:
        :return:
        """
        execInfo = position.getEntryOrder().getExecutionInfo()
        self.info("BUY at $%.2f" % (execInfo.getPrice()))
        pass

    def onExitOk(self, position):
        """
            输出出仓股票金额
        :param position:
        :return:
        """
        execInfo = position.getExitOrder().getExecutionInfo()
        self.info("SELL at $%.2f" % (execInfo.getPrice()))
        self.__position = None

    def onExitCanceled(self, position):
        self.__position.exitMarket()

    def onBars(self, bars):
        """
            实现Dual Thrust策略回测
        :param bars:
        :return:
        """
        account = self.getBroker().getCash()
        bar = bars[self.__instrument]
        if self.__position is None and self.__dual[-1] is not None:
            current_price = bar.getClose()
            open_price = bar.getOpen()
            buy_line = open_price + (self.__k * self.__dual[-1])

            one = bar.getPrice() * 100
            oneUnit = account // one
            if oneUnit > 0 and current_price > buy_line:
                self.__position = self.enterLong(self.__instrument, oneUnit * 100, True)
        elif self.__position is not None and not self.__position.exitActive() and self.__dual[-1] is not None:
            current_price = bar.getClose()
            open_price = bar.getOpen()
            sell_line = open_price - (self.__k * self.__dual[-1])

            one = bar.getPrice() * 100
            oneUnit = account // one
            if current_price < sell_line:
                # 如果剩余金额不够，则退市
                self.__position.exitMarket()


def runStrategy(code, csv_file, stdout=True):
    """
        策略回测
    :param code:    股票代码
    :param csv_file:    文件地址
    :param stdout: 是否控制台输出
    :return:
    """
    feed = yahoofeed.Feed()

    feed.addBarsFromCSV(code, csv_file)
    myStrategy = MyStrategy(feed, code)

    # 初始化三大分析工具：收益，回撤、交易及夏普比率（6月21日新增）
    """
       文档：http://gbeced.github.io/pyalgotrade/docs/v0.18/html/stratanalyzer.html
       这个文档提供很多回测指标，可以直接使用回调
    """
    returnsAnalyzer = returns.Returns()
    drawDownAnalyzer = drawdown.DrawDown()
    tradesAnalyzer = trades.Trades()
    sharpeRatioAnalyzer = sharpe.SharpeRatio()

    # 将分析工具加入策略中进行辅助分析
    myStrategy.attachAnalyzer(returnsAnalyzer)
    myStrategy.attachAnalyzer(drawDownAnalyzer)
    myStrategy.attachAnalyzer(tradesAnalyzer)
    myStrategy.attachAnalyzer(sharpeRatioAnalyzer)

    # 开始绘图
    plt = plotter.StrategyPlotter(myStrategy)
    plt.getOrCreateSubplot("returns").addDataSeries("Simple returns", returnsAnalyzer.getReturns())

    # 运行策略进行回测
    myStrategy.run()

    # 最终投资组合
    result = myStrategy.getResult()
    # 夏普比率
    """
    源码参数解释:
        riskFreeRate (int/float.) – The risk free rate per annum.可根据需求对这个值进行修改
        annualized (boolean.) – True if the sharpe ratio should be annualized.
    """
    # TODO 此处的参数为riskFreeRate,0.05是官方给出来的数值
    shareRatio = sharpeRatioAnalyzer.getSharpeRatio(0.05)
    # 累计收益率
    cumReturn = returnsAnalyzer.getCumulativeReturns()[-1] * 100
    # 最大回撤比例
    maxDrawdown = drawDownAnalyzer.getMaxDrawDown() * 100
    # 最长回撤周期
    longestDrawDownDuration = drawDownAnalyzer.getLongestDrawDownDuration()
    # 交易次数
    tradeCount = tradesAnalyzer.getCount()
    # 交易中盈利次数
    profitableCount = tradesAnalyzer.getProfitableCount()
    # 交易中亏损次数
    unprofitableCount = tradesAnalyzer.getUnprofitableCount()

    if stdout:
        print("最终投资组合值: $%.2f" % result)
        print("夏普率: %.2f" % shareRatio)
        print("累计收益率: %.2f %%" % cumReturn)
        print("最大回撤比例: %.2f %%" % maxDrawdown)
        print("最长回撤周期: %s" % longestDrawDownDuration)
        print("交易总次数: %d次" % tradeCount)
        print("交易中盈利次数: %d次" % profitableCount)
        print("交易中亏损次数: %d次" % unprofitableCount)
        plt.plot()

    return result, shareRatio, cumReturn, maxDrawdown, longestDrawDownDuration, tradeCount, profitableCount, unprofitableCount


def AnalyzeByDualThrust(path, Index='ROE'):
    """
        Dual Thrust策略流程方法，从我们排序后筛选出来的股票中，分别获取历史数据去feed这个strategy，并运行
    :param path:
    :param Index:
    :return:
    """
    code2Name_dict, code2Industry_dict = stockCode2NameAndIndustry(getStockCodeAndName())
    download_dir = "data/share_price_processed"
    result_dir = "result"
    result_path = "dual_thrust_{}.csv".format(Index)
    if not os.path.exists("result"):
        os.mkdir(result_dir)

    ret_dict = {
        "code": [],
        "startTime": [],
        "endTime": [],
        "result": [],
        "shareRatio": [],
        "cumReturn(%)": [],
        "maxDrawdown(%)": [],
        "longestDrawDownDuration": [],
        "tradeCount": [],
        "profitableCount": [],
        "unprofitableCount": []
    }
    code_lis = []
    with open(path, 'r', encoding='utf-8') as f:
        count = 0
        lines = f.readlines()
        for line in lines:
            if count == 0:
                count += 1
                continue
            info = line.split('\t')
            code_lis.append(info[0])
    for code in code_lis:
        try:
            newStock = Stock(stock_code=code, stock_name=code2Name_dict[code], stock_industry=code2Industry_dict[code])
        except KeyError:
            print('股票代码为 {} 已经退市，略过！'.format(code))
            continue
        csv_file = os.path.join(download_dir, "{}.csv".format(code))
        # 获取近7年历史数据，格式为PyAlgo要求的数据格式，可以在这里调整要获取的时间范围[startTime,endTime]
        df = newStock.getPriceData(startTime=None, endTime=None)
        # 也可以直接从csv文件中获取所有的历史数据（近7年内）
        # df = pd.read_csv(csv_file)
        startTime = df.Date.iloc[0]
        endTime = df.Date.iloc[-1]
        code = os.path.basename(csv_file)[:6]

        try:
            result, shareRatio, cumReturn, maxDrawdown, longestDrawDownDuration, tradeCount, profitableCount, unprofitableCount = runStrategy(
                code, csv_file)
        except:
            print('error {}!'.format(code))
            continue
        ret_dict["code"].append(code)
        ret_dict["startTime"].append(startTime)
        ret_dict["endTime"].append(endTime)
        ret_dict["result"].append(result)
        ret_dict["shareRatio"].append(shareRatio)
        ret_dict["cumReturn(%)"].append(cumReturn)
        ret_dict["maxDrawdown(%)"].append(maxDrawdown)
        ret_dict["longestDrawDownDuration"].append(str(longestDrawDownDuration).split('\t')[0])
        ret_dict["tradeCount"].append(tradeCount)
        ret_dict["profitableCount"].append(profitableCount)
        ret_dict["unprofitableCount"].append(unprofitableCount)

    result_path = os.path.join(result_dir, result_path)
    ret_df = pd.DataFrame(ret_dict)
    ret_df.to_csv(result_path, index=False, encoding='utf-8')


def testOneStock(code):
    download_path = "data/share_price_processed"
    csv_path = os.path.join(download_path, "{}.csv".format(code))
    code = os.path.basename(csv_path)[:6]
    csv_file = csv_path
    df = pd.read_csv(csv_file)
    startTime = df.Date.iloc[0]
    endTime = df.Date.iloc[-1]
    print(" 开始日期： %s" % startTime)
    runStrategy(code, csv_file, stdout=True)
    print("结束日期 %s" % endTime)


if __name__ == '__main__':
    # 根据MACD排序后的股票进行Dual Thrust策略分析，根据PyAlgo文档说明，起始资金为100万美元
    # AnalyzeByDualThrust('data/filtered_stocks_MACD.txt', Index='MACD')
    # 根据ROE排序后的股票进行Dual Thrust策略分析，根据PyAlgo文档说明，起始资金为100万美元
    # AnalyzeByDualThrust('data/filtered_stocks_ROE.txt')

    # 可以测试单个股票，起始资金为100万美元
    testOneStock('000599')
