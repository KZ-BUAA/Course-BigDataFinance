import pandas as pd
import numpy as np
import copy

sell = {1300.05: 100, 1300.04: 30, 1300.03: 20, 1300.02: 10, 1300.01: 5, 1300.0: 100}
buy = {1299.99: 2, 1299.98: 10, 1299.97: 50, 1299.96: 100, 1299.95: 2}

buy = pd.DataFrame.from_dict(buy,orient='index',columns=['lots']).reset_index().rename(columns={'index':'price'})
sell = pd.DataFrame.from_dict(sell,orient='index',columns=['lots']).reset_index().rename(columns={'index':'price'})
buy = buy.sort_values(by='price',ascending=False).reset_index(drop=True)
sell = sell.sort_values(by='price',ascending=True).reset_index(drop=True)

df = pd.read_csv('C:\\Users\\10114\\Desktop\\operate.csv')

opr = df.itertuples()
for one_step in opr:
    if one_step.op == 'buy':
        # 想买
        ask_price = one_step.price
        ask_lots = one_step.lots
        if one_step.order_type == 'limit order':
            # 想买，限价单
            if sell['price'][0] > ask_price:
                # 没有可以匹配的订单，加入buy表
                price_index = buy[buy['price']==ask_price].index.tolist()
                if len(price_index) == 0:
                    buy = buy.append({'price' : ask_price , 'lots' : ask_lots} , ignore_index=True)
                else:
                    buy.iloc[price_index[0], -1] += ask_lots

            else:
                # 有可以匹配的订单
                for i in list(sell.index):
                    if sell.iloc[i, 0] > ask_price or ask_lots <= 0:
                        break
                    if ask_lots >= sell.iloc[i, -1]:
                        ask_lots -= sell.iloc[i, -1]
                        sell.iloc[i, -1] = 0
                    else:
                        sell.iloc[i, -1] -= ask_lots
                        ask_lots = 0

                if ask_lots > 0:
                    print('市场上所有可买均买入')
                    # 因为是限价单，所以需把剩余加入buy表中
                    price_index = buy[buy['price']==ask_price].index.tolist()
                    if len(price_index) == 0:
                        buy = buy.append({'price' : ask_price , 'lots' : ask_lots} , ignore_index=True)
                    else:
                        buy.iloc[price_index[0], -1] += ask_lots

        elif one_step.order_type == 'market order':
            # 想买，市价单
            if sell['price'][0] > ask_price:
                # 没有可以匹配的订单，加入buy表
                price_index = buy[buy['price']==ask_price].index.tolist()
                if len(price_index) == 0:
                    # 列表为空
                    buy = buy.append({'price' : ask_price , 'lots' : ask_lots} , ignore_index=True)
                else:
                    buy.iloc[price_index[0], -1] += ask_lots

            else:
                # 可以匹配
                for i in list(sell.index):
                    if ask_lots <= 0:
                        break
                    if ask_lots >= sell.iloc[i, -1]:
                        ask_lots -= sell.iloc[i, -1]
                        sell.iloc[i, -1] = 0
                    else:
                        sell.iloc[i, -1] -= ask_lots
                        ask_lots = 0

                if ask_lots > 0:
                    print('市场上所有可买均买入')
                    # 市价单，理应raise error

        else:
            print('第{}行（个）操作类型有误'.format(one_step.Index+1))


    elif one_step.op == 'sell':
        # 想卖
        sell_price = one_step.price
        sell_lots = one_step.lots
        if one_step.order_type == 'limit order':
            # 想卖，限价单
            if buy['price'].iloc[0] < sell_price:
                # 没有可以匹配的订单，加入sell表
                price_index = sell[sell['price']==sell_price].index.tolist()
                if len(price_index) == 0:
                    print(1)
                    # 列表为空
                    print(type(sell_lots))
                    sell = sell.append([{'price' : sell_price , 'lots' : int(sell_lots)}] , ignore_index=True)
                else:
                    #print(price_index)
                    sell.iloc[price_index[0], -1] += sell_lots

            else:
                # 有可以匹配的订单
                for i in list(buy.index):
                    if buy['price'][i] < sell_price or sell_lots <= 0:
                        break
                    if sell_lots >= buy.iloc[i, -1]:
                        print(type(sell_lots))
                        print(type(buy.iloc[i, -1]))
                        sell_lots -= buy.iloc[i, -1]
                        buy.iloc[i, -1] = 0
                        print(type(sell_lots))
                    else:
                        buy.iloc[i, -1] -= sell_lots
                        sell_lots = 0

                if sell_lots > 0:
                    print('市场上所有可卖均卖出')
                    # 限价单 把没买加入sell表
                    price_index = sell[sell['price']==sell_price].index.tolist()
                    if len(price_index) == 0:
                        print(sell_lots)
                        #sell_lots = sell_lots.astype(int)
                        print(type(sell_lots.item()))
                        print(222)
                        x=copy.deepcopy(sell_lots.item())
                        print(type(x))
                        sell = sell.append({'price' : sell_price , 'lots' : x} , ignore_index=True)
                    else:
                        sell.iloc[price_index[0], -1] += sell_lots

        elif one_step.order_type == 'market order':
            # 想卖，市价单
            if buy['price'].iloc[0] < sell_price:
                # 没有可以匹配的订单，加入sell表
                price_index = sell[sell['price']==sell_price].index.tolist()
                if len(price_index) == 0:
                    sell = sell.append({'price': sell_price, 'lots': sell_lots}, ignore_index=True)
                else:
                    sell.iloc[price_index[0], -1] += sell_lots

            else:
                # 可以匹配
                for i in list(buy.index):
                    if sell_lots <= 0:
                        break
                    if sell_lots >= buy.iloc[i, -1]:
                        sell_lots -= buy.iloc[i, -1]
                        buy.iloc[i, -1] = 0
                    else:
                        buy.iloc[i, -1] -= sell_lots
                        sell_lots = 0

                if sell_lots > 0:
                    print('市场上所有可卖均卖出')
                    # 市价单，理应raise error

        else:
            print('第{}行（个）操作类型有误'.format(one_step.Index+1))

    buy = buy[~buy['lots'].isin([0])]
    sell = sell[~sell['lots'].isin([0])]

    # 每次操作后重新排列两张表
    buy = buy.sort_values(by='price',ascending=False).reset_index(drop=True)
    sell = sell.sort_values(by='price',ascending=True).reset_index(drop=True)
    sell['price'].astype(int)

    print('第{}行（个）操作后'.format(one_step.Index+1))
    print('------------------------------')
    print('buy表：')
    print(buy)
    print('------------------------------')
    print('sell表：')
    print(sell)
    print('------------------------------')
    print('\n\n')