import streamlit as st
from core.auth import get_current_user
from core.sidebar import render_sidebar

st.set_page_config(
    page_title="LADOS 2.0",
    page_icon="📘",
    layout="wide"
)

if "usuario" not in st.session_state:
    st.switch_page("Login.py")

st.markdown("""
<style>
[data-testid="stSidebarNav"] li a svg {
    display: none !important;
}
[data-testid="stSidebarNav"] li a {
    text-align: left !important;
    padding-left: 1rem !important;
    font-family: 'Inter', sans-serif;
    font-size: 15px;
    font-weight: bold;
}
</style>
""", unsafe_allow_html=True)

render_sidebar()

pg = st.navigation([
    st.Page("pages/1_Inicio.py", title="INÍCIO"),
    st.Page("pages/2_Questoes.py", title="QUESTÕES"),
    st.Page("pages/3_Correcao.py", title="CORREÇÃO"),
    st.Page("pages/4_Relatorios.py", title="RELATÓRIOS"),
])

pg.run()
