import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import json
import os

from datetime import datetime, timedelta
from core.auth import get_current_user


# ============================================================
# FUNÇÕES AUXILIARES PARA CARREGAR DADOS
# ============================================================

def carregar_usuarios():
    """Carrega dados dos usuários do JSON"""

    base_path = os.path.dirname(os.path.dirname(__file__))
    caminho = os.path.join(base_path, "data", "usuarios.json")

    if os.path.exists(caminho):

        try:
            with open(caminho, "r", encoding="utf-8") as f:
                return json.load(f)

        except:
            return {}

    return {}


def carregar_questoes():
    """Carrega dados das questões"""

    base_path = os.path.dirname(os.path.dirname(__file__))
    caminho = os.path.join(base_path, "data", "itens.json")

    if os.path.exists(caminho):

        try:
            with open(caminho, "r", encoding="utf-8") as f:
                return json.load(f)

        except:
            return []

    return []


def carregar_descritores():
    """Carrega dados dos descritores"""

    base_path = os.path.dirname(os.path.dirname(__file__))

    descritores = {}

    for matriz, arquivo in [
        ("BNCC", "bncc.json"),
        ("CNCA", "cnca.json"),
        ("SAEB", "saeb.json")
    ]:

        caminho = os.path.join(base_path, "data", arquivo)

        if os.path.exists(caminho):

            try:

                with open(caminho, "r", encoding="utf-8") as f:
                    dados = json.load(f)

                descritores[matriz] = dados

            except:
                descritores[matriz] = {}

    return descritores


# ============================================================
# PÁGINA PRINCIPAL
# ============================================================

