import streamlit as st
from database import get_conn

USER_KEY = "current_user"

def login_user(username, password):
    conn = get_conn()
    cur = conn.cursor()
    cur.execute(
        "SELECT id, username FROM users WHERE username=? AND password=?",
        (username, password)
    )
    row = cur.fetchone()
    conn.close()
    if row:
        st.session_state[USER_KEY] = {"id": row[0], "username": row[1]}
        return True
    return False

def get_current_user():
    return st.session_state.get(USER_KEY)

def logout_user():
    if USER_KEY in st.session_state:
        del st.session_state[USER_KEY]
    st.rerun()