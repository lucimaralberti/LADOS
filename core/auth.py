import streamlit as st
import requests
import os
from dotenv import load_dotenv

load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

def autenticar_usuario(email: str, senha: str):
    headers = {
        "apikey": SUPABASE_KEY,
        "Authorization": f"Bearer {SUPABASE_KEY}"
    }
    url = f"{SUPABASE_URL}/rest/v1/usuarios?email=eq.{email}&select=*"
    
    try:
        response = requests.get(url, headers=headers)
        if response.status_code == 200 and response.json():
            usuario = response.json()[0]
            # Usar a coluna 'senha' (não 'senha_hash')
            if usuario.get("senha") == senha:
                return usuario
        return None
    except Exception as e:
        print(f"Erro: {e}")
        return None

def get_current_user():
    if "usuario" in st.session_state:
        return st.session_state["usuario"]
    return None

def fazer_login():
    st.markdown("""
    <style>
    [data-testid="stSidebar"] { display: none; }
    [data-testid="stSidebarHeader"] { display: none; }
    [data-testid="collapsedControl"] { display: none; }
    </style>
    """, unsafe_allow_html=True)
    
    st.title("📚 LADOS 2.0")
    st.subheader("Sistema de Avaliação")
    
    with st.form("login_form"):
        email = st.text_input("E-mail")
        senha = st.text_input("Senha", type="password")
        submitted = st.form_submit_button("Entrar", type="primary", use_container_width=True)
        
        if submitted:
            if email and senha:
                usuario = autenticar_usuario(email, senha)
                if usuario:
                    st.session_state["usuario"] = usuario
                    st.success("Login realizado com sucesso!")
                    st.rerun()
                else:
                    st.error("❌ E-mail ou senha inválidos")
            else:
                st.error("❌ Preencha e-mail e senha")

def logout():
    if "usuario" in st.session_state:
        del st.session_state["usuario"]
    st.rerun()
