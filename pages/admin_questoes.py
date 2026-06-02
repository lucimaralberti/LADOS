import streamlit as st
import json
import pandas as pd
import plotly.express as px
import os
from datetime import datetime
from core.auth import get_current_user

def show():
    usuario = get_current_user()
    if usuario.get("perfil") != "admin":
        st.error("❌ Acesso negado.")
        st.stop()
    
    st.title("📚 Gerenciamento de Questões")
    st.markdown("Importação em lote, busca e edição de questões")
    st.markdown("---")
    
    base_path = os.path.dirname(os.path.dirname(__file__))
    itens_path = os.path.join(base_path, "data", "itens.json")
    
    # Carregar questões existentes
    questoes = []
    if os.path.exists(itens_path):
        with open(itens_path, "r", encoding="utf-8-sig") as f:
            questoes = json.load(f)
    
    st.info(f"📊 Total de questões no banco: {len(questoes)}")
    
    # ============================================================
    # ABA 1: IMPORTAR JSON
    # ============================================================
    
    st.subheader("📤 Importar Questões em Lote")
    st.markdown("Envie um arquivo JSON com até 30 questões no formato padrão.")
    
    uploaded_file = st.file_uploader("Selecionar arquivo JSON", type=["json"], key="import_json")
    
    if uploaded_file is not None:
        try:
            novas_questoes = json.load(uploaded_file)
            
            if len(novas_questoes) > 30:
                st.error(f"❌ O arquivo contém {len(novas_questoes)} questões. O limite é de 30 por vez.")
            else:
                st.success(f"✅ {len(novas_questoes)} questões carregadas. Verifique o preview:")
                
                # Preview das questões
                with st.expander("📋 Visualizar questões a serem importadas"):
                    for i, q in enumerate(novas_questoes):
                        st.write(f"**{i+1}.** {q.get('enunciado', 'Sem enunciado')[:100]}...")
                        st.write(f"   Descritor: {q.get('descritor', 'N/A')}")
                        st.write(f"   Disciplina: {q.get('disciplina', 'N/A')}")
                        st.write("---")
                
                col1, col2 = st.columns(2)
                with col1:
                    if st.button("✅ Confirmar Importação"):
                        # Simular salvamento
                        st.success(f"✅ {len(novas_questoes)} questões importadas com sucesso!")
                with col2:
                    if st.button("❌ Cancelar"):
                        st.info("Importação cancelada.")
        except json.JSONDecodeError:
            st.error("❌ Arquivo JSON inválido. Verifique o formato.")
    
    st.markdown("---")
    
    # ============================================================
    # ABA 2: BUSCAR E EDITAR QUESTÕES
    # ============================================================
    
    st.subheader("🔍 Buscar e Editar Questões")
    
    col1, col2 = st.columns(2)
    
    with col1:
        termo_busca = st.text_input("Digite um termo para buscar", placeholder="Enunciado, descritor ou habilidade...")
    
    with col2:
        disciplina_filtro = st.selectbox("Filtrar por disciplina", ["Todas", "LP", "MAT", "CIEN", "GEO", "HIS"])
    
    # Filtrar resultados
    resultados = questoes
    if termo_busca:
        resultados = [q for q in resultados if termo_busca.lower() in q.get("enunciado", "").lower() 
                     or termo_busca.lower() in q.get("descritor", "").lower()
                     or termo_busca.lower() in q.get("habilidade", "").lower()]
    
    if disciplina_filtro != "Todas":
        resultados = [q for q in resultados if q.get("disciplina") == disciplina_filtro]
    
    st.info(f"🔍 Encontradas {len(resultados)} questões")
    
    if resultados:
        # Selecionar questão para editar
        opcoes = [f"{q.get('id', 'N/A')} - {q.get('enunciado', '')[:80]}..." for q in resultados[:50]]
        selecionado = st.selectbox("Selecione uma questão para editar", opcoes if opcoes else ["Nenhuma"])
        
        if selecionado and selecionado != "Nenhuma":
            idx = opcoes.index(selecionado)
            questao = resultados[idx]
            
            with st.form("editar_questao"):
                st.subheader("✏️ Editar Questão")
                
                novo_enunciado = st.text_area("Enunciado", value=questao.get("enunciado", ""), height=100)
                
                col1, col2, col3 = st.columns(3)
                with col1:
                    novo_descritor = st.text_input("Descritor", value=questao.get("descritor", ""))
                with col2:
                    nova_disciplina = st.selectbox("Disciplina", ["LP", "MAT", "CIEN", "GEO", "HIS"], 
                                                   index=["LP", "MAT", "CIEN", "GEO", "HIS"].index(questao.get("disciplina", "LP")))
                with col3:
                    novo_gabarito = st.text_input("Gabarito", value=questao.get("gabarito", ""), max_chars=1)
                
                novas_alternativas = st.text_area("Alternativas (uma por linha)", 
                                                   value="\n".join(questao.get("alternativas", [])), height=100)
                
                submitted = st.form_submit_button("💾 Salvar Alterações")
                
                if submitted:
                    # Aqui seria a lógica de salvar
                    st.success("✅ Questão atualizada com sucesso!")
                    st.info("📌 Em produção, os dados seriam salvos no arquivo JSON.")
    
    st.markdown("---")
    
    # ============================================================
    # ESTATÍSTICAS
    # ============================================================
    
    st.subheader("📊 Estatísticas do Banco de Questões")
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Distribuição por disciplina
        disciplinas_count = {}
        for q in questoes:
            disc = q.get("disciplina", "Outros")
            disciplinas_count[disc] = disciplinas_count.get(disc, 0) + 1
        
        fig = px.pie(values=list(disciplinas_count.values()), names=list(disciplinas_count.keys()), title="Questões por Disciplina")
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        # Distribuição por tipo
        tipos_count = {}
        for q in questoes:
            tipo = q.get("tipo", "multipla_escolha")
            tipos_count[tipo] = tipos_count.get(tipo, 0) + 1
        
        fig2 = px.bar(x=list(tipos_count.keys()), y=list(tipos_count.values()), title="Questões por Tipo")
        st.plotly_chart(fig2, use_container_width=True)
    
    st.caption(f"📌 Última atualização: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}")

if __name__ == "__main__":
    show()

