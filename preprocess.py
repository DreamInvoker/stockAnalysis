import datetime
import json
import os
import time
from multiprocessing.dummy import Pool

import requests
import tushare as ts
from bs4 import BeautifulSoup

"""
    用于获取股价历史行情数据、三大财报数据和财务统计数据
    @Author: zengshuang61@gmail.com
"""

def getHTMLText(url, code="utf-8"):
    try:
        r = requests.get(url)
        r.raise_for_status()
        r.encoding = code
        return r.text
    except:
        return ""

def getStockCodeAndName(file_name='data/stocks.json'):
    """
        获取3522支股票的code和name，这里包括所有沪深上市的公司。
        因为601990和601138无法从tushare下载股价数据，所以剔除之后剩余3520支股票
    """
    if not os.path.exists(file_name):
        json.dump({}, open(file_name, 'w', encoding='utf-8'))
    else:
        dic_stocks = json.load(open(file_name, 'r', encoding='utf-8'))
        return dic_stocks

    stocks = ts.get_stock_basics()

    stock_code_list = list(stocks.index)
    stock_names_list = list(stocks.name)
    stock_industry_list = list(stocks.industry)

    dic_stocks = dict(code=stock_code_list, name=stock_names_list, industry=stock_industry_list)

    with open(file_name, 'w', encoding='utf-8') as f:
        json.dump(dic_stocks, f, ensure_ascii=False)

    return dic_stocks


def get_zcfzb(stock_code, file_name, type):
    """
        通过爬取网易财经的数据获取某支股票的资产负债表文件
    :param stock_code:股票代码
    :param file_name:文件保存位置
    :param type:为空时按季度，为year按年度
    :return:
    """
    if os.path.exists(file_name):
        return None
    try:
        r = requests.get("http://quotes.money.163.com/service/zcfzb_" + stock_code + ".html?type=" + type)
        r.raise_for_status()
        with open(file_name, 'wb') as fd:
            for chunk in r.iter_content():
                fd.write(chunk)
        time.sleep(3)
    except:
        print(stock_code + "_________zcfzb____failed,type=" + type)


def get_lrb(stock_code, file_name, type):
    """
        通过爬取网易财经的数据获取某支股票的利润表文件
    :param stock_code:股票代码
    :param file_name:文件保存位置
    :param type:为空时按季度，为year按年度
    :return:
    """
    if os.path.exists(file_name):
        return None
    try:
        r = requests.get("http://quotes.money.163.com/service/lrb_" + stock_code + ".html?type=" + type)
        r.raise_for_status()
        with open(file_name, 'wb') as fd:
            for chunk in r.iter_content():
                fd.write(chunk)
        time.sleep(3)
    except:
        print(stock_code + "_________lrb____failed,type=" + type)


def get_xjllb(stock_code, file_name, type):
    """
        通过爬取网易财经的数据获取某支股票的现金流量表文件
    :param stock_code:股票代码
    :param file_name:文件保存位置
    :param type:为空时按季度，为year按年度
    :return:
    """
    if os.path.exists(file_name):
        return None
    try:
        r = requests.get("http://quotes.money.163.com/service/xjllb_" + stock_code + ".html?type=" + type)
        r.raise_for_status()
        with open(file_name, 'wb') as fd:
            for chunk in r.iter_content():
                fd.write(chunk)
        time.sleep(3)
    except:
        print(stock_code + "_________xjllb____failed,type=" + type)


def getFinanceData(code):
    """
        获取代码为code的股票的三大财报数据
    :param code: 股票代码
    :return:
    """
    zcfzb_path = 'data/zcfzb/'
    lrb_path = 'data/lrb/'
    xjllb_path = 'data/xjllb/'

    get_zcfzb(code, zcfzb_path + 'season/' + code + '.csv', '')
    get_lrb(code, lrb_path + 'season/' + code + '.csv', '')
    get_xjllb(code, xjllb_path + 'season/' + code + '.csv', '')
    get_zcfzb(code, zcfzb_path + 'year/' + code + '.csv', 'year')
    get_lrb(code, lrb_path + 'year/' + code + '.csv', 'year')
    get_xjllb(code, xjllb_path + 'year/' + code + '.csv', 'year')


def getFinanceDataOfCodes(code_list):
    """
        单核多线程下载财报数据
    :param code_list:股票代码列表
    :return:
    """
    pool = Pool(4)
    pool.map(getFinanceData, code_list)
    pool.close()
    pool.join()


