import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from pylab import mpl
from sklearn.decomposition import PCA

df1 = pd.read_excel('stock.xlsx', sheet_name='Sheet1')

df2 = pd.read_excel('stock.xlsx', sheet_name='Sheet2', header=None)

df2.columns = df1.columns

# 将两份数据连接到一起
df = pd.concat([df1, df2], axis=0)

# 生成最终使用的dataframe，除时间和代码外，其他都是主成分分析的指标
df = pd.DataFrame({
    'date': df['时间'],
    'code': df['代码'],
    'open_price': df['开盘价(元)'],
    'close_price': df['收盘价(元)'],
    'highest_price': df['最高价(元)'],
    'lowest_price': df['最低价(元)'],
    'trade_num': df['成交量(股)'],
    'trade_money': df['成交金额(元)'],
    'exchange': df['换手率(%)'],
    'PB': df['PB市净率'],
    'TTM': df['市盈率TTM']
})
df['date'] = pd.to_datetime(df['date'])

# 去除停牌的没有数据的股票框
df = df.replace({'--': np.nan})

# 按日期和股票代码分类
final_df = df.pivot_table(index='date', columns='code')

target = list(df.columns)[2:]  # 把时间和股票代码去掉
stock_code = list(df['code'].unique())  # 取出所有股票的代码集合

# 生成评估数据
test = pd.read_csv('沪深300指数历史数据.csv')
test = pd.DataFrame({
    'date': test['日期'],
    'price': test['收盘']
})
test['date'] = pd.to_datetime(test['date'], format='%Y年%m月%d日')
test['price'] = pd.to_numeric(test['price'])

test = test.sort_values(by='date', ascending=True)
test = test.set_index('date', drop=True)
test = (test - test.mean()) / test.std()

# 接下来逐只股票生成情绪因子
coef = []  # 相关系数列表

for one_stock in stock_code:
    # 取一只股票
    temp = pd.DataFrame()
    for one_target in target:
        # 取该股票的每一个指标
        one_column = final_df[(one_target, one_stock)]
        temp = pd.concat([temp, one_column], axis=1)  # 拼接进该股票的总表

    temp.columns = target
    temp = (temp - temp.mean()) / temp.std()  # 归一化
    temp = temp.dropna(axis=0, how='any')  # 去除停牌

    # 接下来进行主成分分析
    pca = PCA(n_components=1)
    sentiment = pca.fit_transform(temp)
    temp['emo'] = sentiment  # 情绪因子列
    temp['hs'] = test.loc[temp.index]  # 沪深三百对比列
    plt.clf()
    mpl.rcParams['font.sans-serif'] = ['SimHei']
    mpl.rcParams['axes.unicode_minus'] = False
    plt.plot(temp['emo'], label='情绪因子')
    plt.plot(temp['hs'], color='orange', label='沪深300')
    plt.xticks(rotation=45)
    plt.title('{}与沪深300走势对比图'.format(one_stock))
    if abs(np.corrcoef(temp['hs'], temp['emo'])[1, 0]) > 0.8:
        plt.legend()
        plt.show()

    coef.append(abs(np.corrcoef(temp['hs'], temp['emo'])[1, 0]))  # 记录相关系数

plt.clf()
mpl.rcParams['font.sans-serif'] = ['SimHei']
mpl.rcParams['axes.unicode_minus'] = False
plt.hist(coef, histtype='step')
plt.title('相关系数直方图')
plt.savefig('相关系数直方图.jpg')
plt.show()
tot = 0
for i in coef:
    if abs(i) > 0.4:
        # 统计中度相关及以上的
        tot += 1
print('与沪深300变化中度相关及以上的情绪因子个数为：', tot)
