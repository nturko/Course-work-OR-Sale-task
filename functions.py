import random
import pandas as pd
import os
import csv
from bokeh.plotting import figure


def markdown2string(file_path):
    with open(file_path, 'r', encoding='utf-8',
              errors='ignore') as f:
        string = f.read()

    return string


def create_file_with_condition(condition):
    names = {name for roots, dirs, files in os.walk('data/input_files') for name in files}
    available_name_found = False
    skeleton = 'condition_{}.csv'
    i = 1
    while not available_name_found:
        if skeleton.format(i) not in names:
            available_name_found = True
            condition.to_csv(r'data\input_files\{}'.format(skeleton.format(i)), index=False, header=False)
        else:
            i += 1


def parse_condition_csv(path):
    providers = pd.DataFrame(columns=['Запаси', 'Ціна', 'Знижка', 'Умова знижки'])
    try:
        with open(path, 'r') as f:
            lines = csv.reader(f, delimiter=",")
            for line in lines:
                rows = [[int(line[0]), int(line[1]), int(line[2]), int(line[3])]]
                providers = providers.append(pd.DataFrame(rows, columns=providers.columns), ignore_index=True)
    except:
        return 'Обраний файл не відповідає потрібному формату'

    return providers


def create_line(df1, df2):
    x1 = []
    x2 = []
    y1 = []
    y2 = []
    for i in range(1, len(df1)+1):
            x1.append(i)
            y1.append(df1.loc[i, 'Витрати'])
    for j in range(1, len(df2)+1):
        x2.append(j)
        y2.append(df2.loc[j, 'Витрати'])

    graph = figure(title='Зміна цільової функції від кроку до кроку', x_axis_label='Крок', y_axis_label='Витраченно на кроці')
    graph.multi_line([x1, x2], [y1, y2], color=["firebrick", "navy"], alpha=[0.8, 0.3], line_width=5)
    return graph


def create_random_condition(num_suppliers, min_val_price, max_val_price,
                            price_deviation, min_val_stock, max_val_stock):
        condition = []
        providers = pd.DataFrame(columns=['Запаси', 'Ціна', 'Знижка', 'Умова знижки'])
        for i in range(0, num_suppliers):
            sup, pr, disc, disc_c = 0, 0, 0, 0
            sup = random.randint(min_val_stock, max_val_stock)
            pr = random.randint(min_val_price, max_val_price)
            while disc <= 0:
                disc = random.randint(pr - price_deviation, pr - 1)
            disc_c = random.randint(min_val_stock, max_val_stock)
            condition.append([sup, pr, disc, disc_c])
            providers = providers.append(pd.DataFrame(condition, columns=providers.columns), ignore_index=True)
            condition.pop()
        return providers

