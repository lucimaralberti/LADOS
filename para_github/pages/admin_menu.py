import streamlit as st
from core.auth import get_current_user

def show():
    usuario = get_current_user()
    if usuario.get("perfil") != "admin":
        st.error("❌ Acesso negado.")
        st.stop()
    
    st.title("⚙️ Administração - LADOS 2.0")
    st.markdown("---")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("📋 Auditoria", use_container_width=True):
            st.session_state.pagina_atual = "admin_auditoria"
            st.rerun()
        st.caption("Logs, exportações, estatísticas")
    
    with col2:
        if st.button("📚 Gerenciar Questões", use_container_width=True):
            st.session_state.pagina_atual = "admin_questoes"
            st.rerun()
        st.caption("Importar, editar, validar")
    
    with col3:
        if st.button("👥 Gerenciar Usuários", use_container_width=True):
            st.session_state.pagina_atual = "admin_usuarios"
            st.rerun()
        st.caption("Cadastrar, editar, perfis")
    
    st.markdown("---")
    st.info("📌 Selecione uma opção acima para gerenciar o sistema.")

if __name__ == "__main__":
    show()
