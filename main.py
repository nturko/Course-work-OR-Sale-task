import streamlit as st
import pages as md


def main():
    st.sidebar.title("Оберіть сторінку:")
    pages = ['Математичні відомості', 'Інструкція користувача/FAQ', 'Створення нової умови', 'Розв\'язання задачі']
    page = st.sidebar.radio("Навігація", options=pages)

    if page == 'Математичні відомості':
        md.presentation_page()

    if page == 'Інструкція користувача/FAQ':
        md.instruction_page()

    if page == 'Створення нової умови':
        md.create_condition_page()

    if page == 'Розв\'язання задачі':
        md.solution_page()


if __name__ == '__main__':
    main()
