import pandas as pd
import numpy as np
import csv

providers = pd.read_csv('data/input_files/condition_4.csv', names=['Запаси', 'Ціна', 'Знижка', 'Умова знижки'])


def get_z(df):
    df['Витрати'] = None
    for i in range(1, len(df)+1):
        df.loc[i, 'Витрати'] = int((df.loc[i, 'Ціна купівлі']) * (df.loc[i, 'Кількість товару']))
    df.astype(int)


def check_v(df):
    new_v = df['Запаси'].sum()
    return new_v


def check_n(df):
    new_n = df['Умова знижки'].sum()
    return new_n


def check_sale(df):
    for i in range(1, len(df)+1):
        if df.loc[i, 'Умова знижки'] > df.loc[i, 'Запаси']:
            df.loc[i, 'Умова знижки'] = np.NaN
            df.loc[i, 'Знижка'] = np.NaN
        else:
            i += 1


def penalty(df):
    df['Штраф'] = ""
    for i in range(1, len(df)+1):
        if df.loc[i, 'Умова знижки'] <= df.loc[i, 'Запаси']:
            df.loc[i, 'Штраф'] = df.loc[i, 'Ціна'] - df.loc[i, 'Знижка']
        else:
            df.loc[i, 'Штраф'] = 0

def sale_checker(df):
    df['Без знижки'] = None
    for i in range(1, len(df)+1):
        n_i = df.loc[i, 'Умова знижки']
        v_i = df.loc[i, 'Запаси']
        if n_i < v_i:
            df.loc[i, 'Без знижки'] = n_i - 1
        else:
            df.loc[i, 'Без знижки'] = v_i
            df.loc[i, 'Знижка'] = df.loc[i, 'Ціна']
    return df.astype(int)


def greedy_algorithm(df, need):
    total_v = check_v(df)
    total_n = check_n(df)
    buy_table = pd.DataFrame(columns=['Постачальник', 'Ціна купівлі', 'Кількість товару'])
    if total_n < need:
        if total_v >= need:
            check_sale(df)
            while need > 0:
                min_s = df['Ціна'].min()
                index_s = df['Ціна'].idxmin()
                min_c = df['Знижка'].min()
                index_c = df['Знижка'].idxmin()
                if min_c < min_s or min_c == min_s:
                    future_x = df.loc[index_c, 'Запаси']
                    future_x2 = df.loc[index_c, 'Умова знижки']
                    if future_x <= need:
                        buy_table = buy_table.append(
                            {'Постачальник': index_c, 'Ціна купівлі': min_c, 'Кількість товару': future_x},
                            ignore_index=True)
                    else:
                        if need >= future_x2:
                            buy_table = buy_table.append(
                                {'Постачальник': index_c, 'Ціна купівлі': min_c, 'Кількість товару': need},
                                ignore_index=True)
                        else:
                            new_min_index_s = df.loc[index_c, 'Ціна']
                            buy_table = buy_table.append(
                                {'Постачальник': index_c, 'Ціна купівлі': new_min_index_s, 'Кількість товару': need},
                                ignore_index=True)
                    df.loc[index_c, 'Знижка'] = np.NaN
                    df.loc[index_c, 'Ціна'] = np.NaN
                else:
                    new_x = df.loc[index_s, 'Запаси']
                    if new_x <= need:
                        buy_table = buy_table.append(
                            {'Постачальник': index_s, 'Ціна купівлі': min_s, 'Кількість товару': new_x},
                            ignore_index=True)
                    else:
                        buy_table = buy_table.append(
                            {'Постачальник': index_s, 'Ціна купівлі': min_s, 'Кількість товару': need},
                            ignore_index=True)
                    df.loc[index_s, 'Знижка'] = np.NaN
                    df.loc[index_s, 'Ціна'] = np.NaN
                last_x = buy_table['Кількість товару'].iloc[-1]
                need -= last_x
            buy_table.index += 1
            return buy_table.astype(int)
        else:
            return 'Сума запасів ({} ум. од.) менша, аніж потреба ({} ум.од.)'.format(total_v, need)
    else:
        return 'Сумарна умова знижки ({} ум.од.) більше/рівна, аніж потреба ({} ум.од.)'.format(total_n, need)


