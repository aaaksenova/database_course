import streamlit as st
import psycopg2
import datetime
import search_functions


def connect():
    conn = psycopg2.connect(dbname="gfmqvpia",
                            user="gfmqvpia",
                            password="NwRoBJ0KJHXmjqUva_7ZW0XOO-qfA26E",
                            host="castor.db.elephantsql.com")

    cur = conn.cursor()
    return conn, cur


conn, cur = connect()

prod_dict = {"Потреб": 'credit', "Ипотека": 'mortage', "Дебетовая карта": 'debitCard',
             "Кредитная карта": "creditCard", "Вклад": 'deposit'}

st.title('Личный кабинет оператора в ФэнсиБанке')

st.session_state['phone_number'] = st.text_area('Введите номер клиента')
check_button = st.button('Проверить в базе')
if check_button:
    if not search_functions.check_user(cur, st.session_state['phone_number']):
        st.markdown("""Сообщи, что пользователь не зарегистрирован и перед обращением ему нужно скачать приложение или сходить в ВСП.""")
    else:
        st.markdown(search_functions.get_name(cur, st.session_state['phone_number']))

session_button = st.button('Новая сессия')
if session_button:
    st.session_state['timestampstart'] = datetime.datetime.now()
    st.session_state['sessionid'] = search_functions.get_new_sessionid(cur)
topic_button = st.button('Новая тема')
if topic_button:
    st.session_state['timestampstart'] = datetime.datetime.now()
st.session_state['product'] = st.selectbox("Выберите продукт", index=0, options=["Потреб", "Ипотека", "Дебетовая карта",
                                                             "Кредитная карта", "Вклад"])
productkeyword = prod_dict[st.session_state['product']]
cur.execute("""
SELECT productdescription
FROM products
WHERE productkeyword = '{}';
""".format(productkeyword))
st.markdown(cur.fetchall()[0][0])

end_button = st.button('Закончили')
if end_button:
    st.session_state['timestampend'] = datetime.datetime.now()
    st.session_state['last_subsession'] = search_functions.session_logging(cur, conn, st.session_state['phone_number'], st.session_state['sessionid'],
                                     st.session_state['timestampstart'], st.session_state['timestampend'], productkeyword)
    sales_button = st.button('ПРОДАЖА!')
    if sales_button:
        sales_flag = 1
        search_functions.sales_logging(cur, conn, st.session_state['last_subsession'], sales_flag)

st.subheader('Введите данные по оценке пользователя')
solved = st.selectbox("Вы решили вопрос?", index=0, options=['да', 'нет'])
csi = st.selectbox("Оценка удовлетворенности сервисом", index=0, options=[1, 2, 3, 4, 5])
comment = st.text_area('Введите комментарий')
csi_button = st.button('Отправить')
if csi_button:
    csi_flag = 1
    solved = True if solved == 'да' else False
    search_functions.csi_logging(cur, conn, csi_flag, st.session_state['last_subsession'], solved, csi, comment)
