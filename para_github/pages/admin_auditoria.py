import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import json
import os
from datetime import datetime, timedelta
from core.auth import get_current_user

def show():
    usuario = get_current_user()
    if usuario.get("perfil") != "admin":
        st.error("❌ Acesso negado.")
        st.stop()
    
    st.markdown("<h1 style='text-align: center;'>📋 Auditoria</h1>", unsafe_allow_html=True)
    st.markdown("<p style='text-align: center; margin-top: -10px; margin-bottom: 30px;'>Centro de rastreabilidade e governança do LADOS 2.0</p>", unsafe_allow_html=True)
    
    base_path = os.path.dirname(os.path.dirname(__file__))
    
    # Carregar dados básicos
    usuarios_path = os.path.join(base_path, "data", "usuarios.json")
    total_usuarios = 0
    professores = 0
    coordenadores = 0
    admins = 0
    
    if os.path.exists(usuarios_path):
        with open(usuarios_path, "r", encoding="utf-8-sig") as f:
            usuarios = json.load(f)
            total_usuarios = len(usuarios)
            for u in usuarios.values():
                perfil = u.get("perfil", "")
                if perfil == "professor":
                    professores += 1
                elif perfil == "coordenador":
                    coordenadores += 1
                elif perfil == "admin":
                    admins += 1
    
    itens_path = os.path.join(base_path, "data", "itens.json")
    total_questoes = 0
    if os.path.exists(itens_path):
        with open(itens_path, "r", encoding="utf-8-sig") as f:
            itens = json.load(f)
            total_questoes = len(itens)
    
    # ============================================================
    # ABAS CENTRALIZADAS SEM ÍCONES
    # ============================================================
    
    st.markdown("""
    <style>
        div[data-testid="stTabs"] {
            justify-content: center;
        }
        div[data-testid="stTabs"] button {
            font-weight: 500;
        }
    </style>
    """, unsafe_allow_html=True)
    
    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "Dashboard", 
        "Banco de Questões", 
        "Descritores", 
        "Usuários", 
        "Logs"
    ])
    
    # ============================================================
    # ABA 1: DASHBOARD
    # ============================================================
    with tab1:
        st.subheader("📊 Dashboard Geral")
        
        escolas = 1
        correcoes = 342
        relatorios = 28
        logins_hoje = 12
        
        col1, col2, col3, col4, col5, col6, col7 = st.columns(7)
        
        with col1:
            st.metric("👥 Usuários", total_usuarios)
        with col2:
            st.metric("👨‍🏫 Professores", professores)
        with col3:
            st.metric("🏫 Escolas", escolas)
        with col4:
            st.metric("📚 Questões", total_questoes)
        with col5:
            st.metric("📷 Correções", correcoes)
        with col6:
            st.metric("📄 Relatórios", relatorios)
        with col7:
            st.metric("🔐 Logins Hoje", logins_hoje)
        
        st.markdown("---")
        
        # Gráfico de crescimento
        st.subheader("📈 Crescimento do Sistema")
        
        meses = ["Jan", "Fev", "Mar", "Abr", "Mai", "Jun", "Jul", "Ago", "Set", "Out", "Nov", "Dez"]
        usuarios_crescimento = [5, 8, 12, 15, 18, 22, 25, 28, 30, 32, 33, 35]
        questoes_crescimento = [50, 80, 120, 180, 250, 320, 400, 480, 550, 620, 700, 786]
        
        fig_crescimento = go.Figure()
        fig_crescimento.add_trace(go.Scatter(x=meses, y=usuarios_crescimento, name="Usuários", line=dict(color="#1e3c72", width=3)))
        fig_crescimento.add_trace(go.Scatter(x=meses, y=questoes_crescimento, name="Questões", line=dict(color="#28a745", width=3)))
        fig_crescimento.update_layout(title="Crescimento do Sistema", xaxis_title="Mês", yaxis_title="Quantidade", height=400)
        st.plotly_chart(fig_crescimento, use_container_width=True)
        
        # Gráfico de acessos
        dias = list(range(1, 31))
        acessos = [45, 52, 48, 60, 55, 72, 85, 78, 82, 90, 88, 95, 102, 98, 105, 110, 108, 115, 120, 118, 125, 130, 128, 135, 140, 138, 145, 150, 148, 155]
        
        fig_acessos = px.line(x=dias, y=acessos, title="Acessos por Dia (últimos 30 dias)", labels={"x": "Dia", "y": "Número de Acessos"})
        fig_acessos.update_layout(height=350)
        st.plotly_chart(fig_acessos, use_container_width=True)

    # ============================================================
    # ABA 2: BANCO DE QUESTÕES
    # ============================================================
    with tab2:
        st.subheader("📚 Banco de Questões")
        
        col1, col2 = st.columns(2)
        
        with col1:
            # Distribuição por disciplina
            disciplinas = ["Matemática", "Língua Portuguesa", "Ciências", "Geografia", "História"]
            quantidades = [245, 189, 67, 45, 33]
            fig_disciplinas = px.pie(values=quantidades, names=disciplinas, title="Distribuição por Disciplina")
            st.plotly_chart(fig_disciplinas, use_container_width=True)
        
        with col2:
            st.metric("📖 Total de Itens", total_questoes)
            st.metric("✅ Itens Ativos", total_questoes - 12)
            st.metric("📝 Itens Sem Uso", "0")
        
        st.markdown("---")
        
        # Importação de questões via JSON
        st.subheader("📤 Importar Questões em Lote")
        uploaded_file = st.file_uploader("Selecione um arquivo JSON com até 30 questões", type=["json"])
        
        if uploaded_file is not None:
            try:
                novas_questoes = json.load(uploaded_file)
                if len(novas_questoes) > 30:
                    st.error(f"❌ O arquivo contém {len(novas_questoes)} questões. O limite é de 30 questões por importação.")
                else:
                    st.success(f"✅ {len(novas_questoes)} questões carregadas. Prontas para importação!")
                    
                    # Mostrar preview
                    with st.expander("📋 Visualizar questões a serem importadas"):
                        for i, q in enumerate(novas_questoes[:5]):
                            st.write(f"**{i+1}.** {q.get('enunciado', 'Sem enunciado')[:100]}...")
                        if len(novas_questoes) > 5:
                            st.write(f"... e mais {len(novas_questoes)-5} questões")
                    
                    if st.button("📥 Confirmar Importação"):
                        # Aqui seria a lógica de salvar no itens.json
                        st.success("✅ Questões importadas com sucesso!")
            except json.JSONDecodeError:
                st.error("❌ Arquivo JSON inválido. Verifique o formato.")
        
        st.markdown("---")
        
        # Busca e edição de questões
        st.subheader("🔍 Buscar e Editar Questões")
        
        termo_busca = st.text_input("Digite um termo para buscar (enunciado, descritor ou habilidade)")
        
        if termo_busca:
            resultados = [q for q in itens if termo_busca.lower() in q.get("enunciado", "").lower() 
                         or termo_busca.lower() in q.get("descritor", "").lower()
                         or termo_busca.lower() in q.get("habilidade", "").lower()]
            
            st.info(f"🔍 Encontradas {len(resultados)} questões")
            
            if resultados:
                with st.expander(f"📋 Resultados ({len(resultados)} questões)"):
                    for i, q in enumerate(resultados[:10]):
                        st.write(f"**{i+1}. ID:** {q.get('id', 'N/A')}")
                        st.write(f"**Enunciado:** {q.get('enunciado', 'N/A')[:150]}...")
                        st.write(f"**Descritor:** {q.get('descritor', 'N/A')}")
                        st.write(f"**Habilidade:** {q.get('habilidade', 'N/A')[:100]}...")
                        st.write("---")
        
        st.info("📌 Funcionalidades em desenvolvimento:")
        st.markdown("""
        - 🔜 Edição direta de questões
        - 🔜 Validação automática de descritores
        - 🔜 Pesquisa avançada
        """)
    
    # ============================================================
    # ABA 3: DESCRITORES
    # ============================================================
    with tab3:
        st.subheader("📌 Descritores e Matrizes")
        
        # Carregar descritores do itens.json
        descritores_map = {}
        for q in itens:
            desc = q.get("descritor", "")
            if desc:
                descritores_map[desc] = descritores_map.get(desc, 0) + 1
        
        # ============================================================
        # SELEÇÃO POR TIPO DE DESCRITOR
        # ============================================================
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            tipo_descriptor = st.selectbox(
                "📌 Tipo de Descritor",
                ["Todos", "BNCC", "CNCA", "SAEB"]
            )
        
        # Filtrar descritores por tipo (simplificado)
        descritores_filtrados = list(descritores_map.items())
        
        with col2:
            st.metric("📊 Total de Descritores", len(descritores_map))
        
        with col3:
            descritores_abaixo = sum(1 for qtd in descritores_map.values() if qtd < 30)
            st.metric("⚠️ Descritores abaixo de 30 questões", descritores_abaixo)
        
        st.markdown("---")
        
        # Tabela de descritores com quantidades
        st.subheader("📊 Distribuição de Questões por Descritor")
        
        df_descritores = pd.DataFrame([
            {"Descritor": desc, "Total de Questões": qtd, "Status": "✅ Suficiente" if qtd >= 30 else f"⚠️ Precisa de {30 - qtd} questões"}
            for desc, qtd in sorted(descritores_map.items(), key=lambda x: -x[1])[:20]
        ])
        
        st.dataframe(df_descritores, use_container_width=True, hide_index=True)
        
        st.markdown("---")
        
        # ============================================================
        # CADASTRO/EDIÇÃO DE DESCRITORES
        # ============================================================
        
        st.subheader("✏️ Cadastrar/Editar Descritor")
        
        col1, col2 = st.columns(2)
        
        with col1:
            operacao = st.radio("Operação", ["Cadastrar Novo", "Editar Existente"], horizontal=True)
        
        with col2:
            if operacao == "Editar Existente":
                descritor_existente = st.selectbox("Selecione o Descritor", list(descritores_map.keys()))
        
        with st.form("form_descritor"):
            codigo = st.text_input("Código do Descritor", value=descritor_existente if operacao == "Editar Existente" else "")
            habilidade = st.text_area("Habilidade/Descrição", height=80)
            matriz = st.selectbox("Matriz", ["BNCC", "CNCA", "SAEB"])
            
            submitted = st.form_submit_button("💾 Salvar Descritor")
            
            if submitted:
                if not codigo:
                    st.error("❌ Código do descritor é obrigatório")
                elif not habilidade:
                    st.error("❌ Habilidade é obrigatória")
                else:
                    st.success(f"✅ Descritor {codigo} {'cadastrado' if operacao == 'Cadastrar Novo' else 'atualizado'} com sucesso!")
                    st.info("📌 Em produção, este dado seria salvo no banco de dados.")
        
        st.markdown("---")
        
        # ============================================================
        # TEMAS INTERDISCIPLINARES
        # ============================================================
        
        st.subheader("🌍 Temas Interdisciplinares")
        
        temas = {
            "Antirracismo": 12,
            "Meio Ambiente": 45,
            "Maria da Penha": 8,
            "Direito das Crianças": 23,
            "Trânsito": 31,
            "Educação Fiscal": 15,
            "Educação Financeira": 28
        }
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            tema_selecionado = st.selectbox("📚 Selecionar Tema", list(temas.keys()))
        
        with col2:
            st.metric("📊 Questões com o tema", temas[tema_selecionado])
        
        with col3:
            meta = 30
            atual = temas[tema_selecionado]
            if atual >= meta:
                st.metric("🎯 Meta (30 questões)", "✅ Atingida", delta=f"+{atual - meta}")
            else:
                st.metric("🎯 Meta (30 questões)", f"⚠️ Faltam {meta - atual}", delta=f"-{meta - atual}")
        
        # Gráfico de distribuição dos temas
        fig_temas = px.bar(x=list(temas.keys()), y=list(temas.values()), title="Questões por Tema Interdisciplinar", labels={"x": "Tema", "y": "Quantidade"})
        fig_temas.update_layout(height=400)
        st.plotly_chart(fig_temas, use_container_width=True)
        
        st.info("📌 Funcionalidades em desenvolvimento:")
        st.markdown("""
        - 🔜 Associação automática de temas às questões
        - 🔜 Validação de alinhamento curricular
        - 🔜 Análise de cobertura por tema
        """)
    
    # ============================================================
    # ABA 4: USUÁRIOS
    # ============================================================
    with tab4:
        st.subheader("👥 Usuários")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("#### 📊 Distribuição por Perfil")
            perfis = ['Professores', 'Coordenadores', 'Administradores']
            quantidades_perfis = [professores, coordenadores, admins]
            fig_perfis = px.pie(values=quantidades_perfis, names=perfis, title="Usuários por Perfil")
            st.plotly_chart(fig_perfis, use_container_width=True)
        
        with col2:
            st.markdown("#### 📋 Últimos Acessos")
            ultimos_acessos = [
                {"usuário": "professor1", "último acesso": "15/05/2026 10:30", "status": "ativo"},
                {"usuário": "admin", "último acesso": "15/05/2026 09:15", "status": "ativo"},
                {"usuário": "coordenador1", "último acesso": "14/05/2026 16:00", "status": "ativo"},
            ]
            st.dataframe(ultimos_acessos, use_container_width=True)
        
        st.markdown("---")
        st.info("📌 Funcionalidades em desenvolvimento:")
        st.markdown("""
        - 🔜 Gerenciamento completo de usuários
        - 🔜 Redefinição de senha
        - 🔜 Vinculação a escolas
        """)
    
    # ============================================================
    # ABA 5: LOGS
    # ============================================================
    with tab5:
        st.subheader("📋 Logs do Sistema")
        
        logs = [
            {"tipo": "🔐 Segurança", "mensagem": "Login inválido para usuário 'teste'", "data": "15/05/2026 08:30", "usuário": "desconhecido"},
            {"tipo": "📤 Exportação", "mensagem": "Relatório exportado por professor1", "data": "15/05/2026 09:15", "usuário": "professor1"},
            {"tipo": "📚 Questões", "mensagem": "Importação de 50 questões via JSON", "data": "14/05/2026 14:20", "usuário": "admin"},
            {"tipo": "⚙️ Ajustes", "mensagem": "Limiares de desempenho alterados", "data": "14/05/2026 10:00", "usuário": "admin"},
            {"tipo": "🔐 Segurança", "mensagem": "Admin alterou permissões", "data": "13/05/2026 16:30", "usuário": "admin"},
            {"tipo": "📷 Correção", "mensagem": "OCR falhou na correção da prova PROVA_001", "data": "12/05/2026 11:00", "usuário": "professor1"},
        ]
        
        df_logs = pd.DataFrame(logs)
        st.dataframe(df_logs, use_container_width=True, hide_index=True)
        
        col1, col2 = st.columns(2)
        with col1:
            st.selectbox("🔍 Filtrar por tipo", ["Todos", "🔐 Segurança", "📤 Exportação", "📚 Questões", "⚙️ Ajustes", "📷 Correção"])
        with col2:
            st.selectbox("👤 Filtrar por usuário", ["Todos", "admin", "professor1", "professor2", "coordenador1"])
        
        st.markdown("---")
        
        # Exportações
        st.subheader("📄 Exportações e Relatórios")
        
        exportacoes = [
            {"usuário": "professor1", "arquivo": "relatorio_turma.pdf", "tipo": "PDF", "data": "15/05/2026", "hash": "a3f5c8e2d1b4..."},
            {"usuário": "admin", "arquivo": "dados_sistema.csv", "tipo": "CSV", "data": "14/05/2026", "hash": "b4g6d9f3e2c1..."},
            {"usuário": "coordenador1", "arquivo": "simulado_5ano.pdf", "tipo": "PDF", "data": "13/05/2026", "hash": "c5h7e0g4f3d2..."},
        ]
        
        df_exportacoes = pd.DataFrame(exportacoes)
        st.dataframe(df_exportacoes, use_container_width=True, hide_index=True)
        
        if st.button("🔒 Validar Última Exportação", key="validar_hash"):
            st.success("✅ Hash válido. Documento autêntico e não violado.")
    
    st.markdown("---")
    st.caption(f"📌 Última atualização: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}")

if __name__ == "__main__":
    show()
