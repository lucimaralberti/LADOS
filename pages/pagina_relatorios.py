import streamlit as st

import pandas as pd
from datetime import datetime
from core.auth import get_current_user
from services.exportador_resultados import (
    exportador, analise_desempenho, integracao_supabase, dashboard
)

def show():
    usuario = get_current_user()
    
    st.title("📊 Relatórios e Análises")
    st.caption("Análise de desempenho, exportação de resultados e histórico")
    
    if not usuario:
        st.error("⚠️ Usuário não autenticado")
        return
    
    # ========== SELEÇÃO DE DADOS ==========
    st.subheader("1️⃣ Selecionar Dados")
    
    col1, col2 = st.columns(2)
    
    with col1:
        turmas = ["5º Ano A", "5º Ano B", "5º Ano C", "6º Ano A", "6º Ano B"]
        turma_selecionada = st.selectbox("🏫 Turma", turmas)
    
    with col2:
        provas = ["Matemática - 3º Ano", "Português - 3º Ano", "Ciências - 3º Ano", "Todas"]
        prova_selecionada = st.selectbox("📄 Prova", provas)
    
    # ========== SIMULAÇÃO DE DADOS (mock) ==========
    # TODO: Substituir por dados reais do Supabase
    dados_mock = [
        {"numero_prova": 1, "acertos": 8, "total": 10, "percentual": 80, "nota": 8.0, 
         "horario": "08:30", "data": "20/05/2026", "timestamp": "2026-05-20T08:30:00"},
        {"numero_prova": 2, "acertos": 7, "total": 10, "percentual": 70, "nota": 7.0, 
         "horario": "08:35", "data": "20/05/2026", "timestamp": "2026-05-20T08:35:00"},
        {"numero_prova": 3, "acertos": 9, "total": 10, "percentual": 90, "nota": 9.0, 
         "horario": "08:40", "data": "20/05/2026", "timestamp": "2026-05-20T08:40:00"},
        {"numero_prova": 4, "acertos": 6, "total": 10, "percentual": 60, "nota": 6.0, 
         "horario": "08:45", "data": "20/05/2026", "timestamp": "2026-05-20T08:45:00"},
        {"numero_prova": 5, "acertos": 8, "total": 10, "percentual": 80, "nota": 8.0, 
         "horario": "08:50", "data": "20/05/2026", "timestamp": "2026-05-20T08:50:00"},
    ]
    
    # Adicionar detalhes mock para análise de descritores
    for i, d in enumerate(dados_mock):
        d["detalhes"] = [
            {"questao": 1, "acertou": True, "descritor": "EF05MA01", "disciplina": "Matemática"},
            {"questao": 2, "acertou": True, "descritor": "EF05MA02", "disciplina": "Matemática"},
            {"questao": 3, "acertou": i % 2 == 0, "descritor": "EF05MA03", "disciplina": "Matemática"},
            {"questao": 4, "acertou": i % 3 == 0, "descritor": "EF05LP01", "disciplina": "Português"},
            {"questao": 5, "acertou": i % 2 == 1, "descritor": "EF05LP02", "disciplina": "Português"},
        ]
        d["disciplina"] = "Matemática" if i % 2 == 0 else "Português"
    
    st.markdown("---")
    
    # ========== 9. EXPORTAÇÃO DE RESULTADOS ==========
    st.subheader("2️⃣ Exportar Resultados")
    
    col_exp1, col_exp2, col_exp3 = st.columns(3)
    
    with col_exp1:
        if st.button("📄 Exportar CSV", use_container_width=True):
            csv_data = exportador.exportar_csv(dados_mock, f"relatorio_{turma_selecionada}")
            st.download_button(
                label="⬇️ Baixar CSV",
                data=csv_data,
                file_name=f"relatorio_{turma_selecionada}_{datetime.now().strftime('%Y%m%d')}.csv",
                mime="text/csv"
            )
    
    with col_exp2:
        if st.button("📊 Exportar Excel", use_container_width=True):
            excel_data = exportador.exportar_excel(dados_mock, f"relatorio_{turma_selecionada}")
            st.download_button(
                label="⬇️ Baixar Excel",
                data=excel_data,
                file_name=f"relatorio_{turma_selecionada}_{datetime.now().strftime('%Y%m%d')}.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )
    
    with col_exp3:
        if st.button("📑 Exportar PDF", use_container_width=True):
            pdf_data = exportador.exportar_pdf_relatorio(
                dados_mock, turma_selecionada, prova_selecionada, datetime.now()
            )
            st.download_button(
                label="⬇️ Baixar PDF",
                data=pdf_data,
                file_name=f"relatorio_{turma_selecionada}_{datetime.now().strftime('%Y%m%d')}.pdf",
                mime="application/pdf"
            )
    
    st.markdown("---")
    
    # ========== 10. DASHBOARD DE DESEMPENHO ==========
    st.subheader("3️⃣ Dashboard Interativo")
    
    # Usar a classe DashboardDesempenho
    dashboard.exibir_dashboard(dados_mock)
    
    st.markdown("---")
    
    # ========== 11. ANÁLISE DE DISTRATORES ==========
    st.subheader("4️⃣ Análise de Distratores")
    
    tab1, tab2, tab3 = st.tabs(["📊 Por Descritor", "📈 Por Disciplina", "🎯 Distratores"])
    
    with tab1:
        # Análise por descritor
        analise_descritores = analise_desempenho.analisar_por_descritor(dados_mock)
        if not analise_descritores.empty:
            st.dataframe(analise_descritores, use_container_width=True)
            
            # Gráfico de barras
            import plotly.express as px
            fig = px.bar(analise_descritores.reset_index(), 
                         x='descritor', y='percentual_acerto',
                         title="Percentual de Acerto por Descritor",
                         labels={'percentual_acerto': '% de Acerto', 'descritor': 'Descritor'})
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("Nenhum dado disponível para análise por descritor")
    
    with tab2:
        # Análise por disciplina
        analise_disciplinas = analise_desempenho.analisar_por_disciplina(dados_mock)
        if not analise_disciplinas.empty:
            st.dataframe(analise_disciplinas, use_container_width=True)
            
            # Gráfico de pizza
            import plotly.express as px
            fig = px.pie(analise_disciplinas.reset_index(), 
                         values='percentual_acerto', names='disciplina',
                         title="Percentual de Acerto por Disciplina")
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("Nenhum dado disponível para análise por disciplina")
    
    with tab3:
        # Análise de distratores
        analise_distratores = analise_desempenho.analise_distorcedores(dados_mock)
        if not analise_distratores.empty:
            st.dataframe(analise_distratores, use_container_width=True)
            st.caption("Quais alternativas erradas foram mais escolhidas pelos alunos")
        else:
            st.info("Nenhum erro detectado para análise de distratores")
    
    st.markdown("---")
    
    # ========== 15. INTEGRAÇÃO COM SUPABASE ==========
    st.subheader("5️⃣ Integração com Supabase")
    
    col_sup1, col_sup2 = st.columns(2)
    
    with col_sup1:
        if st.button("💾 Salvar Sessão no Supabase", use_container_width=True):
            with st.spinner("Salvando dados..."):
                sucesso = integracao_supabase.salvar_sessao(
                    sessao_id="TESTE_001",
                    correcoes=dados_mock,
                    periodo="1º Bimestre",
                    ordem="Primeiro",
                    prova=prova_selecionada,
                    turma=turma_selecionada,
                    usuario=usuario
                )
                if sucesso:
                    st.success("✅ Sessão salva com sucesso!")
                else:
                    st.warning("⚠️ Modo de demonstração - Conecte ao Supabase para salvar")
    
    with col_sup2:
        if st.button("📥 Recuperar Histórico", use_container_width=True):
            with st.spinner("Carregando histórico..."):
                historico = integracao_supabase.recuperar_historico(turma_selecionada, prova_selecionada)
                if historico:
                    st.dataframe(pd.DataFrame(historico), use_container_width=True)
                else:
                    st.info("Nenhum histórico encontrado (modo de demonstração)")
    
    st.markdown("---")
    st.caption("📌 Os dados exibidos são de demonstração. Conecte ao Supabase para dados reais.")

if __name__ == "__main__":
    show()


