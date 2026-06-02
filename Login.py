import streamlit as st
from services.auth_service import AuthService

def mostrar_login():
    """Função de login para ser chamada pelo app.py"""
    st.title("📚 Sistema LADOS")
    st.markdown("### Diagnóstico Pedagógico Inteligente")
    st.markdown("---")
    
    @st.cache_resource
    def get_auth():
        return AuthService(usar_supabase=True)
    
    auth = get_auth()
    
    with st.form("login_form"):
        email = st.text_input("📧 E-mail", placeholder="admin@lados.com")
        senha = st.text_input("🔒 Senha", type="password", placeholder="••••••••")
        submitted = st.form_submit_button("Entrar", use_container_width=True)
        
        if submitted:
            if not email or not senha:
                st.error("❌ Preencha e-mail e senha!")
            else:
                with st.spinner("Conectando..."):
                    usuario = auth.autenticar(email, senha)
                
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
        """)

if __name__ == "__main__":
    mostrar_login()
