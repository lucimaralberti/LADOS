import streamlit as st
import json
from pathlib import Path

# Usuários padrão embutidos (fallback)
USUARIOS_PADRAO = [
    {"id": "1", "nome": "Administrador", "email": "admin@lados.com", "senha": "admin123", "role": "admin"},
    {"id": "2", "nome": "Professor Demo", "email": "professor@lados.com", "senha": "professor123", "role": "professor"},
    {"id": "3", "nome": "Coordenadora", "email": "coordenadora@lados.com", "senha": "coord123", "role": "coordenadora"}
]

def mostrar_login():
    """Função de login"""
    
    # Esconder header
    st.markdown("""<style>header {visibility: hidden;}</style>""", unsafe_allow_html=True)
    
    st.title("📚 Sistema LADOS")
    st.markdown("### Diagnóstico Pedagógico Inteligente")
    st.markdown("---")
    
    with st.form("login_form"):
        email = st.text_input("📧 E-mail", placeholder="admin@lados.com")
        senha = st.text_input("🔒 Senha", type="password", placeholder="••••••••")
        submitted = st.form_submit_button("Entrar", use_container_width=True)
        
        if submitted:
            if not email or not senha:
                st.error("❌ Preencha e-mail e senha!")
            else:
                usuario = autenticar_usuario(email, senha)
                if usuario:
                    st.session_state["autenticado"] = True
                    st.session_state["usuario"] = usuario
                    st.success(f"✅ Bem-vindo, {usuario['nome']}!")
                    st.rerun()
                else:
                    st.error("❌ E-mail ou senha incorretos!")
    
    with st.expander("ℹ️ Credenciais de teste"):
        st.markdown("""
        - **Admin:** `admin@lados.com` / `admin123`
        - **Professor:** `professor@lados.com` / `professor123`
        - **Coordenadora:** `coordenadora@lados.com` / `coord123`
        """)

def autenticar_usuario(email: str, senha: str):
    """Autentica usando arquivo JSON ou fallback embutido"""
    try:
        # Tentar ler do arquivo primeiro
        usuarios_path = Path("data/usuarios.json")
        if usuarios_path.exists():
            conteudo = usuarios_path.read_text(encoding='utf-8-sig')
            usuarios = json.loads(conteudo)
        else:
            # Usar fallback embutido
            usuarios = USUARIOS_PADRAO
        
        for usuario in usuarios:
            if usuario.get('email') == email and usuario.get('senha') == senha:
                return usuario
        return None
    except Exception as e:
        # Em caso de erro, usar fallback
        for usuario in USUARIOS_PADRAO:
            if usuario.get('email') == email and usuario.get('senha') == senha:
                return usuario
        return None

show = mostrar_login

if __name__ == "__main__":
    mostrar_login()
