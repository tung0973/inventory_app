import streamlit as st

def mobile_css():
    st.markdown(
        """
        <style>
          /* Fix thanh dưới điện thoại */
          footer {visibility: hidden;}
          .stApp { bottom: 50px; }
          @media (max-width: 600px) {
        .nav-button {
          font-size: 14px;
          padding: 8px 0;
    }
}

        </style>
        
        """,
        unsafe_allow_html=True
    )