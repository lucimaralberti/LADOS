import streamlit as st

# Configuração da página
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
    """Função principal do aplicativo"""
    init_session_state()
    
    # Se não está autenticado, mostra o login
    if not st.session_state.autenticado:
        from Login import mostrar_login
        mostrar_login()
        return
    
    # Se está autenticado, mostra o menu principal
    st.sidebar.title("📚 Sistema LADOS")
    st.sidebar.markdown(f"### 👤 {st.session_state.usuario.get('nome', 'Usuário')}")
    st.sidebar.markdown(f"📧 {st.session_state.usuario.get('email', '')}")
    st.sidebar.markdown(f"🔑 Perfil: {st.session_state.usuario.get('role', 'user').capitalize()}")
    st.sidebar.markdown("---")
    
    # Menu de navegação
    menu_opcoes = ["🏠 Início", "📝 Questões", "🔍 Correção", "📊 Relatórios"]
    
    # Adiciona opções de admin se for administrador
    role = st.session_state.usuario.get('role', '')
    if role in ['admin', 'administrador']:
        menu_opcoes.extend(["⚙️ Admin", "👥 Usuários"])
    
    menu_opcoes.append("🚪 Sair")
    
    escolha = st.sidebar.selectbox("📌 Navegação", menu_opcoes)
    
    # Processa a escolha
    if escolha == "🚪 Sair":
        st.session_state.autenticado = False
        st.session_state.usuario = None
        st.rerun()
    
    elif escolha == "🏠 Início":
        st.info("📄 Página Início - Em desenvolvimento")
    
    elif escolha == "📝 Questões":
        st.info("📄 Página Questões - Em desenvolvimento")
    
    elif escolha == "🔍 Correção":
        st.info("📄 Página Correção - Em desenvolvimento")
    
    elif escolha == "📊 Relatórios":
        st.info("📄 Página Relatórios - Em desenvolvimento")
    
    elif escolha == "⚙️ Admin" and role in ['admin', 'administrador']:
        st.info("⚙️ Painel Admin - Em desenvolvimento")
    
    elif escolha == "👥 Usuários" and role in ['admin', 'administrador']:
        st.info("👥 Gerenciar Usuários - Em desenvolvimento")

if __name__ == "__main__":
    main()
