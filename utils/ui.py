import streamlit as st
import requests

def show_lottie(url: str, height: int = 160):
    try:
        import streamlit_lottie
    except Exception:
        st.caption("Install streamlit-lottie for header animation (optional).")
        return
    try:
        r = requests.get(url, timeout=10)
        if r.status_code == 200:
            streamlit_lottie.st_lottie(r.json(), height=height, loop=True)
    except Exception:
        pass