import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import json
import os
from datetime import datetime
from core.auth import get_current_user
from services.supabase_service import supabase_service

def show():
    usuario = get_current_user()
    
    if not usuario or usuario.get("perfil") != "admin":
        st.error("⛔ Acesso restrito a administradores")
        return
    
    st.title("📋 Auditoria do Sistema")
    st.caption("Logs de atividades e monitoramento")
    
    # ============================================================
    # CARREGAR DADOS
    # ============================================================
    
    # Inicializar variáveis com valores padrão
    usuarios = []
    itens = []
    correcoes = []
    logs = []
    
    try:
        # Carregar usuários do Supabase
        if supabase_service.client:
            result = supabase_service.client.table("usuarios").select("*").execute()
            usuarios = result.data if result.data else []
        else:
            # Fallback para arquivo local
            if os.path.exists("data/usuarios.json"):
                with open("data/usuarios.json", "r", encoding="utf-8") as f:
                    usuarios = json.load(f)
    except Exception as e:
        st.warning(f"Erro ao carregar usuários: {e}")
        usuarios = []
    
    try:
        # Carregar itens/questões do Supabase
        if supabase_service.client:
            result = supabase_service.client.table("provas").select("*").execute()
            itens = result.data if result.data else []
        else:
            # Fallback para arquivo local
            if os.path.exists("data/itens.json"):
                with open("data/itens.json", "r", encoding="utf-8") as f:
                    itens_data = json.load(f)
                    itens = itens_data if isinstance(itens_data, list) else []
    except Exception as e:
        st.warning(f"Erro ao carregar itens: {e}")
        itens = []
    
    try:
        # Carregar correções do Supabase
        if supabase_service.client:
            result = supabase_service.client.table("correcoes").select("*").execute()
            correcoes = result.data if result.data else []
    except Exception as e:
        st.warning(f"Erro ao carregar correções: {e}")
        correcoes = []
    
    # ============================================================
    # ESTATÍSTICAS GERAIS
    # ============================================================
    st.subheader("📊 Estatísticas Gerais")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("👥 Usuários", len(usuarios), border=True)
    with col2:
        st.metric("📝 Questões/Provas", len(itens), border=True)
    with col3:
        st.metric("✅ Correções", len(correcoes), border=True)
    with col4:
        st.metric("📈 Taxa de Acerto", f"{45}%", border=True)
    
    st.markdown("---")
    
    # ============================================================
    # LISTA DE USUÁRIOS
    # ============================================================
    st.subheader("👥 Usuários do Sistema")
    
    if usuarios:
        df_usuarios = pd.DataFrame(usuarios)
        
        # Garantir que as colunas existem
        colunas_disponiveis = df_usuarios.columns.tolist()
        
        colunas_exibir = []
        for col in ["nome", "email", "perfil", "created_at"]:
            if col in colunas_disponiveis:
                colunas_exibir.append(col)
        
        if colunas_exibir:
            st.dataframe(df_usuarios[colunas_exibir], use_container_width=True)
        else:
            st.dataframe(df_usuarios, use_container_width=True)
    else:
        st.info("Nenhum usuário encontrado")
    
    st.markdown("---")
    
    # ============================================================
    # LISTA DE ITENS (PROVAS)
    # ============================================================
    st.subheader("📝 Provas Geradas")
    
    if itens:
        # Verificar se a variável itens existe e não está vazia
        if isinstance(itens, list) and len(itens) > 0:
            df_itens = pd.DataFrame(itens)
            
            colunas_disponiveis = df_itens.columns.tolist()
            colunas_exibir = []
            
            for col in ["exam_id", "nome", "disciplina", "ano", "qtd_questoes", "created_at"]:
                if col in colunas_disponiveis:
                    colunas_exibir.append(col)
            
            if colunas_exibir:
                st.dataframe(df_itens[colunas_exibir], use_container_width=True)
            else:
                st.dataframe(df_itens, use_container_width=True)
        else:
            st.info("Nenhuma prova encontrada")
    else:
        st.info("Nenhuma prova encontrada")
    
    st.markdown("---")
    
    # ============================================================
    # GRÁFICOS
    # ============================================================
    st.subheader("📈 Análise de Dados")
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Gráfico de usuários por perfil
        if usuarios:
            perfis = {}
            for u in usuarios:
                perfil = u.get("perfil", "indefinido")
                perfis[perfil] = perfis.get(perfil, 0) + 1
            
            if perfis:
                fig = px.pie(
                    values=list(perfis.values()),
                    names=list(perfis.keys()),
                    title="Usuários por Perfil"
                )
                st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        # Gráfico de provas por disciplina
        if itens and isinstance(itens, list) and len(itens) > 0:
            disciplinas = {}
            for item in itens:
                if isinstance(item, dict):
                    disc = item.get("disciplina", "indefinido")
                    disciplinas[disc] = disciplinas.get(disc, 0) + 1
            
            if disciplinas:
                fig = px.bar(
                    x=list(disciplinas.keys()),
                    y=list(disciplinas.values()),
                    title="Provas por Disciplina",
                    labels={"x": "Disciplina", "y": "Quantidade"}
                )
                st.plotly_chart(fig, use_container_width=True)
    
    st.markdown("---")
    
    # ============================================================
    # LOGS DO SISTEMA
    # ============================================================
    st.subheader("📜 Logs do Sistema")
    
    # Tentar carregar logs
    logs_encontrados = []
    
    try:
        if os.path.exists("logs"):
            for arquivo in os.listdir("logs"):
                if arquivo.endswith(".log"):
                    caminho = os.path.join("logs", arquivo)
                    with open(caminho, "r", encoding="utf-8") as f:
                        linhas = f.readlines()[-20:]  # Últimas 20 linhas
                        for linha in linhas:
                            logs_encontrados.append({"arquivo": arquivo, "linha": linha.strip()})
    except Exception as e:
        st.warning(f"Erro ao ler logs: {e}")
    
    if logs_encontrados:
        df_logs = pd.DataFrame(logs_encontrados)
        st.dataframe(df_logs, use_container_width=True)
    else:
        st.info("Nenhum log encontrado")
    
    st.caption(f"Última atualização: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}")

if __name__ == "__main__":
    show()
