"""
Módulo de login - Pode ser importado ou executado diretamente
"""

import streamlit as st
from core.auth import autenticar_usuario

def mostrar_login():
    """Função que mostra a tela de login (chamada pelo app.py)"""
    
    st.markdown("""
    <style>
    [data-testid="stSidebar"] { display: none; }
    [data-testid="stSidebarHeader"] { display: none; }
    #MainMenu { visibility: hidden; }
    footer { visibility: hidden; }
    
    .login-box {
        max-width: 400px;
        margin: auto;
        padding: 2rem;
        background: white;
        border-radius: 15px;
        box-shadow: 0 4px 25px rgba(0,0,0,0.1);
        text-align: center;
    }
    
    .login-title {
        font-size: 28px;
        font-weight: bold;
        margin-bottom: 2rem;
        color: #1e3c72;
    }
    </style>
    """, unsafe_allow_html=True)
    
    st.markdown("""
    <div class="login-box">
        <div class="login-title">📚 LADOS 2.0</div>
    """, unsafe_allow_html=True)
    
    st.title("Login")
    
    with st.form("login_form"):
        usuario = st.text_input("Usuário", placeholder="Digite seu usuário")
        senha = st.text_input("Senha", type="password", placeholder="Digite sua senha")
        entrar = st.form_submit_button("Entrar", use_container_width=True)
    
    if entrar:
        if usuario and senha:
            user = autenticar_usuario(usuario, senha)
            if user:
                st.session_state["usuario"] = user
                st.session_state["autenticado"] = True
                st.rerun()
            else:
                st.error("❌ Usuário ou senha inválidos")
        else:
            st.error("❌ Preencha usuário e senha")
    
    st.markdown('</div>', unsafe_allow_html=True)

# Quando executado diretamente (streamlit run Login.py)
def main():
    st.set_page_config(page_title="LADOS - Login", page_icon="📘", layout="centered")
    mostrar_login()

if __name__ == "__main__":
    main()
