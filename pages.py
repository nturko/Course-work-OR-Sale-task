import streamlit as st
import SessionState
import os
import pandas as pd
from functions import markdown2string
from streamlit import caching
from functions import create_file_with_condition, parse_condition_csv, create_line, create_random_condition
from algorithms import greedy_algorithm, tsh_1, tsh_2, penalty, sale_checker, get_z


def instruction_page():
    st.title('Інструкція користувача')
    st.markdown(markdown2string('data/markdown/instructions_page.md'))


def solution_page():
    st.title('Отримання розв\'язків')
    session_state = SessionState.get(choose_button=False, input_type='', random='', file='')
    session_state.input_type = st.selectbox('Оберіть тип вхідних даних', ['Файл', 'Випадкова генерація'])

    if session_state.input_type == 'Файл':
        filename = file_selector()
        st.write('Ви обрали `%s`' % filename)
        providers = parse_condition_csv(filename)
        providers2 = parse_condition_csv(filename)
        providers2.index += 1
        providers.index += 1
        st.write(providers)
        st.subheader('Надайте додаткові дані')
        need_n = st.number_input('Введіть потрібну Вам кількість товару', step=10, value=100, min_value=10, max_value=5000)
        method = st.selectbox('Оберіть метод вирішення задачі',
                              ['Жадібний алгоритм',
                               'ТШ_1',
                               'ТШ_2',
                               'Жадібний + ТШ_1'])
        if st.button('Розв\'язати'):
            if method == 'Жадібний алгоритм':
                answer = greedy_algorithm(providers.astype(int), need_n)
                if type(answer) == pd.core.frame.DataFrame:
                    st.write('')
                    st.write('')
                    st.write('')
                    st.success('Задача вирішена. :sunglasses: '
                               'За допомогою жадібного алгоритму було отримано такий розв\'язок:')
                    answer.astype(int)
                    get_z(answer)
                    st.write(answer)
                    z = int(answer['Витрати'].sum())
                    st.markdown("**Сумарна витрата становить:** {} ум. одиниць".format(z))
                else:
                    st.error(answer)

            elif method == 'ТШ_1':
                penalty(providers)
                st.write('')
                st.write('')
                st.write('')
                st.write('Вхідна умова з розрахунком штрафів:')
                st.write(providers)
                answer = tsh_1(providers.astype(int), need_n)
                if type(answer) == pd.core.frame.DataFrame:
                    st.success('Задача вирішена :sunglasses:. '
                               'За допомогою алгоритму ТШ_1 було отримано такий розв\'язок:')
                answer.astype(int)
                get_z(answer)
                st.write(answer)
                z = int(answer['Витрати'].sum())
                st.markdown("**Сумарна витрата становить:** {} ум. одиниць".format(z))

            elif method == 'ТШ_2':
                sale_checker(providers)
                st.write('')
                st.write('')
                st.write('')
                st.write('Вхідна умова з розрахунком купівлі тканини без знижки:')
                st.write(providers)
                answer = tsh_2(providers, need_n)
                if type(answer) == pd.core.frame.DataFrame:
                    st.success('Задача вирішена :sunglasses:. '
                            'За допомогою алгоритму ТШ_2 було отримано такий розв\'язок:')
                    answer.astype(int)
                    st.write(answer)
                    z = int(answer['Витрата'].sum())
                    st.markdown("**Сумарна витрата становить:** {} ум. одиниць".format(z))
                else:
                    st.error(answer)

            elif method == 'Жадібний + ТШ_1':
                answer1 = greedy_algorithm(providers.astype(int), need_n)
                if type(answer1) == pd.core.frame.DataFrame:
                    st.write('')
                    st.write('')
                    st.write('')
                    st.success('Задача вирішена :sunglasses: .'
                               ' За допомогою жадібного алгоритму було отримано такий розв\'язок:')
                    get_z(answer1)
                    st.write(answer1)
                    z1 = int(answer1['Витрати'].sum())
                    st.markdown("**Сумарна витрата становить:** {} ум. одиниць".format(z1))
                    st.write('')
                    st.write('')
                    st.write('')
                    penalty(providers2)
                    st.write(providers2)
                    answer2 = tsh_1(providers2.astype(int), need_n)
                    if type(answer2) == pd.core.frame.DataFrame:
                        st.success('Задача вирішена :sunglasses: .'
                                   ' За допомогою алгоритму ТШ_1 було отримано такий розв\'язок:')
                    get_z(answer2)
                    st.write(answer2)
                    z2 = int(answer2['Витрати'].sum())
                    st.markdown("**Сумарна витрата становить:** {} ум. одиниць".format(z2))
                    st.write('')
                    st.write('')
                    st.write('')
                    st.subheader('Дослідження отриманих розв\'язків')
                    graph1 = create_line(answer1, answer2)
                    st.bokeh_chart(graph1, use_container_width=True)

                else:
                    st.error(answer1)

    elif session_state.input_type == 'Випадкова генерація':
        providers = pd.DataFrame(columns=['Запаси', 'Ціна', 'Знижка', 'Умова знижки'])
        new_m = st.number_input('Кількість постачальників', step=1, value=5, min_value=1, max_value=100)
        pr_dev = st.number_input('Максимальна різниця початкової ціни та ціни з наданням знижки',
                                 step=1, value=20, min_value=1, max_value=100)

        new_price = st.slider('Діапазон цін без надання знижки', 2, 200, (10, 100))
        new_v = st.slider('Діапазон запасів постачальників', 1, 400, (1, 60))
        if st.button('Згенерувати умову задачі'):
            providers = create_random_condition(new_m, new_price[0], new_price[1], pr_dev, new_v[0], new_v[1])
            providers.index += 1
            providers.to_csv(r'data/random/condition_random.csv', index=False)
        providers = pd.read_csv('data/random/condition_random.csv', sep=',')
        providers.index += 1
        providers2 = providers
        st.write(providers)
        st.subheader('Надайте додаткові дані')
        need_n = st.number_input('Введіть потрібну Вам кількість товару', step=10, value=100, min_value=10,
                                     max_value=5000)
        method = st.selectbox('Оберіть метод вирішення задачі',
                                  ['Жадібний алгоритм', 'ТШ_1', 'ТШ_2', 'Жадібний + ТШ_1'])
        if st.button('Розв\'язати'):
            if method == 'Жадібний алгоритм':
                answer = greedy_algorithm(providers.astype(int), need_n)
                if type(answer) == pd.core.frame.DataFrame:
                    st.write('')
                    st.write('')
                    st.write('')
                    st.success('Задача вирішена. :sunglasses: '
                                   'За допомогою жадібного алгоритму було отримано такий розв\'язок:')
                    answer.astype(int)
                    get_z(answer)
                    answer.astype(int)
                    st.write(answer)
                    z = int(answer['Витрати'].sum())
                    st.markdown("**Сумарна витрата становить:** {} ум. одиниць".format(z))
                else:
                    st.error(answer)

            elif method == 'ТШ_1':
                penalty(providers)
                st.write('')
                st.write('')
                st.write('')
                st.write('Вхідні умова з розрахунком штрафів:')
                st.write(providers)
                answer = tsh_1(providers.astype(int), need_n)
                if type(answer) == pd.core.frame.DataFrame:
                    st.success('Задача вирішена :sunglasses:. '
                            'За допомогою алгоритму ТШ_1 було отримано такий розв\'язок:')
                    answer.astype(int)
                    get_z(answer)
                    answer.astype(int)
                    st.write(answer)
                    z = int(answer['Витрати'].sum())
                    st.markdown("**Сумарна витрата становить:** {} ум. одиниць".format(z))
                else:
                    st.error(answer)

            elif method == 'ТШ_2':
                sale_checker(providers)
                st.write('')
                st.write('')
                st.write('')
                st.write('Вхідні умова з розрахунком купівлі тканини без знижки:')
                st.write(providers)
                answer = tsh_2(providers, need_n)
                if type(answer) == pd.core.frame.DataFrame:
                    st.success('Задача вирішена :sunglasses:. '
                            'За допомогою алгоритму ТШ_2 було отримано такий розв\'язок:')
                    answer.astype(int)
                    st.write(answer)
                    z = int(answer['Витрата'].sum())
                    st.markdown("**Сумарна витрата становить:** {} ум. одиниць".format(z))
                else:
                    st.error(answer)

            elif method == 'Жадібний + ТШ_1':
                answer1 = greedy_algorithm(providers.astype(int), need_n)
                if type(answer1) == pd.core.frame.DataFrame:
                    st.write('')
                    st.write('')
                    st.write('')
                    st.success('Задача вирішена :sunglasses: .'
                                   ' За допомогою жадібного алгоритму було отримано такий розв\'язок:')
                    get_z(answer1)
                    answer1.astype(int)
                    st.write(answer1)
                    z1 = int(answer1['Витрати'].sum())
                    st.markdown("**Сумарна витрата становить:** {} ум. одиниць".format(z1))
                    st.write('')
                    st.write('')
                    st.write('')
                    penalty(providers2)
                    st.write(providers2)
                    answer2 = tsh_1(providers2.astype(int), need_n)
                    st.success('Задача вирішена :sunglasses: .'
                                   'За допомогою алгоритму ТШ_1 було отримано такий розв\'язок:')
                    get_z(answer2)
                    answer2.astype(int)
                    st.write(answer2)
                    z2 = int(answer2['Витрати'].sum())
                    st.markdown("**Сумарна витрата становить:** {} ум. одиниць".format(z2))
                    st.write('')
                    st.write('')
                    st.write('')
                    st.subheader('Дослідження отриманих розв\'язків')
                    graph1 = create_line(answer1, answer2)
                    st.bokeh_chart(graph1, use_container_width=True)
                else:
                    st.error(answer1)


