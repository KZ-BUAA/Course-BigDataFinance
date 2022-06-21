import sys

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from pylab import mpl


def form_ssd(data):
    """
    生成价差函数
    :param data: trans 生成的dataframe
    :return: 股票名称元组，有两个元素
    """
    data = data.cumprod()
    col = data.columns  # 取出列名
    name = []
    num = []

    for i in range(len(col)):
        for j in range(i + 1, len(col)):
            name.append(col[i] + ' ' + col[j])
            num.append(sum((data[col[i]] - data[col[j]]) ** 2))

    return dict(zip(name, num))


def form_pair(data_before, data, t_buy, t_sell, if_plot, num):
    """
    配对交易交易期函数，传入形成期数据、交易期数据等，返回 建仓、平仓、购买类型、股票名称四个列表
    :param data_before: df.pivot_table(index='date',columns='code',values='standard')  df为trans函数生成的dataframe  形成期数据
    :param data: df.pivot_table(index='date',columns='code',values='standard')  df为trans函数生成的dataframe  交易期数据
    :param t_buy: 建仓区间
    :param t_sell: 平仓区间
    :param if_plot: 是否绘制价格走势对比图
    :return: buy 建仓日期列表   sell 平仓日期列表   signal 购买类型 （+1为做空第一支股票、买入第二支股票，-1反之）   name 股票名称列表
    """
    ssd_dict = form_ssd(data_before)
    first = sorted(ssd_dict.items(), key=lambda x: x[1])[num][0].split()[0]
    second = sorted(ssd_dict.items(), key=lambda x: x[1])[num][0].split()[1]
    print(first)
    print(second)
    price = data[first] - data[second]
    name = (first, second)

    mu = np.mean(price)
    sigma = np.std(price)
    high_buy = mu + t_buy * sigma
    low_buy = mu - t_buy * sigma
    high_sell = mu + t_sell * sigma
    low_sell = mu - t_sell * sigma

    flag = 0

    buy = []
    sell = []
    signal = []

    '''
    for i in range(len(price)):
        if price[i] >= high_buy:
            if flag == 0:
                flag = 1
                continue
            elif flag == 1:
                buy.append(data.index[i])
                signal.append(flag)
                flag = 2
                continue

        if price[i] <= low_buy:
            if flag == 0:
                flag = -1
                continue
            elif flag == -1:
                buy.append(data.index[i])
                signal.append(flag)
                flag = -2
                continue

        if low_sell < price[i] < high_sell:
            if flag == 2 or flag == -2:
                sell.append(data.index[i])
                flag = 0

        if price[i] < mu - 3 * sigma or price[i] > mu + 3 * sigma:
            if flag == 2 or flag == -2:
                sell.append(data.index[i])
                flag = 0
    '''

    for i in range(len(price)):
        if price[i] >= high_buy:
            if flag == 0:
                flag = 1

                buy.append(data.index[i])
                signal.append(flag)
                # flag = 2
                continue

        if price[i] <= low_buy:
            if flag == 0:
                flag = -1

                buy.append(data.index[i])
                signal.append(flag)
                # flag = -2
                continue

        if low_sell < price[i] < high_sell:
            if flag == 1 or flag == -1:
                sell.append(data.index[i])
                flag = 0

        if price[i] < mu - 3 * sigma or price[i] > mu + 3 * sigma:
            if flag == 1 or flag == -1:
                sell.append(data.index[i])
                flag = 0

    if if_plot:
        mpl.rcParams['font.sans-serif'] = ['SimHei']
        mpl.rcParams['axes.unicode_minus'] = False
        plt.plot(price)

        plt.axhline(y=mu, color='black', label='均值')
        plt.axhline(y=mu + t_buy * sigma, color='purple', label='建仓条件')
        plt.axhline(y=mu - t_buy * sigma, color='purple')
        plt.axhline(y=mu + t_sell * sigma, color='yellow', label='平仓条件')
        plt.axhline(y=mu - t_sell * sigma, color='yellow')
        plt.title('形成期股票走势图(third)')
        plt.legend()
        plt.savefig('形成期价格走势图.jpg')
        plt.show()

    if len(buy) != len(sell):
        buy = buy[:-1]
        signal = signal[:-1]

    return buy, sell, signal, name