def downloadSharePrice(code, years=7):
    """
        下载指定股票代码的历史股价数据到本地, 文件名为<code>.csv, 默认下载7年的数据
    :param code: 股票代码，例如000001
    :param years: 至今多少年的行情数据
    :return:
    """
    if years == 0:
        return
    # 存储路径，pyalgotrade处理的数据
    # save_path = os.path.join("data/share_price_processed/", "{}.csv".format(code))
    # 历史数据存储的路径
    save_path = os.path.join("data/share_price/", "{}.csv".format(code))
    # 判断之前是否下载过
    if os.path.exists(save_path):
        print("{} 已下载".format(code))
        return

    now = datetime.datetime.now()
    start_time = now - datetime.timedelta(days=years * 365)
    # start = start_time.strftime("%Y-%m-%d")
    start = "2011-05-31"
    end_time = "2018-05-28"
    try:
        print("{} 正在下载过去{}年的股价数据".format(code, years))
        # 注释掉的为pyalgotrade处理的数据
        # df = ts.get_k_data(code, start=start,end=end_time)
        # 下面的是tushare的历史股价数据，近三年的股价数据，因为tushare的get_hist_data接口只提供近三年的数据
        df = ts.get_hist_data(code, start=start, end=end_time)
        print("{} 下载完成".format(code))
    except:
        print("{} 下载失败".format(code))
        return

    if len(df) < 1:
        print("{} 下载失败".format(code))
        return

    # 新建Adj Close字段，生成pyalgotrade数据的时候用，当生成历史数据的时候需要将其注释掉
    # df["Adj Close"] = df.close

    # 下面两行用来获取历史数据
    df['code'] = code
    df.sort_index()

    # 将tushare下的数据的字段保存为pyalgotrade所要求的数据格式，生成pyalgotrade数据的时候用，当生成历史数据的时候需要将其注释掉
    # df.columns = ["Date", "Open", "Close", "High", "Low", "Volume", "code", "Adj Close"]

    # 将数据保存成本地csv文件，生成pyalgotrade用
    # df.to_csv(save_path, index=False)
    # 生成历史数据时用
    df.to_csv(save_path, index=True)


def downloadSharePriceOfCodes(code_list):
    """
        单核多线程下载股价数据
    :param code_list:股票代码列表
    :return:
    """
    pool = Pool(4)
    pool.map(downloadSharePrice, code_list)
    pool.close()
    pool.join()


def isExist(code, path="data/share_price/ "):
    """
        data/share_price_processed/或data/share_price/
    :param code:
    :param path:
    :return:
    """
    stock_path = os.path.join(path, "{}.csv".format(code))
    if not os.path.exists(stock_path):
        print("股票代码为：{} 的股价数据正在重新下载".format(code))
        downloadSharePrice(code)


def isExitOfCodes(code_list):
    pool = Pool(4)
    pool.map(isExist, code_list)
    pool.close()
    pool.join()


def mkdir(path):
    if not os.path.exists(path):
        os.mkdir(path)


def getStockInfo(lst, fpath):
    Listtitle = ['sz/sh', '代码', '名称', '总市值', '净资产', '净利润', '市盈率(%)', '市净率(%)', '毛利率(%)', '净利率(%)', 'ROE(%)']
    with open(fpath, 'w', encoding='utf-8') as f:
        for i in range(len(Listtitle)):
            f.write("{0:<11}\t".format(Listtitle[i], chr(12288)))
    count = 0
    for stock in lst:
        List = []
        url = 'http://quote.eastmoney.com/sz' + stock + ".html"
        html = getHTMLText(url, "GB2312")
        try:
            if html == "":
                url = 'http://quote.eastmoney.com/sh' + stock + ".html"
                html = getHTMLText(url, "GB2312")
                List.append('sh')
                if html == "":
                    continue
            else:
                List.append('sz')

            List.append(stock)
            soup = BeautifulSoup(html, 'html.parser')
            stock = soup.find('div', attrs={'class': 'cwzb'}).find_all('tbody')[0]
            name = stock.find_all('b')[0]
            List.append(name.text)
            keyList = stock.find_all('td')[1:9]
            for i in range(len(keyList)):
                List.append(keyList[i].text.split('%')[0])
            with open(fpath, 'a', encoding='utf-8') as f:
                f.write('\n')
                for i in range(len(List)):
                    f.write('{0:<10}\t'.format(List[i], chr(12288)))
            count = count + 1
            print("\r当前进度: {:.2f}%".format(count * 100 / len(lst)), end="")
        except:
            count = count + 1
            print("\r当前进度: {:.2f}%".format(count * 100 / len(lst)), end="")
            continue


if __name__ == '__main__':

    # 创建数据文件夹
    dir_list = ['data/lrb/season', 'data/lrb/year', 'data/xjllb/season', 'data/xjllb/year', 'data/zcfzb/season',
                'data/zcfzb/year', 'data/share_price_processed', 'data/share_price']
    for path in dir_list:
        if not os.path.exists(path):
            mkdir(path)

    # 获取3520支股票代码，名称及所属行业
    dict_stocks = getStockCodeAndName()
    stock_code_list = dict_stocks['code']
    print("一共{}支股票！".format(len(stock_code_list)))

    '''
    获取每支股票的三大财报数据（包括年度和季度）
    来源：网易财经
    下载时间：2018年5月16日—2018年5月17日
    年度财报截止日期：2017年12月31日
    季度财报截止日期：2018年3月31日
    '''
    getFinanceDataOfCodes(stock_code_list)

    '''
    获取每支股票最近7年的股价数据，或者注释掉一些代码获取近三年内的历史数据【2018.6月10日新增】
    来源：tushare
    下载时间：2018年5月29日
    股价时间跨度：2011年5月31日—2018年5月28日
    '''
    downloadSharePriceOfCodes(stock_code_list)
    # 查看哪些股票的股价数据没有被下载，并重新下载
    isExitOfCodes(stock_code_list)

    '''
    获取每支股票的财务统计数据，包括代码、名称、总市值、净资产、净利润、市盈率(%)、市净率(%)、毛利率(%)、净利率(%)、ROE(%)
    来源：东方财富网个股页面
    '''
    getStockInfo(stock_code_list, 'data/stockInfo.txt')