def create_condition_page():
    st.title('Створення нової умови задачі')
    df = get_new_table()

    if st.button('Візуалізувати'):
        st.write(df)

    if st.button('Зберегти умову у файл'):
        create_file_with_condition(df)
        caching.clear_cache()

    if st.button('Додати постачальника'):
        df.append(pd.Series(), ignore_index=True)

    for i in range(len(df) + 1):
        st.subheader('Запас {} постачальника'.format(i + 1))
        V = st.number_input('Оберіть запас {} постачальника'.format(i + 1), step=1, value=10, min_value=1,
                            max_value=100)
        S = st.number_input('Оберіть ціну {} постачальника'.format(i + 1), step=1, value=15, min_value=1, max_value=100)
        C = st.number_input('Оберіть ціну зі знижкою {} постачальника'.format(i + 1), step=1, value=5, min_value=1,
                            max_value=100)
        n = st.number_input('Оберіть умову знижки {} постачальника'.format(i + 1), step=1, value=7, min_value=2,
                            max_value=100)
    if st.button('Зберегти постачальника'):
        if C < S:
            df.loc[i] = [V, S, C, n]
        else:
            st.error('Ціна зі знижкою більше звичайної ціни')


def presentation_page():
    st.title('Задача про знижки')
    st.markdown(markdown2string('data/markdown/presentation_page.md'))


def file_selector(folder_path='./data/input_files'):
    filenames = os.listdir(folder_path)
    selected_filename = st.selectbox('Оберіть файл', filenames)
    return os.path.join(folder_path, selected_filename)


@st.cache(allow_output_mutation=True)
def get_new_table():
    df = pd.DataFrame(columns=['Запаси', 'Ціна', 'Знижка', 'Умова знижки'])
    return df