def back(stock, op, name_list, t_buy, t_sell, init_money):
    """
    回测函数
    :param stock: trans函数生成的dataframe
    :param op: 操作元组    元组中单个元素形为：(Timestamp('2020-06-17 00:00:00'), Timestamp('2020-06-19 00:00:00'), -1)
    :param name_list: 两只股票的元组
    :param t_buy: 建仓区间
    :param t_sell: 平仓区间
    :param init_money: 初始资金
    :return: 每次建仓平仓的收益
    """
    first = name_list[0]
    second = name_list[1]
    profit_list = []

    x_buy_list = []
    y_buy_list = []
    x_sell_list = []
    y_sell_list = []

    for i in range(len(op)):
        buy_date = op[i][0]
        sell_date = op[i][1]
        opt = op[i][2]

        first_buy = stock.loc[(stock['date'] == buy_date) & (stock['code'] == first)]['price'].iloc[0]
        first_sell = stock.loc[(stock['date'] == sell_date) & (stock['code'] == first)]['price'].iloc[0]
        second_buy = stock.loc[(stock['date'] == buy_date) & (stock['code'] == second)]['price'].iloc[0]
        second_sell = stock.loc[(stock['date'] == sell_date) & (stock['code'] == second)]['price'].iloc[0]

        first_stock = init_money / first_buy
        second_stock = init_money / second_buy

        profit = - opt * (first_sell * first_stock) + opt * (second_sell * second_stock)
        profit_list.append(profit / init_money)

        x_buy_list.append(buy_date)
        y_buy_list.append(first_buy)
        x_buy_list.append(buy_date)
        y_buy_list.append(second_buy)
        x_sell_list.append(sell_date)
        y_sell_list.append(first_sell)
        x_sell_list.append(sell_date)
        y_sell_list.append(second_sell)

    plt.plot(stock['date'].unique(), stock.loc[stock['code'] == first]['price'], color='grey', label='股票1')
    plt.plot(stock['date'].unique(), stock.loc[stock['code'] == second]['price'], color='red', label='股票2')
    plt.scatter(x_buy_list, y_buy_list, s=10, c='blue', label='建仓点')  # stroke, colour
    plt.scatter(x_sell_list, y_sell_list, s=10, c='green', label='平仓点')

    mpl.rcParams['font.sans-serif'] = ['SimHei']
    mpl.rcParams['axes.unicode_minus'] = False

    plt.title('交易期两只股票价格走势图(third)')
    plt.legend()
    plt.savefig('价格走势图.jpg')
    plt.show()

    s = stock.pivot_table(index='date', columns='code', values='standard')

    price = s[first] - s[second]
    plt.plot(price, color='grey')

    mu = np.mean(price)
    sigma = np.std(price)

    plt.axhline(y=mu, color='black', label='均值')
    plt.axhline(y=mu + t_buy * sigma, color='purple', label='建仓条件')
    plt.axhline(y=mu - t_buy * sigma, color='purple')
    plt.axhline(y=mu + t_sell * sigma, color='yellow', label='平仓条件')
    plt.axhline(y=mu - t_sell * sigma, color='yellow')

    plt.scatter(x_buy_list, [price.loc[i] for i in x_buy_list], s=8, c='blue', label='建仓点')
    plt.scatter(x_sell_list, [price.loc[i] for i in x_sell_list], s=8, c='green', label='平仓点')

    mpl.rcParams['font.sans-serif'] = ['SimHei']
    mpl.rcParams['axes.unicode_minus'] = False

    plt.title('交易期两只股票价差走势图(third)')
    plt.legend()
    plt.savefig('价差图.jpg')
    plt.show()

    return profit_list


def trade(form, trading, t_buy, t_sell, num):
    """
    将之前的所有函数打包调用
    :param form: trans 生成的dataframe
    :param trading: trans 生成的dataframe
    :param buy: 建仓区间
    :param sell: 平仓区间
    :return: 每次操作的收益
    """
    buy, sell, signal, name = form_pair(form.pivot_table(index='date', columns='code', values='standard'),
                                        trading.pivot_table(index='date', columns='code', values='standard'),
                                        t_buy,
                                        t_sell,
                                        True,
                                        num)
    trading_tuple = tuple(zip(buy, sell, signal))
    profit = back(trading, trading_tuple, name, t_buy, t_sell, 1000)
    return profit


def trans(df):
    """
    生成所需dataframe
    :param df: 初始股票数据
    :return: dataframe 所需股票数据
    """
    output = pd.DataFrame({
        'date': df['时间'],
        'code': df['代码'],
        'price': df['收盘价(元)'],
        'price_before': df['前收盘价(元)']
    })
    output['standard'] = 1 + (output['price'] - output['price_before']) / output['price_before']
    output['date'] = pd.to_datetime(output['date'])
    return output


pairing = pd.read_excel('20-21.xlsx')  # 形成期数据
pairing = trans(pairing)
trading = pd.read_excel('21-22.xlsx')  # 交易期数据
trading = trans(trading)

for i in range(10):
    final = trade(pairing, trading, 1.5, 0.2, i)
    print(final)
    print(sum(final))


