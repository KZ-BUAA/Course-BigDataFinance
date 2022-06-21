import pandas as pd
import copy

from copulas import *

df = pd.read_csv('stock_final_20_22.csv', encoding='gbk')  # 读入数据

df.set_index('date', inplace=True)  # 设置目录
temp = copy.deepcopy(df)
prices = temp.dropna(axis=1)
returns = np.log(prices).diff().dropna()

# 初始化日期
form_start = '2020-06-01'
form_end = '2021-05-31'
trade_start = '2021-06-01'
trade_end = '2022-05-31'

# 初始化形成期，交易期数据
prices_form = prices[form_start:form_end]
prices_trade = prices[trade_start:trade_end]
returns_form = returns.loc[form_start:form_end]
returns_trade = returns.loc[trade_start:trade_end]

# 计算肯德尔相关系数
results = pd.DataFrame(columns=['tau'])

for s1 in returns_form.columns:
    for s2 in returns_form.columns:
        if (s1 != s2) and (f'{s2}-{s1}' not in results.index):
            results.loc[f'{s1}-{s2}'] = stats.kendalltau(returns_form[s1], returns_form[s2])[0]


def parse_pair(pair):
    # 切分函数
    s1 = pair[:pair.find('-')]
    s2 = pair[pair.find('-') + 1:]
    return s1, s2


# 选取股票对
selected_stocks = []
selected_pairs = []

for pair in results.sort_values(by='tau', ascending=False).index:
    s1, s2 = parse_pair(pair)
    if (s1 not in selected_stocks) and (s2 not in selected_stocks):
        selected_stocks.append(s1)
        selected_stocks.append(s2)
        selected_pairs.append(pair)

    if len(selected_pairs) == 10:
        # 选取配对关系较好的前十只股票
        break

marginals_df = pd.DataFrame(index=selected_stocks, columns=['Distribution', 'AIC', 'BIC', 'KS_pvalue'])


algo_returns = {}
cl = 0.95  # confidence level
op_list = pd.DataFrame()
output = pd.DataFrame(index=returns_trade.index, columns=selected_pairs)

for pair in selected_pairs:
    s1, s2 = parse_pair(pair)

    # 拟合边缘分布
    params_s1 = stats.t.fit(returns_form[s1])
    dist_s1 = stats.t(*params_s1)
    params_s2 = stats.t.fit(returns_form[s2])
    dist_s2 = stats.t(*params_s2)

    # 计算cdf
    u = dist_s1.cdf(returns_form[s1])
    v = dist_s2.cdf(returns_form[s2])

    # 拟合copula
    best_aic = np.inf
    best_copula = None

    copulas = [GaussianCopula()]
    for copula in copulas:
        copula.fit(u, v)
        L = copula.log_likelihood(u, v)
        aic = 2 * copula.num_params - 2 * L
        if aic < best_aic:
            best_aic = aic
            best_copula = copula

    # 计算条件概率
    prob_s1 = []
    prob_s2 = []

    # 计算交易点
    for u, v in zip(dist_s1.cdf(returns_trade[s1]), dist_s2.cdf(returns_trade[s2])):
        prob_s1.append(best_copula.cdf_u_given_v(u, v))
        prob_s2.append(best_copula.cdf_v_given_u(u, v))

    probs_trade = pd.DataFrame(np.vstack([prob_s1, prob_s2]).T, index=returns_trade.index, columns=[s1, s2])

    # 初始化两个状态记录变量
    long = False
    short = False

    for t in output.index:
        if long:
            if (probs_trade.loc[t][s1] > 0.5) or (probs_trade.loc[t][s2] < 0.5):
                output.loc[t, pair] = '0,0'
                long = False
            else:
                output.loc[t, pair] = '1,-1'

        elif short:
            if (probs_trade.loc[t][s1] < 0.5) or (probs_trade.loc[t][s2] > 0.5):
                output.loc[t, pair] = '0,0'
                short = False
            else:
                output.loc[t, pair] = '-1,1'

        else:
            if (probs_trade.loc[t][s1] < (1 - cl)) and (probs_trade.loc[t][s2] > cl):
                # s1被低估，s2被高估
                output.loc[t, pair] = '1,-1'
                long = True
            elif (probs_trade.loc[t][s1] > cl) and (probs_trade.loc[t][s2] < (1 - cl)):
                # s2被低估，s1被高估
                output.loc[t, pair] = '-1,1'
                short = True
            else:
                output.loc[t, pair] = '0,0'


output.to_csv('output_20_22.csv', sep=',', encoding='utf-8')