def tsh_1(df, need):
    total_v = check_v(df)
    total_n = check_n(df)
    buy_table = pd.DataFrame(columns=['Постачальник', 'Ціна купівлі', 'Кількість товару'])
    if total_n < need:
        if total_v >= need:
            while need > 0:
                p = int(df['Штраф'].max())
                index_p = df['Штраф'].idxmax()
                if p > 0:
                    new_n = df.loc[index_p, 'Умова знижки']
                    min_c = df.loc[index_p, 'Знижка']
                    min_ss = df.loc[index_p, 'Ціна']
                    if new_n <= need:
                        buy_table = buy_table.append({'Постачальник': index_p, 'Ціна купівлі': min_c,
                                                      'Кількість товару': new_n}, ignore_index=True)
                        df.loc[index_p, 'Ціна'] = 1000
                        df.loc[index_p, 'Штраф'] = 0
                        df.loc[index_p, 'Запаси'] -= new_n
                        df.loc[index_p, 'Умова знижки'] = 0
                        last_x1 = buy_table['Кількість товару'].iloc[-1]
                        need -= last_x1
                    elif need < new_n:
                        buy_table = buy_table.append({'Постачальник': index_p, 'Ціна купівлі': min_ss,
                                                      'Кількість товару': 0}, ignore_index=True)
                        df.loc[index_p, 'Штраф'] = 0
                        df.loc[index_p, 'Знижка'] = np.NaN
                elif p == 0:
                    min_s = df['Ціна'].min(skipna=True)
                    index_s = df['Ціна'].idxmin(skipna=True)
                    min_c = df['Знижка'].min(skipna=True)
                    index_c = df['Знижка'].idxmin(skipna=True)
                    if min_c < min_s or min_c == min_s:
                        future_x = df.loc[index_c, 'Запаси']
                        future_x2 = df.loc[index_c, 'Умова знижки']
                        new_min_s = df.loc[index_c, 'Ціна']
                        if future_x <= need and future_x2 <= future_x:
                            buy_table = buy_table.append(
                                {'Постачальник': index_c, 'Ціна купівлі': min_c, 'Кількість товару': future_x},
                                ignore_index=True)
                        elif future_x < future_x2 and future_x <= need:
                            buy_table = buy_table.append({'Постачальник': index_c, 'Ціна купівлі': new_min_s,
                                                          'Кількість товару': future_x},
                                                         ignore_index=True)
                            df.loc[index_c, 'Знижки'] = np.NaN
                        elif future_x > need:
                            buy_table = buy_table.append({'Постачальник': index_c, 'Ціна купівлі': min_c,
                                                          'Кількість товару': need},
                                                         ignore_index=True)

                        df.loc[index_c, 'Знижка'] = np.NaN
                        df.loc[index_c, 'Ціна'] = 100
                    else:
                        new_x = df.loc[index_s, 'Запаси']
                        if new_x <= need:
                            buy_table = buy_table.append(
                                {'Постачальник': index_s, 'Ціна купівлі': min_s, 'Кількість товару': new_x},
                                ignore_index=True)
                        else:
                            buy_table = buy_table.append(
                                {'Постачальник': index_s, 'Ціна купівлі': min_s, 'Кількість товару': need},
                                ignore_index=True)
                        df.loc[index_s, 'Знижка'] = np.NaN
                        df.loc[index_s, 'Ціна'] = np.NaN
                    last_x = buy_table['Кількість товару'].iloc[-1]
                    need -= last_x
            buy_table.index += 1
            return buy_table.astype(int)
        else:
            return 'Сума запасів ({} ум. од.) менша, аніж потреба ({} ум.од.)'.format(total_v, need)
    else:
        return 'Сумарна умова знижки {} ум. од.) більше/рівна, аніж потреба {} ум. од.)'.format(total_n, need)


def tsh_2(df, need):
    total_v = check_v(df)
    total_n = check_n(df)
    buy_table = pd.DataFrame(columns=['Постачальник', 'Витрата', 'Кількість тканини'])
    if total_n < need:
        if total_v >= need:
            while need > 0:
                buy_point = pd.DataFrame(data=None, index=[i for i in range(1, len(df) + 1)],
                                         columns=['К-сть тканини', 'Витрати'])
                new_v = df['Запаси'].min()
                if new_v > need:
                    buy_point['К-сть тканини'] = need
                else:
                    buy_point['К-сть тканини'] = new_v

                for i in range(1, len(df)+1):
                    v_i = df.loc[i, 'Запаси']
                    t_i = buy_point.loc[i, 'К-сть тканини']
                    y_i = df.loc[i, 'Без знижки']
                    if v_i > 0:
                        if t_i <= y_i:
                            buy_point.loc[i, 'Витрати'] = buy_point.loc[i, 'К-сть тканини'] * df.loc[i, 'Ціна']
                        else:
                            buy_point.loc[i, 'Витрати'] = y_i * df.loc[i, 'Ціна'] + (buy_point.loc[i, 'К-сть тканини'] - y_i)*df.loc[i, 'Знижка']
                    else:
                        buy_point.loc[i, 'Витрати'] = np.NaN
                buy_point['Витрати'] = pd.to_numeric(buy_point['Витрати'])
                min_q = buy_point['Витрати'].min()
                index_q = buy_point['Витрати'].idxmin()
                big_t = buy_point['К-сть тканини'].iloc[-1]
                buy_table = buy_table.append({'Постачальник': index_q, 'Витрата': min_q, 'Кількість тканини': big_t},
                                             ignore_index=True)

                if big_t > df.loc[index_q, 'Без знижки']:
                    df.loc[index_q, 'Ціна'] = df.loc[index_q, 'Знижка']
                df.loc[index_q, 'Запаси'] = df.loc[index_q, 'Запаси'] - big_t
                if df.loc[index_q, 'Запаси'] == 0:
                    df.loc[index_q, 'Запаси'] = np.NaN
                need -= big_t
            buy_table.index += 1
            return buy_table.astype(int)
        else:
            return 'Сума запасів ({} ум. од.) менша, аніж потреба ({} ум.од.)'.format(total_v, need)
    else:
        return 'Сумарна умова знижки {} ум. од.) більше/рівна, аніж потреба {} ум. од.)'.format(total_n, need)

