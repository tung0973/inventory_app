import streamlit as st

def mobile_css():
    st.markdown(
        """
        <style>
          /* Fix thanh dưới điện thoại */
          footer {visibility: hidden;}
          .stApp { bottom: 50px; }
        </style>
        """,
        unsafe_allow_html=True
    )