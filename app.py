import streamlit as st
from pathlib import Path

# Configuração da página (deve ser o PRIMEIRO comando)
st.set_page_config(
    page_title="LADOS 2.0",
    page_icon="📚",
    layout="wide",
    initial_sidebar_state="expanded"
)

def init_session_state():
    """Inicializa o estado da sessão"""
    if "autenticado" not in st.session_state:
        st.session_state.autenticado = False
    if "usuario" not in st.session_state:
        st.session_state.usuario = None

def main():
    """Função principal"""
    init_session_state()
    
    # Se NÃO está autenticado, mostra APENAS o login (sem sidebar)
    if not st.session_state.autenticado:
        from Login import mostrar_login
        mostrar_login()
        return
    
    # ==========================================
    # SÓ CHEGA AQUI SE ESTIVER AUTENTICADO
    # ==========================================
    
    # Sidebar apenas para usuários logados
    with st.sidebar:
        st.markdown(f"### 👤 {st.session_state.usuario.get('nome', 'Usuário')}")
        st.markdown(f"📧 {st.session_state.usuario.get('email', '')}")
        st.markdown(f"🔑 Perfil: {st.session_state.usuario.get('role', 'user').capitalize()}")
        st.markdown("---")
        
        # Menu de navegação
        menu_opcoes = ["🏠 Início", "📝 Questões", "🔍 Correção", "📊 Relatórios"]
        
        role = st.session_state.usuario.get('role', '')
        if role in ['admin', 'administrador']:
            menu_opcoes.extend(["⚙️ Admin", "👥 Usuários"])
        
        menu_opcoes.append("🚪 Sair")
        
        escolha = st.selectbox("📌 Navegação", menu_opcoes)
        
        if escolha == "🚪 Sair":
            st.session_state.autenticado = False
            st.session_state.usuario = None
            st.rerun()
    
    # Conteúdo da página principal
    st.title("📚 Sistema LADOS")
    st.markdown(f"### Bem-vindo, {st.session_state.usuario.get('nome', 'Usuário')}!")
    st.markdown("---")
    
    # Placeholder para as páginas
    st.info("Selecione uma opção no menu lateral para começar.")

if __name__ == "__main__":
    main()
