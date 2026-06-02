import streamlit as st
from core.auth import get_current_user
from core.sidebar import render_sidebar
from Login import show as mostrar_login

# Configuração da página
st.set_page_config(
    page_title="LADOS 2.0",
    page_icon="📘",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Estilo para esconder sidebar na página de login
st.markdown("""
<style>
    /* Esconder sidebar completamente na página de login */
    .stApp [data-testid="stSidebar"] {
        display: none;
    }
    .stApp [data-testid="collapsedControl"] {
        display: none;
    }
</style>
""", unsafe_allow_html=True)

def main():
    """Função principal do aplicativo"""
    
    # Verificar autenticação
    usuario = get_current_user()
    
    if not usuario:
        # Mostrar apenas o login, sem sidebar
        mostrar_login()
        return
    
    # Se estiver logado, mostrar sidebar
    if "pagina" not in st.session_state:
        st.session_state.pagina = "inicio"
    
    # Remover estilo que esconde sidebar
    st.markdown("""
    <style>
        .stApp [data-testid="stSidebar"] {
            display: flex;
        }
    </style>
    """, unsafe_allow_html=True)
    
    render_sidebar()
    
    # Navegação
    pagina = st.session_state.pagina
    
    if pagina == "inicio":
        import pages.pagina_inicio as inicio
        inicio.show()
    elif pagina == "questoes":
        import pages.pagina_questoes as questoes
        questoes.show()
    elif pagina == "correcao":
        import pages.pagina_correcao as correcao
        correcao.show()
    elif pagina == "relatorios":
        import pages.pagina_relatorios as relatorios
        relatorios.show()
    elif pagina == "perfil":
        import pages.perfil as perfil
        perfil.show()
    elif pagina.startswith("admin"):
        import importlib
        modulo = importlib.import_module(f"pages.{pagina}")
        modulo.show()
    else:
        st.session_state.pagina = "inicio"
        st.rerun()

if __name__ == "__main__":
    main()
