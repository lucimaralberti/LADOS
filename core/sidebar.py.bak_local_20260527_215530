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

    div.stButton > button {
        display: block !important;
    }
    </style>
    """, unsafe_allow_html=True)

    # SIDEBAR
    with st.sidebar:

        # LOGO
        try:
            st.image("assets/logo.png", width=150)
        except:
            st.markdown("<div style='text-align: center; font-size: 20px; font-weight: bold; color: white;'>📘 LADOS</div>", unsafe_allow_html=True)

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

            # PERFIL
            if st.button("👤 PERFIL", key="menu_perfil", use_container_width=True):
                st.session_state.pagina = "perfil"
                st.rerun()

            # INÍCIO
            if st.button("🏠 INÍCIO", key="menu_inicio", use_container_width=True):
                st.session_state.pagina = "inicio"
                st.rerun()

            # QUESTÕES
            if st.button("📝 QUESTÕES", key="menu_questoes", use_container_width=True):
                st.session_state.pagina = "questoes"
                st.rerun()

            # CORREÇÃO
            if st.button("🔍 CORREÇÃO", key="menu_correcao", use_container_width=True):
                st.session_state.pagina = "correcao"
                st.rerun()

            # RELATÓRIOS
            if st.button("📊 RELATÓRIOS", key="menu_relatorios", use_container_width=True):
                st.session_state.pagina = "relatorios"
                st.rerun()

            st.markdown("---")

            # SAIR
            if st.button("🔓 SAIR", key="menu_sair", use_container_width=True):
                for key in list(st.session_state.keys()):
                    del st.session_state[key]
                st.rerun()

        # ============================================
        # ADMINISTRADOR
        # ============================================

        elif perfil == "admin":

            # PERFIL
            if st.button("👤 PERFIL", key="admin_perfil", use_container_width=True):
                st.session_state.pagina = "perfil"
                st.rerun()

            # AUDITORIA
            if st.button("📋 AUDITORIA", key="admin_auditoria", use_container_width=True):
                st.session_state.pagina = "admin_auditoria"
                st.rerun()

            # SAÚDE
            if st.button("💚 SAÚDE", key="admin_saude", use_container_width=True):
                st.session_state.pagina = "admin_saude"
                st.rerun()

            # USUÁRIOS
            if st.button("👥 USUÁRIOS", key="admin_usuarios", use_container_width=True):
                st.session_state.pagina = "admin_usuarios"
                st.rerun()

            # AJUSTES
            if st.button("⚙️ AJUSTES", key="admin_ajustes", use_container_width=True):
                st.session_state.pagina = "admin_ajustes"
                st.rerun()

            st.markdown("---")

            # SAIR
            if st.button("🔓 SAIR", key="admin_sair", use_container_width=True):
                for key in list(st.session_state.keys()):
                    del st.session_state[key]
                st.rerun()

        st.caption("LADOS 2.0 - Sistema de Avaliação")
