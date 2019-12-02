import datetime
import time

from Stock import *
from preprocess import getStockCodeAndName

"""
    设计两种股票排序逻辑：
    1.	根据股价指标MACD（平滑异同移动平均线）计算排名；
    2.	根据个股财务统计数据中的ROE（加权平均净资产收益率）进行排名。
    @Author: zengshuang61@gmail.com
"""


def sortDictByValueDesc(dict):
    return sorted(dict.items(), key=lambda d: d[1], reverse=True)


def printProcess(c, total, interval, DoneInfo='Done!'):
    """
        输出进度和百分比
    :param c: 当前完成任务数
    :param total: 总任务数
    :param interval: 已消耗的时间
    :param DoneInfo: 完成后的提示
    :return:
    """
    per = int(c / total * 100)
    k = per + 1
    s = '>' * (per // 2) + '-' * ((100 - k) // 2)
    print('\r{}[{}%---{}/{}]\ttime:{}.'.format(s, per, c, total, interval), end='')
    if per == 100:
        print('\n{}'.format(DoneInfo))


def sortStockByMACD(dict_stocks):
    """
        获取每支股票的MACD指标（按天），计算大于0的天数占总天数的百分比，然后降序排列
    :param dict_stocks:
    :return:
    """
    stock_code_list = dict_stocks['code']
    stock_name_list = dict_stocks['name']
    stock_industry_list = dict_stocks['industry']
    # MACD指标对比方案：计算每支股票MACD为0以上的天数占比，然后存入数组，供后面需要
    MACD_in_percent_dict = {}
    total = len(stock_code_list)
    c = 0
    start = datetime.datetime.now()
    print('MACD排序进行中')
    for i in range(len(stock_code_list)):
        code = stock_code_list[i]
        name = stock_name_list[i]
        industry = stock_industry_list[i]
        stock = Stock(stock_code=code, stock_name=name, stock_industry=industry)
        macd = stock.MACD()['macd']
        count = macd.count()
        percentage = macd[macd >= 0].count() / count
        MACD_in_percent_dict[code] = percentage
        c += 1
        # 输出进度
        printProcess(c, total, datetime.datetime.now() - start, 'MACD sort Done!')
    return sortDictByValueDesc(MACD_in_percent_dict)


def sortStockByROE():
    """
        根据东方财富网个股页面提供的每支股票的ROE百分比（加权净资产收益率）对股票进行排序
    :return:
    """
    path = 'data/stockInfo.txt'
    roe_dict = {}
    with open(path, 'r', encoding='utf-8') as f:
        lines = f.readlines()
        count = 0
        for line in lines:
            if count == 0:
                count += 1
                continue
            info = line.split('\t')
            if info[10].strip() == '-':
                continue
            roe_dict[info[1].strip()] = float(info[10].strip())
    return sortDictByValueDesc(roe_dict)


def saveFilteredStocks(sorted_stocks, Index='ROE', path='data/filtered_stocks', start=0, end=-1):
    """
        对排序后的股票进行筛选，去除带有*ST的股票，并保存到文件中
    :param sorted_stocks: 排序后的股票，格式：(code,index)，（股票，相应指数）
    :param Index: 指标类型
    :param path: 保存文件的路径
    :return:
    """
    print('{}指标开始筛选：'.format(Index))
    code2Name_dict, code2Industry_dict = stockCode2NameAndIndustry(dict_stocks)
    f = open('{}_{}.txt'.format(path, Index), 'w', encoding='utf-8')
    headers = ['代码', '名称', '行业', Index]
    for i in range(len(headers)):
        f.write("{0:<4}\t".format(headers[i], chr(12288)))
    length = len(sorted_stocks)
    count = 0
    c = 0
    startTime = datetime.datetime.now()
    for code, index in sorted_stocks[start:end]:
        name = code2Name_dict[code]
        industry = code2Industry_dict[code]
        c += 1
        if str(name).startswith('*ST'):
            continue
        f.write('\n{}\t{}\t{}\t{}'.format(code, name, industry, index))
        count += 1
        printProcess(c, end - start, datetime.datetime.now() - startTime, '排除*ST Done!')
        time.sleep(0.1)
    print('筛选后：{}支股票'.format(count))
    print('保存至文件：{}_{}.txt中'.format(path, Index))


def stockCode2NameAndIndustry(dict_stocks):
    stock_code_list = dict_stocks['code']
    stock_name_list = dict_stocks['name']
    stock_industry_list = dict_stocks['industry']
    code2Name_dict = {}
    code2Industry_dict = {}
    for i in range(len(stock_code_list)):
        code = stock_code_list[i]
        name = stock_name_list[i]
        industry = stock_industry_list[i]
        code2Name_dict[code] = name
        code2Industry_dict[code] = industry
    return code2Name_dict, code2Industry_dict


if __name__ == '__main__':
    # 对A股3520家上市公司进行排名，
    dict_stocks = getStockCodeAndName()

    # 方法一：根据MACD
    # 可以通过修改start和end修改筛选出来的股票规模，这里是去掉刚上市几个月的公司
    sorted_stocks = sortStockByMACD(dict_stocks)
    saveFilteredStocks(sorted_stocks, Index='MACD', start=101, end=376)
    # 方法二：ROE
    sorted_stocks = sortStockByROE()
    saveFilteredStocks(sorted_stocks, start=6, end=276)
