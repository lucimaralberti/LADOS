import streamlit as st
from core.auth import get_current_user

# ============================================
# ⚠️ NÃO CHAMAR A SIDEBAR AQUI!
# A SIDEBAR É GERENCIADA PELO APP.PY
# ============================================

def show():
    """Conteúdo da página"""
    
    usuario = get_current_user()
    
    st.title("Título da Página")
    st.markdown("Conteúdo da página...")

if __name__ == "__main__":
    show()
