import streamlit as st
from core.auth import get_current_user

def show():
    usuario = get_current_user()
    if usuario.get("perfil") != "admin":
        st.error("❌ Acesso negado.")
        st.stop()
    
    st.title("⚙️ Configurações")
    st.info("Página de configurações em desenvolvimento")
