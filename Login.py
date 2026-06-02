import streamlit as st
import json
from pathlib import Path

def mostrar_login():
    """Função de login - sem sidebar"""
    
    # Esconder header e sidebar
    st.markdown(
        """
        <style>
            header {visibility: hidden;}
            .stApp > header {display: none;}
        </style>
        """,
        unsafe_allow_html=True
    )
    
    # Container centralizado
    with st.container():
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
                    usuario = autenticar_local(email, senha)
                    
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

def autenticar_local(email: str, senha: str):
    """Autenticação usando arquivo JSON (leitura robusta)"""
    try:
        usuarios_path = Path("data/usuarios.json")
        if not usuarios_path.exists():
            st.error("Arquivo de usuários não encontrado!")
            return None
        
        # Ler o arquivo tratando possíveis BOM
        conteudo = usuarios_path.read_text(encoding='utf-8-sig')
        usuarios = json.loads(conteudo)
        
        for usuario in usuarios:
            if usuario.get('email') == email and usuario.get('senha') == senha:
                return {
                    'id': usuario.get('id'),
                    'email': usuario.get('email'),
                    'nome': usuario.get('nome'),
                    'role': usuario.get('role', 'professor')
                }
        return None
    except Exception as e:
        st.error(f"Erro na autenticação: {e}")
        return None

# Para compatibilidade
show = mostrar_login

if __name__ == "__main__":
    mostrar_login()
