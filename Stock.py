import os

import matplotlib.pyplot as plt
import pandas
import stockstats

"""
    股票处理类
    功能：
        1.获取股票的历史行情数据
        2.计算17种股价指标
        3.通过matplotlib绘制图像，便于对某支股票进行分析
    @Author: zengshuang61@gmail.com
"""

class Stock(object):
    def __init__(self, stock_code, stock_name='', stock_industry='', start_time=None, end_time=None):
        """
            Stock类的构造方法
        :param stock_code: 股票代码
        :param stock_name: 股票名称
        :param stock_industry: 股票所属行业
        :param start_time: 要分析的时间区间，开始时间
        :param end_time: 结束时间
        """
        self.code = stock_code
        self.name = stock_name
        self.industry = stock_industry
        filename = '{}.csv'.format(stock_code)
        self.price_path = os.path.join('data/share_price_processed/', filename)
        self.hist_price_path = os.path.join('data/share_price/', filename)
        self.lrb_season_path = os.path.join('data/lrb/season/', filename)
        self.lrb_year_path = os.path.join('data/lrb/year/', filename)
        self.xjllb_season_path = os.path.join('data/xjllb/season/', filename)
        self.xjllb_year_path = os.path.join('data/xjllb/year/', filename)
        self.zcfzb_season_path = os.path.join('data/zcfzb/season/', filename)
        self.zcfzb_year_path = os.path.join('data/zcfzb/year/', filename)

        # 输出当前处理的股票
        # self.print_stock()
        # 获取stockstats的统计类，此类用于计算各项股价指标,
        # https://github.com/jealous/stockstats
        self.stat = stockstats.StockDataFrame.retype(self.getHisPriceData(startTime=start_time, endTime=end_time))

    def print_stock(self):
        print('processing stock code : {} , stock name : {} , stock industry : {} . '.format(self.code, self.name,
                                                                                             self.industry))

    def getPriceData(self, startTime=None, endTime=None):
        """
            此方法得到的数据供Dual Thrust策略分析，是PyAlgo要求的数据结构，可以指定时间范围
        :param startTime:开始时间，默认是None
        :param endTime:结束时间，默认是None
        :return:
        """

        if not (startTime and endTime):
            # print('there is no startTime and endTime set.')
            price = pandas.read_csv(self.price_path)
            return price
        else:
            # TODO 通过时间筛选股价数据
            pass


    def getHisPriceData(self, startTime=None, endTime=None):
        """
            此方法用于计算个股的各项股价指标，采用tushare原始的csv数据结构
        :param startTime: 开始时间，默认是None
        :param endTime: 结束时间，默认是None
        :return:
        """

        if not (startTime and endTime):
            # print('there is no startTime and endTime set.')
            price = pandas.read_csv(self.hist_price_path)
            return price.sort_values(by='date')
        else:
            # TODO 通过时间筛选历史股价数据
            pass

    def pltShow(self, func, figsize=(13.50, 7.0), grid=True, subplots=True, **kw):
        func.plot(figsize=figsize, grid=grid, subplots=subplots, **kw)
        plt.show()

    """
        以下方法获为17种股价指标，通过stockstats库获取，分析时可以适当调整参数
        stockstats的github地址：https://github.com/jealous/stockstats
    """

    def volumDelta(self):
        """
            volume_delta交易量delta转换
        :return:
        """
        return self.stat[['volume', 'volume_delta']]

    def closeDelta(self):
        """
            close_delta 收盘价delta转换
        :return:
        """
        return self.stat[['close', 'close_delta']]

    def n_d(self):
        """
            计算n天差
        :return:
        """
        return self.stat[['close', 'close_1_d', 'close_2_d', 'close_-1_d', 'close_-2_d']]

    def n_openChangeInPercent(self):
        """
            计算n天开盘价百分比
        :return:
        """
        return self.stat[['close', 'close_-1_r', 'close_-2_r']]

    def CR(self):
        """
            计算CR指标，也就是价格动量指标，它能够大体反映出股价的压力带和支撑带，弥补AR、BR的不足
            文档：http://wiki.mbalib.com/wiki/CR%E6%8C%87%E6%A0%87
            分析要领：
        　　1. 运用CR指标应该综合其它技术指标共同分析。
        　　2. 当CR由下向上穿过"副地震带"时，股价会受到次级压力。反之，当CR从上向下穿过"副地震带"时，股价会受到次级支撑的压力。
        　　3. 当CR由下向上穿过"主地震带"时，股价会受到相对强大的压力；反之，当CR由上自下穿过"主地震带"时，股价会受到相对强大的支撑力。
        　　4. CR跌穿a、b、c、d四条线，再由低点向上爬升160时，为短线获利的一个良机，应适当卖出股票。
        　　5. CR跌至40以下时，是建仓良机。而CR高于300~400时，应注意适当减仓。
        :return:
        """
        return self.stat[['close', 'cr', 'cr-ma1', 'cr-ma2', 'cr-ma3']]

    def KDJ(self):
        """
            KDJ指标，也就是随机指标。
            文档：http://wiki.mbalib.com/wiki/%E9%9A%8F%E6%9C%BA%E6%8C%87%E6%A0%87
            它综合了动量观念、强弱指标及移动平均线的优点，用来度量股价脱离价格正常范围的变异程度。
            KDJ指标考虑的不仅是收盘价，而且有近期的最高价和最低价，这避免了仅考虑收盘价而忽视真正波动幅度的弱点。
        :return:
        """
        # three days KDJK cross up 3 days KDJD
        # stockStat['kdjk_3_xu_kdjd_3'].plot(figsize=(20,10), grid=True)
        # plt.show()
        # 分别是k d j 三个数据统计项。默认是统计9天
        return self.stat[['close', 'kdjk', 'kdjd', 'kdjj']]

    def SMA(self):
        """
            SMA指标，简单移动平均线（Simple Moving Average，SMA），又称“算术移动平均线”
            文档：http://wiki.mbalib.com/wiki/Sma

        :return:
        """
        return self.stat[['close', 'close_5_sma', 'close_10_sma']]

    def MACD(self):
        """
            MACD指标，平滑异同移动平均线(Moving Average Convergence Divergence，简称MACD指标)，也称移动平均聚散指标。
            文档：http://wiki.mbalib.com/wiki/MACD
            MACD技术分析，运用DIF线与MACD线之相交型态及直线棒高低点与背离现象，作为买卖讯号，尤其当市场股价走势呈一较为明确波段趋势时，
            MACD 则可发挥其应有的功能，但当市场呈牛皮盘整格局，股价不上不下时，MACD买卖讯号较不明显。
            当用MACD作分析时，亦可运用其他的技术分析指标如短期 K，D图形作为辅助工具，而且也可对买卖讯号作双重的确认。
            相关源码
                fast = df['close_12_ema']
                slow = df['close_26_ema']
                df['macd'] = fast - slow
                df['macds'] = df['macd_9_ema']
                df['macdh'] = (df['macd'] - df['macds'])
        :return:
        """
        return self.stat[['close', 'macd', 'macds', 'macdh']]

    def BOLL(self):
        """
            布林线指标(Bollinger Bands)
            文档：http://wiki.mbalib.com/wiki/BOLL
            1、当布林线开口向上后，只要股价K线始终运行在布林线的中轨上方的时候，说明股价一直处在一个中长期上升轨道之中，这是BOLL指标发出的持股待涨信号，如果TRIX指标也是发出持股信号时，这种信号更加准确。此时，投资者应坚决持股待涨。
            2、当布林线开口向下后，只要股价K线始终运行在布林线的中轨下方的时候，说明股价一直处在一个中长期下降轨道之中，这是BOLL指标发出的持币观望信号，如果TRIX指标也是发出持币信号时，这种信号更加准确。此时，投资者应坚决持币观望。
        :return:
        """
        # 包括向上和向下的band
        return self.stat[['close', 'boll', 'boll_ub', 'boll_lb']]

    def RSI(self):
        """
            相对强弱指标（Relative Strength Index，简称RSI），也称相对强弱指数、相对力度指数
            文档：http://wiki.mbalib.com/wiki/RSI

        :return:
        """
        return self.stat[['close', 'rsi_6', 'rsi_12']]

    def WR(self):
        """
            威廉指数（Williams%Rate）该指数是利用摆动点来度量市场的超买超卖现象
            文档：http://wiki.mbalib.com/wiki/%E5%A8%81%E5%BB%89%E6%8C%87%E6%A0%87
        :return:
        """
        return self.stat[['close', 'wr_10', 'wr_6']]

    def CCI(self):
        """
            顺势指标又叫CCI指标，其英文全称为“Commodity Channel Index”， 是由美国股市分析家唐纳德·蓝伯特（Donald Lambert）所创造的，是一种重点研判股价偏离度的股市分析工具。
            文档：http://wiki.mbalib.com/wiki/%E9%A1%BA%E5%8A%BF%E6%8C%87%E6%A0%87
        :return:
        """
        return self.stat[['close', 'cci', 'cci_20']]

    def ATR(self):
        """
            均幅指标（Average True Ranger,ATR），均幅指标（ATR）是取一定时间周期内的股价波动幅度的移动平均值，主要用于研判买卖时机。
            文档：http://wiki.mbalib.com/wiki/%E5%9D%87%E5%B9%85%E6%8C%87%E6%A0%87
            均幅指标无论是从下向上穿越移动平均线，还是从上向下穿越移动平均线时，都是一种研判信号
        :return:
        """
        return self.stat[['close', 'tr', 'atr']]

    def DMA(self):
        """
            DMA指标（Different of Moving Average）又叫平行线差指标，是目前股市分析技术指标中的一种中短期指标，它常用于大盘指数和个股的研判。
            文档：http://wiki.mbalib.com/wiki/DMA
        :return:
        """
        return self.stat[['close', 'dma']]

    def DMI_DI_DX_ADX_ADXR(self):
        """
            动向指数Directional Movement Index,DMI），http://wiki.mbalib.com/wiki/DMI
            平均趋向指标（Average Directional Indicator，简称ADX），http://wiki.mbalib.com/wiki/ADX
            平均方向指数评估（ADXR）实际是今日ADX与前面某一日的ADX的平均值。ADXR在高位与ADX同步下滑，可以增加对ADX已经调头的尽早确认
            文档：http://wiki.mbalib.com/wiki/%E5%B9%B3%E5%9D%87%E6%96%B9%E5%90%91%E6%8C%87%E6%95%B0%E8%AF%84%E4%BC%B0
            ADXR是ADX的附属产品，只能发出一种辅助和肯定的讯号，并非入市的指标，而只需同时配合动向指标(DMI)的趋势才可作出买卖策略。
            在应用时，应以ADX为主，ADXR为辅。
        :return:
        """
        return self.stat[['close', 'pdi', 'mdi', 'dx', 'adx', 'adxr']]

    def TRIX_MATRIX(self):
        """
            TRIX指标又叫三重指数平滑移动平均指标（Triple Exponentially Smoothed Average）
            文档：http://wiki.mbalib.com/wiki/TRIX
        :return:
        """
        return self.stat[['close', 'trix', 'trix_9_sma']]

    def VR_MAVR(self):
        """
            成交量比率（Volumn Ratio，VR）（简称VR），是一项通过分析股价上升日成交额（或成交量，下同）与股价下降日成交额比值， 从而掌握市场买卖气势的中期技术指标。
            文档：http://wiki.mbalib.com/wiki/%E6%88%90%E4%BA%A4%E9%87%8F%E6%AF%94%E7%8E%87
        :return:
        """
        return self.stat[['close', 'vr', 'vr_6_sma']]

        # TODO 根据股票的三大财报数据进行分析

        # TODO 分析财务报表数据


