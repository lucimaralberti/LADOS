import streamlit as st
from core.auth import get_current_user
from core.sidebar import render_sidebar
from Login import mostrar_login

st.set_page_config(page_title="LADOS 2.0", page_icon="📘", layout="wide")

if "usuario" not in st.session_state:
    mostrar_login()
    st.stop()

# Sidebar
render_sidebar()

# Roteamento
page = st.query_params.get("page", "inicio")

if page == "inicio":
    import pages.pagina_inicio as inicio
    inicio.show()
elif page == "questoes":
    import pages.pagina_questoes as questoes
    questoes.show()
elif page == "correcao":
    import pages.pagina_correcao as correcao
    correcao.show()
elif page == "relatorios":
    import pages.pagina_relatorios as relatorios
    relatorios.show()
elif page == "admin_dashboard":
    import pages.admin_dashboard as admin
    admin.show()
elif page == "admin_auditoria":
    import pages.admin_auditoria as admin_auditoria
    admin_auditoria.show()
elif page == "admin_saude":
    import pages.admin_saude as admin_saude
    admin_saude.show()
elif page == "admin_usuarios":
    import pages.admin_usuarios as admin_usuarios
    admin_usuarios.show()
elif page == "admin_ajustes":
    import pages.admin_ajustes as admin_ajustes
    admin_ajustes.show()
else:
    import pages.pagina_inicio as inicio
    inicio.show()
