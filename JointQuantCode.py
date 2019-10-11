"""
    这里的代码是聚宽（JointQuant）量化分析平台上运行的策略回测代码，
    如需运行策略进行回测，请登录聚宽官网：https://www.joinquant.com/
    本例回测的股票代码为600230 沧州大化
    @Author: zengshuang61@gmail.com
"""


def initialize(context):
    g.security = get_index_stocks('000905.XSHG')
    set_universe(g.security)
    set_benchmark('600230.XSHG')
    set_commission(PerTrade(buy_cost=0.0003, sell_cost=0.0013, min_cost=5))


def handle_data(context, data):
    stocknum = 50
    security = g.security
    # 根据大盘指数进行止损
    his = attribute_history('600230.XSHG', 10, '1d', 'close')
    if ((1 - float(his['close'][-1] / his['close'][0])) >= 0.03):
        if len(context.portfolio.positions) > 0:
            for stock in list(context.portfolio.positions.keys()):
                order_target(stock, 0)
        return
    # 分配资金
    if len(context.portfolio.positions) < stocknum:
        Num = stocknum - len(context.portfolio.positions)
        Cash = context.portfolio.cash / Num
    else:
        Cash = context.portfolio.cash
    # Buy
    for stock in security:
        # 求出持有该股票的仓位，买入没有持仓并符合条件股票
        position = context.portfolio.positions[stock].amount
        if position < 100:
            hist = attribute_history(stock, 3, '1d', ('high', 'low', 'close', 'open'))
            HH = max(hist['high'][:-1])
            LC = min(hist['close'][:-1])
            HC = max(hist['close'][:-1])
            LL = min(hist['low'][:-1])
            Open = hist['open'][-1]
            # 使用第n-1日的收盘价作为当前价
            current_price = hist['close'][-1]
            Range = max((HH - LC), (HC - LL))
            K1 = 0.9
            BuyLine = Open + K1 * Range
            if current_price > BuyLine:  # and position < 100:
                order_value(stock, Cash)
    # Sell
    for stock in list(context.portfolio.positions.keys()):
        hist = history(3, '1d', 'close', [stock])
        case1 = (1 - (hist[stock][-1] / hist[stock][0])) >= 0.06
        case2 = (1 - (hist[stock][-2] / hist[stock][0])) >= 0.08
        if case1 or case2:
            order_target(stock, 0)
