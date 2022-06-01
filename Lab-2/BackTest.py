import copy

import pandas as pd
import numpy as np
from matplotlib import pyplot as plt
from pylab import mpl

stock = pd.read_excel('stock.xlsx')  # 股票列表
stock['代码'] = stock['代码'].apply(lambda x: str(x))
stock['时间'] = pd.to_datetime(stock['时间'])


def backtest(stock, op, step, init):
    """
    回测
    :param stock: 股票
    :param op: 操作
    :param step: 每次选几只股票
    :param init: 初始资金
    :return: op_df 每次调仓的股票和购买份额    num_df 每次调仓时的持有资金、收益率
    """
    stock_list = []
    share_list = []
    date_list = []
    money = [init]
    rate = [0]

    tot = 0
    avg_money = init / step

    # 初始化 第一次买入
    for i in range(step):
        stock_name = op.loc[i, 'stock']
        date = op.loc[i, 'date']
        price = stock.loc[(stock['代码'] == stock_name) & (stock['时间'] == date)]['开盘价(元)'].iloc[0]

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
            price = stock.loc[(stock['代码'] == stock_name) & (stock['时间'] == date)]['开盘价(元)'].iloc[0]
            temp_money += price * share_list[tot - step + i]

        money.append(temp_money)
        rate.append((temp_money - init) / init)
        avg_money = temp_money / step

        for i in range(step):
            stock_name = temp.loc[i, 'stock']
            price = stock.loc[(stock['代码'] == stock_name) & (stock['时间'] == date)]['开盘价(元)'].iloc[0]

            stock_list.append(stock_name)
            share_list.append(avg_money / price)
            date_list.append(date)

        tot += step

    close_date = sorted(stock['时间'])
    close_date = close_date[-1]
    temp_money = 0

    for i in range(step):
        stock_name = stock_list[tot - step + i]
        price = stock.loc[(stock['代码'] == stock_name) & (stock['时间'] == close_date)]['开盘价(元)'].iloc[0]
        temp_money += price * share_list[tot - step + i]

    money.append(temp_money)
    rate.append((temp_money - init) / init)

    op_df = pd.DataFrame(list(zip(date_list, stock_list, share_list)), columns=['date', 'stock_name', 'buy_num'])
    d = list(op_df['date'].unique())
    d.append(close_date)
    num_df = pd.DataFrame(list(zip(d, money, rate)), columns=['date', 'money', 'rate'])
    return op_df, num_df


def get_300(data, init, date):
    """
    本函数目的为得到以沪深300为基准的调仓日数据，用于之后绘图比较
    :param data: 沪深300日线数据
    :param init: 起始资金
    :param date: 调仓日期列表
    :return: 调仓日期对应的沪深300的资金及收益率
    """
    tot = init / data.loc[data['交易时间'] == date[0]]['开盘价'].iloc[0]
    rate = [0]
    money = [init]
    for i in date[1:]:
        price = data.loc[data['交易时间'] == i]['开盘价'].iloc[0]
        money.append(price * tot)
        rate.append((price * tot - init) / init)
    return money, rate


def main():
    g = pd.read_excel('300.xlsx')
    g['交易时间'] = pd.to_datetime(g['交易时间'])

    HuShen = pd.read_excel('300.xlsx')
    HuShen['交易时间'] = pd.to_datetime(HuShen['交易时间'])

    CAPM, CAPM_num = backtest(stock, pd.read_excel('capm.xlsx'), 5, 1000)
    ThreeF, ThreeF_num = backtest(stock, pd.read_excel('ThreeF.xlsx'), 5, 1000)
    FiveF, FiveF_num = backtest(stock, pd.read_excel('FiveF.xlsx'), 5, 1000)

    hs, hs_rate = get_300(HuShen, 1000, list(CAPM_num['date']))

    """资金变动图"""
    mpl.rcParams['font.sans-serif'] = ['SimHei']
    mpl.rcParams['axes.unicode_minus'] = False
    plt.plot(CAPM_num['date'], CAPM_num['money'])
    plt.plot(ThreeF_num['date'], ThreeF_num['money'])
    plt.plot(FiveF_num['date'], FiveF_num['money'])

    plt.plot(CAPM_num['date'], hs)
    plt.title('资金变动图')
    plt.xlabel('日期')
    plt.ylabel('资金')
    plt.axhline(1000, color='grey')
    plt.legend(['CAPM', '三因子', '五因子', '沪深300', '起始资金线'])
    plt.savefig('资金变化图.png')

    plt.clf()

    """收益率变动图"""
    plt.plot(CAPM_num['date'], CAPM_num['rate'])
    plt.plot(ThreeF_num['date'], ThreeF_num['rate'])
    plt.plot(FiveF_num['date'], FiveF_num['rate'])
    plt.plot(CAPM_num['date'], hs_rate)
    plt.title('收益率变动图')
    plt.xlabel('日期')
    plt.ylabel('收益率')
    plt.axhline(0, color='grey')
    plt.legend(['CAPM', '三因子', '五因子', '沪深300', 'x=0'])
    plt.savefig('收益率变化图.png')

    print('CAPM方法收益率为{}%'.format((CAPM_num['money'].iloc[-1] - 1000) / 10))
    print('三因子方法收益率为{}%'.format((ThreeF_num['money'].iloc[-1] - 1000) / 10))
    print('五因子方法收益率为{}%'.format((FiveF_num['money'].iloc[-1] - 1000) / 10))

    CAPM.to_csv('CAPM选股策略.csv', encoding='utf-8', index=False)
    ThreeF.to_csv('三因子选股策略.csv', encoding='utf-8', index=False)
    FiveF.to_csv('五因子选股策略.csv', encoding='utf-8', index=False)


if __name__ == '__main__': main()
