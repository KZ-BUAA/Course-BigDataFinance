import pandas as pd

# df1 = pd.read_excel('19-20.xlsx')
df2 = pd.read_excel('20-21.xlsx')
df3 = pd.read_excel('21-22.xlsx')

# df = pd.concat([df1, df2, df3], axis=0)
df = pd.concat([df2, df3], axis=0)

stock_code = list(df['代码'].unique())
table = df.pivot_table(index='时间', columns='代码', values='收盘价(元)')

temp = pd.DataFrame()
for one_stock in stock_code:
    temp = pd.concat([temp, table[one_stock]], axis=1)

temp.index.name = 'date'

temp.to_csv('stock_final_20_22.csv', encoding='gbk', sep=',', index=True)
