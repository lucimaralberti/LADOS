import streamlit as st
from core.auth import get_current_user

def render_sidebar():
    usuario = get_current_user()

    if not usuario:
        return

    perfil = usuario.get("perfil", "professor")
    nome = usuario.get("nome", "Usuário")

    # CSS SIDEBAR
    st.markdown("""
    <style>

    /* Fundo azul oceânico */
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #1e3c72 0%, #0f1a2e 100%) !important;
    }

    /* Remove menu padrão */
    [data-testid="stSidebarNav"] {
        display: none !important;
    }

    /* Remove topo */
    [data-testid="stSidebarHeader"] {
        display: none !important;
    }

    /* Remove botão recolher */
    [data-testid="collapsedControl"] {
        display: none !important;
    }

    /* Botões */
    div.stButton > button {
        background: white !important;
        color: #1e3c72 !important;
        font-size: 14px;
        font-weight: bold;
        border: none;
        padding: 10px;
        margin: 5px 0;
        width: 100%;
        border-radius: 10px;
        transition: all 0.2s ease;
    }

    div.stButton > button:hover {
        background: #f0f0f0 !important;
        transform: translateX(5px);
    }

    
    /* Garantir que o botão SAIR apareça */
    div.stButton > button {
        display: block !important;
    }
</style>
    """, unsafe_allow_html=True)

    # SIDEBAR
    with st.sidebar:

        # ============================================
        # LOGO
        # ============================================
        st.sidebar.image("assets/logo.png", width=150)

        # NOME DO USUÁRIO
        st.markdown(f"""
        <div style="
            font-family: 'Inter', sans-serif;
            font-size: 11px;
            font-weight: 500;
            color: white;
            text-align: center;
            margin-top: 5px; margin-bottom: 20px;
        ">
            {nome}
        </div>
        """, unsafe_allow_html=True)
        # ============================================
        # PROFESSOR / COORDENADOR
        # ============================================

        if perfil == "professor" or perfil == "coordenador":

            if st.button("👤 PERFIL", key="menu_perfil", use_container_width=True):
                st.query_params["page"] = "perfil"
                st.rerun()

            if st.button("🏠 INÍCIO", key="menu_inicio", use_container_width=True):
                st.query_params["page"] = "inicio"
                st.rerun()

            if st.button("📝 QUESTÕES", key="menu_questoes", use_container_width=True):
                st.query_params["page"] = "questoes"
                st.rerun()

            if st.button("🔍 CORREÇÃO", key="menu_correcao", use_container_width=True):
                st.query_params["page"] = "correcao"
                st.rerun()

            if st.button("📊 RELATÓRIOS", key="menu_relatorios", use_container_width=True):
                st.query_params["page"] = "relatorios"
                st.rerun()

            st.markdown("---")

            if st.button("🔓 SAIR", key="menu_sair", use_container_width=True):
                for key in list(st.session_state.keys()):
                    del st.session_state[key]

                st.rerun()

        # ============================================
        # ADMINISTRADOR
        # ============================================

        elif perfil == "admin":

            if st.button("👤 PERFIL", key="admin_perfil", use_container_width=True):
                st.query_params["page"] = "perfil"
                st.rerun()

            if st.button("📋 AUDITORIA", key="admin_auditoria", use_container_width=True):
                st.query_params["page"] = "admin_auditoria"
                st.rerun()

            if st.button("💚 SAÚDE", key="admin_saude", use_container_width=True):
                st.query_params["page"] = "admin_saude"
                st.rerun()

            if st.button("👥 USUÁRIOS", key="admin_usuarios", use_container_width=True):
                st.query_params["page"] = "admin_usuarios"
                st.rerun()

            if st.button("⚙️ AJUSTES", key="admin_ajustes", use_container_width=True):
                st.query_params["page"] = "admin_ajustes"
                st.rerun()

            st.markdown("---")

            if st.button("🔓 SAIR", key="admin_sair", use_container_width=True):
                for key in list(st.session_state.keys()):
                    del st.session_state[key]

                st.rerun()

        st.caption("LADOS 2.0 - Sistema de Avaliação")