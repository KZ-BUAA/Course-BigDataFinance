import copy

import pandas as pd
import numpy as np

stock = pd.read_excel('stock.xlsx')  # 股票列表

op = pd.read_excel('d.xlsx')  # 操作列表
op.sort_values(by='时间', inplace=True, ascending=True)
print(op)


def backtest(stock, op, step, init):
    """
    回测
    :param stock: 股票
    :param op: 操作
    :param step: 每次选几只股票
    :param init: 初始资金
    :return:
    """
    stock_list = []
    share_list = []
    date_list = []
    money = [init]

    tot = 0
    avg_money = init / step

    # 初始化 第一次买入
    for i in range(step):
        stock_name = op.loc[i, 'stock']
        date = op.loc[i, 'date']
        price = stock.loc[(stock['代码'] == stock_name) & (stock['时间'] == date)]['收盘价(元)'].iloc[0]

        stock_list.append(stock_name)
        share_list.append(avg_money / price)
        date_list.append(date)

    tot += step
    while tot < len(op):
        start = tot
        temp = copy.deepcopy(op[start:start + step])
        temp = temp.reset_index(drop=True)

        temp_money = 0
        date = temp.loc[0, 'date']

        for i in range(step):
            stock_name = stock_list[tot - step + i]
            price = stock.loc[(stock['代码'] == stock_name) & (stock['时间'] == date)]['收盘价(元)'].iloc[0]
            temp_money += price * share_list[tot - step + i]

        money.append(temp_money)
        avg_money = temp_money / step

        for i in range(step):
            stock_name = temp.loc[i, 'stock']
            price = stock.loc[(stock['代码'] == stock_name) & (stock['时间'] == date)]['收盘价(元)'].iloc[0]

            stock_list.append(stock_name)
            share_list.append(avg_money / price)
            date_list.append(date)

        tot += step

    close_date = sorted(stock['时间'])
    close_date = close_date[-1]
    temp_money = 0

    for i in range(step):
        stock_name = stock_list[tot - step + i]
        price = stock.loc[(stock['代码'] == stock_name) & (stock['时间'] == close_date)]['收盘价(元)'].iloc[0]
        temp_money += price * share_list[tot - step + i]

    money.append(temp_money)

    df = pd.DataFrame(list(zip(date_list, stock_list, share_list)), columns=['date', 'stock_name', 'buy'])
    return df, money, close_date

a,b = backtest(stock,op,1,1000)
print(a)
print(b)