if __name__ == '__main__':
    # 测试
    # stock = Stock(stock_code='000001', stock_name='平安银行', stock_industry='')
    stock = Stock(stock_code='600230')

    # 1、volumDelta指标
    # stock.pltShow(stock.volumDelta(), subplots=False)

    # 2、closeDelta指标
    # stock.pltShow(stock.closeDelta())

    # 3、计算n天差
    # stock.pltShow(stock.n_d())hence

    # 4、计算n天开盘价百分比
    # stock.pltShow(stock.n_openChangeInPercent())

    # 5、CR指标
    # stock.pltShow(stock.CR())

    # 6、KDJ指标
    # stock.pltShow(stock.KDJ())

    # 7、SMA指标
    # stock.pltShow(stock.SMA())

    # 8、MACD指标
    stat = stock.MACD()
    stock.pltShow(stat)

    # 9、BOLL指标
    # stock.pltShow(stock.BOLL())

    # 10、RSI指标
    # stock.pltShow(stock.RSI())

    # 11、WR指标
    # stock.pltShow(stock.WR())

    # 12、CCI指标
    # stock.pltShow(stock.CCI())

    # 13、TR、ATR指标
    # stock.pltShow(stock.ATR())

    # 14、DMA指标
    # stock.pltShow(stock.DMA())

    # 15、DMI，+DI，-DI，DX，ADX，ADXR指标
    # stock.pltShow(stock.DMI_DI_DX_ADX_ADXR())

    # 16、TRIX，MATRIX指标
    # stock.pltShow(stock.TRIX_MATRIX())

    # 17、VR，MAVR指标
    # stock.pltShow((stock.VR_MAVR()))
    print('123')