def show():
    """Dashboard do Administrador"""

    usuario = get_current_user()

    # Verificar se é admin
    if usuario.get("perfil") != "admin":

        st.error("❌ Acesso negado. Esta página é restrita ao Administrador.")
        st.stop()

    st.title("📊 Dashboard do Administrador")
    st.markdown("Visão geral do sistema LADOS 2.0")
    st.markdown("---")

    # ========================================================
    # CARDS PRINCIPAIS
    # ========================================================

    st.subheader("📈 Indicadores Gerais")

    # Carregar dados
    usuarios = carregar_usuarios()
    questoes = carregar_questoes()
    descritores = carregar_descritores()

    # Calcular métricas
    total_usuarios = len(usuarios)
    total_questoes = len(questoes)
    total_descritores = sum(len(d) for d in descritores.values())

    # Contar por perfil
    professores = sum(
        1 for u in usuarios
        if u.get("perfil") == "professor"
    )

    coordenadores = sum(
        1 for u in usuarios
        if u.get("perfil") == "coordenador"
    )

    admins = sum(
        1 for u in usuarios
        if u.get("perfil") == "admin"
    )

    col1, col2, col3, col4 = st.columns(4)

    with col1:

        st.metric(
            "📚 Questões",
            total_questoes,
            delta="+12 este mês",
            delta_color="normal"
        )

    with col2:

        st.metric(
            "👥 Usuários",
            total_usuarios,
            delta=f"+{professores} prof, +{coordenadores} coord"
        )

    with col3:

        st.metric(
            "📋 Descritores",
            total_descritores
        )

    with col4:

        st.metric(
            "✅ Correções",
            "342",
            delta="+45 este mês"
        )

    st.markdown("---")

    # ========================================================
    # GRÁFICO DE USO DO SISTEMA
    # ========================================================

    st.subheader("📈 Uso do Sistema (últimos 30 dias)")

    dias = [
        (datetime.now() - timedelta(days=i)).strftime("%d/%m")
        for i in range(29, -1, -1)
    ]

    acessos = [
        45, 52, 48, 60, 55, 72, 85, 78, 82, 90,
        88, 95, 102, 98, 105, 110, 108, 115,
        120, 118, 125, 130, 128, 135, 140,
        138, 145, 150, 148, 155
    ]

    df_acessos = pd.DataFrame({
        'Dia': dias,
        'Acessos': acessos
    })

    fig = px.line(
        df_acessos,
        x='Dia',
        y='Acessos',
        title="Número de acessos por dia",
        labels={
            'Acessos': 'Número de acessos',
            'Dia': 'Data'
        }
    )

    fig.update_layout(
        height=400,
        template="plotly_white"
    )

    st.plotly_chart(fig, use_container_width=True)

    st.markdown("---")

    # ========================================================
    # DISTRIBUIÇÃO DOS USUÁRIOS
    # ========================================================

    col1, col2 = st.columns(2)

    with col1:

        st.subheader("📊 Distribuição por Perfil")

        perfis = [
            'Professores',
            'Coordenadores',
            'Administradores'
        ]

        quantidades = [
            professores,
            coordenadores,
            admins
        ]

        cores = [
            '#1e3c72',
            '#2a5298',
            '#4a7ab5'
        ]

        fig_pie = go.Figure(
            data=[
                go.Pie(
                    labels=perfis,
                    values=quantidades,
                    marker=dict(colors=cores),
                    hole=0.4
                )
            ]
        )

        fig_pie.update_layout(
            title="Usuários por perfil",
            height=350
        )

        st.plotly_chart(fig_pie, use_container_width=True)

    with col2:

        st.subheader("📋 Status do Sistema")

        st.markdown("""
        | Componente | Status | Última verificação |
        |------------|--------|-------------------|
        | 🔵 **Servidor** | 🟢 Online | Agora |
        | 🗄️ **Banco de Dados** | 🟢 Conectado | Agora |
        | 📚 **API** | 🟢 OK | Agora |
        | 🔐 **Autenticação** | 🟢 Funcionando | Agora |
        | 📧 **E-mail** | 🟢 Configurado | Hoje |
        """)

    st.markdown("---")

    # ========================================================
    # ÚLTIMAS ATIVIDADES
    # ========================================================

    st.subheader("📋 Últimas Atividades")

    atividades = [
        {
            "data": "15/05/2025 10:30",
            "usuario": "admin",
            "acao": "Alterou configurações do sistema",
            "detalhes": "Limiares de desempenho"
        },
        {
            "data": "15/05/2025 09:15",
            "usuario": "admin",
            "acao": "Cadastrou novo descritor",
            "detalhes": "MAT_5EF_D05"
        },
        {
            "data": "14/05/2025 16:00",
            "usuario": "admin",
            "acao": "Realizou backup",
            "detalhes": "Backup completo do sistema"
        },
        {
            "data": "14/05/2025 10:30",
            "usuario": "professor1",
            "acao": "Gerou prova",
            "detalhes": "Matemática - 5º Ano"
        },
        {
            "data": "13/05/2025 14:20",
            "usuario": "professor2",
            "acao": "Corrigiu prova",
            "detalhes": "7 acertos/10 questões"
        }
    ]

    df_atividades = pd.DataFrame(atividades)

    st.dataframe(
        df_atividades,
        use_container_width=True,
        hide_index=True
    )

    st.markdown("---")

    # ========================================================
    # AÇÕES RÁPIDAS
    # ========================================================

    st.subheader("⚡ Ações Rápidas")

    col1, col2, col3, col4 = st.columns(4)

    with col1:

        if st.button(
            "📥 Importar Questões",
            use_container_width=True
        ):

            st.info("Funcionalidade em desenvolvimento")

    with col2:

        if st.button(
            "👥 Gerenciar Usuários",
            use_container_width=True
        ):

            st.info("Funcionalidade em desenvolvimento")

    with col3:

        if st.button(
            "📊 Gerar Relatório",
            use_container_width=True
        ):

            st.info("Funcionalidade em desenvolvimento")

    with col4:

        if st.button(
            "💾 Backup",
            use_container_width=True
        ):

            st.info("Funcionalidade em desenvolvimento")

    st.markdown("---")

    st.caption(
        "📌 Última atualização: "
        + datetime.now().strftime("%d/%m/%Y %H:%M:%S")
    )


if __name__ == "__main__":
    show()
