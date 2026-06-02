import streamlit as st
import json
import os
import io
import zipfile
import random
from datetime import datetime
from core.auth import get_current_user
from services.gerador_prova_pdf import GeradorProva

# ============================================================
# FUNÇÕES DE CARREGAMENTO DE DADOS
# ============================================================

def carregar_descritores_por_tipo_item(tipo_item, ano_escolar):
    """Carrega descritores do arquivo correspondente com base no ano"""
    
    base_path = os.getcwd()
    
    arquivos = {
        "BNCC": "bncc.json",
        "CNCA": "cnca.json",
        "SAEB": "saeb.json"
    }
    
    nome_arquivo = arquivos.get(tipo_item)
    if not nome_arquivo:
        return []
    
    caminho = os.path.join(base_path, "data", nome_arquivo)
    
    if not os.path.exists(caminho):
        return []
    
    try:
        with open(caminho, "r", encoding="utf-8") as f:
            dados = json.load(f)
        
        habilidades = []
        ano_num = ano_escolar[0]  # "1", "2", etc.
        
        # BNCC
        if tipo_item == "BNCC":
            for disciplina, conteudo in dados.items():
                if isinstance(conteudo, dict):
                    for ano, lista_habilidades in conteudo.items():
                        if ano == f"{ano_num}º" or ano == ano_escolar:
                            if isinstance(lista_habilidades, list):
                                for item in lista_habilidades:
                                    if isinstance(item, dict):
                                        codigo = item.get("codigo", "")
                                        habilidade = item.get("habilidade", item.get("descricao", ""))
                                        if codigo and habilidade:
                                            habilidades.append(f"{codigo} - {habilidade}")
        
        # CNCA
        elif tipo_item == "CNCA":
            ano_map = {"1º": "1EF", "2º": "2EF", "3º": "3EF", "4º": "4EF", "5º": "5EF"}
            ano_key = ano_map.get(ano_escolar, f"{ano_num}EF")
            
            for ano, conteudo in dados.items():
                if ano == ano_key:
                    if isinstance(conteudo, dict):
                        for disciplina, lista in conteudo.items():
                            if isinstance(lista, list):
                                for item in lista:
                                    if isinstance(item, dict):
                                        codigo = item.get("codigo", "")
                                        habilidade = item.get("habilidade", "")
                                        if codigo and habilidade:
                                            habilidades.append(f"{codigo} - {habilidade}")
        
        # SAEB
        elif tipo_item == "SAEB":
            ano_map = {"2º": "2EF", "5º": "5EF"}
            ano_key = ano_map.get(ano_escolar, f"{ano_num}EF")
            
            for ano, conteudo in dados.items():
                if ano == ano_key:
                    if isinstance(conteudo, dict):
                        for disciplina, lista in conteudo.items():
                            if isinstance(lista, list):
                                for item in lista:
                                    if isinstance(item, dict):
                                        codigo = item.get("codigo", "")
                                        habilidade = item.get("habilidade", "")
                                        if codigo and habilidade:
                                            habilidades.append(f"{codigo} - {habilidade}")
        
        return habilidades[:50]  # Limitar a 50 descritores
    
    except Exception as e:
        return []


def buscar_questoes_localmente(descritores_selecionados, num_questoes):
    """Busca questões no arquivo itens.json localmente"""
    base_path = os.getcwd()
    caminho = os.path.join(base_path, "data", "itens.json")
    
    if not os.path.exists(caminho):
        return None
    
    try:
        with open(caminho, "r", encoding="utf-8") as f:
            dados = json.load(f)
        
        questoes_encontradas = []
        
        # Extrair códigos dos descritores selecionados
        codigos_descritores = [d.split(" - ")[0] for d in descritores_selecionados]
        
        # Buscar questões que correspondem aos descritores
        for item in dados:
            if isinstance(item, dict):
                descritor_item = item.get("descritor", item.get("codigo_descritor", ""))
                if descritor_item in codigos_descritores:
                    questoes_encontradas.append({
                        "enunciado": item.get("enunciado", item.get("texto", "Questão disponível em breve")),
                        "alternativas": item.get("alternativas", [
                            {"letra": "A", "texto": "Alternativa A"},
                            {"letra": "B", "texto": "Alternativa B"},
                            {"letra": "C", "texto": "Alternativa C"},
                            {"letra": "D", "texto": "Alternativa D"}
                        ]),
                        "gabarito": item.get("gabarito", "A"),
                        "comentario": item.get("comentario", "Comentário disponível em breve.")
                    })
        
        return questoes_encontradas if questoes_encontradas else None
    
    except Exception as e:
        return None


def buscar_questoes_supabase(descritores_selecionados, num_questoes):
    """Busca questões no Supabase (futuro)"""
    # TODO: Implementar conexão com Supabase
    return None


def gerar_questoes_automaticas(descritores_selecionados, num_questoes, disciplina):
    """Gera questões automaticamente quando não encontra no banco"""
    questoes = []
    for i in range(num_questoes):
        descritor_escolhido = descritores_selecionados[i % len(descritores_selecionados)]
        codigo_descritor = descritor_escolhido.split(" - ")[0] if " - " in descritor_escolhido else descritor_escolhido[:20]
        texto_descritor = descritor_escolhido.split(" - ")[1] if " - " in descritor_escolhido else descritor_escolhido
        
        alternativas = [
            {"letra": "A", "texto": f"Alternativa A - Correta para {codigo_descritor}"},
            {"letra": "B", "texto": "Alternativa B - Parcialmente correta"},
            {"letra": "C", "texto": "Alternativa C - Contém erro comum"},
            {"letra": "D", "texto": "Alternativa D - Totalmente incorreta"}
        ]
        
        questoes.append({
            "enunciado": f"Questão {i+1}: {texto_descritor[:150]}",
            "alternativas": alternativas,
            "gabarito": "A",
            "comentario": f"A resposta correta é a alternativa A, pois está alinhada ao descritor {codigo_descritor}."
        })
    
    return questoes


def get_turmas_por_ano(ano_escolar):
    """Retorna turmas baseadas no ano escolar selecionado"""
    ano_num = ano_escolar[0]
    return [f"{ano_escolar} A", f"{ano_escolar} B", f"{ano_escolar} C"]


def get_descritores_disponiveis_por_ano(ano_escolar):
    """Retorna lista de tipos de descritores disponíveis por ano"""
    mapa = {
        "1º Ano": ["BNCC", "CNCA"],
        "2º Ano": ["BNCC", "CNCA", "SAEB"],
        "3º Ano": ["BNCC", "CNCA"],
        "4º Ano": ["BNCC", "CNCA"],
        "5º Ano": ["BNCC", "CNCA", "SAEB"],
        "6º Ano": ["BNCC", "SAEB"],
        "7º Ano": ["BNCC", "SAEB"],
        "8º Ano": ["BNCC", "SAEB"],
        "9º Ano": ["BNCC", "SAEB"]
    }
    return mapa.get(ano_escolar, ["BNCC"])


def get_disciplinas_por_ano(ano_escolar):
    """Retorna disciplinas baseadas no ano escolar"""
    ano_num = int(ano_escolar[0])
    if ano_num <= 4:
        return ["Matemática", "Língua Portuguesa"]
    else:
        return ["Ciências", "Geografia", "História", "Matemática", "Língua Portuguesa"]


# ============================================================
# PÁGINA PRINCIPAL
# ============================================================

def show():
    usuario = get_current_user()
    
    st.title("📚 Geração de Provas")
    st.markdown("Configure os parâmetros abaixo para gerar uma prova personalizada.")
    st.markdown("---")
    
    # ========== DADOS DO PERFIL (PLACEHOLDER) ==========
    if usuario and usuario.get("nome"):
        professor = usuario.get("nome", "Professor")
        escola = usuario.get("escola", "ESCOLA FANTASIA")
        st.info(f"👋 Olá, {professor}! Configurando prova para {escola}")
    else:
        professor = "Professor Exemplo"
        escola = "ESCOLA FANTASIA"
        st.warning("⚠️ Modo de demonstração - Configure seu perfil para personalizar")
    
    # ========== 1) INFORMAÇÕES DA PROVA ==========
    st.subheader("1️⃣ Informações da Prova")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        anos_disponiveis = ["1º Ano", "2º Ano", "3º Ano", "4º Ano", "5º Ano", 
                           "6º Ano", "7º Ano", "8º Ano", "9º Ano"]
        ano_escolar = st.selectbox("📚 Ano Escolar", options=anos_disponiveis, index=4)
    
    with col2:
        turmas_disponiveis = get_turmas_por_ano(ano_escolar)
        turma_selecionada = st.selectbox("🏫 Turma", options=turmas_disponiveis, index=0)
    
    with col3:
        tipo_prova = st.selectbox("📋 Tipo de Prova", ["Múltipla Escolha", "Leitura", "Escrita"], index=0)
    
    col4, col5, col6 = st.columns(3)
    
    with col4:
        disciplinas_disponiveis = get_disciplinas_por_ano(ano_escolar)
        disciplina = st.selectbox("📚 Disciplina", options=disciplinas_disponiveis, index=0)
    
    with col5:
        tipos_descritores = get_descritores_disponiveis_por_ano(ano_escolar)
        tipo_descriptor = st.selectbox("🎯 Tipo Descritor", options=tipos_descritores, index=0)
    
    with col6:
        num_questoes = st.selectbox("🔢 Número de Questões", [5, 10, 15, 20], index=1)
    
    st.markdown("---")
    
    # ========== 2) DESCRITORES ==========
    st.subheader("2️⃣ Descritores / Habilidades")
    
    st.info(f"📖 Carregando descritores da matriz **{tipo_descriptor}** para **{ano_escolar}**")
    
    # Carregar descritores com código e habilidade
    descritores_opcoes = carregar_descritores_por_tipo_item(tipo_descriptor, ano_escolar)
    
    if descritores_opcoes:
        descritores_selecionados = st.multiselect(
            "Selecione os Descritores",
            options=descritores_opcoes,
            default=descritores_opcoes[:2] if len(descritores_opcoes) > 1 else descritores_opcoes,
            help="Mínimo: 1 descritor | Máximo: 5 descritores"
        )
        
        if len(descritores_selecionados) < 1:
            st.warning("⚠️ Selecione pelo menos 1 descritor para gerar a prova")
        elif len(descritores_selecionados) > 5:
            st.error("❌ Máximo de 5 descritores permitidos")
        else:
            st.success(f"✅ {len(descritores_selecionados)} descritor(es) selecionado(s)")
            
            with st.expander("📋 Ver descritores selecionados"):
                for d in descritores_selecionados:
                    st.markdown(f"**{d}**")
    else:
        st.warning(f"⚠️ Nenhum descritor encontrado para {tipo_descriptor} - {ano_escolar}")
        descritores_selecionados = []
    
    st.markdown("---")
    
    # ========== 3) GERAR PROVA ==========
    st.subheader("3️⃣ Gerar Prova")
    
    with st.expander("📋 Resumo da configuração", expanded=False):
        st.markdown(f"""
        - **Escola:** {escola}
        - **Professor:** {professor}
        - **Ano Escolar:** {ano_escolar}
        - **Turma:** {turma_selecionada}
        - **Tipo de Prova:** {tipo_prova}
        - **Disciplina:** {disciplina}
        - **Tipo Descritor:** {tipo_descriptor}
        - **Número de Questões:** {num_questoes}
        - **Descritores Selecionados:** {len(descritores_selecionados)}
        """)
    
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        gerar_btn = st.button("🎯 GERAR PROVA", use_container_width=True, type="primary")
    
    if "zip_buffer" not in st.session_state:
        st.session_state.zip_buffer = None
        st.session_state.nome_base = None
    
    if gerar_btn:
        if not descritores_selecionados:
            st.error("❌ Selecione pelo menos um descritor!")
        else:
            with st.spinner("🔄 Buscando questões e gerando prova..."):
                # Tentar buscar questões localmente
                questoes = buscar_questoes_localmente(descritores_selecionados, num_questoes)
                
                if not questoes:
                    st.info("📡 Buscando questões no Supabase...")
                    questoes = buscar_questoes_supabase(descritores_selecionados, num_questoes)
                
                if not questoes:
                    st.info("🔧 Gerando questões automaticamente...")
                    questoes = gerar_questoes_automaticas(descritores_selecionados, num_questoes, disciplina)
                
                # Garantir que temos o número correto de questões
                while len(questoes) < num_questoes:
                    questoes.extend(questoes[:num_questoes - len(questoes)])
                questoes = questoes[:num_questoes]
                
                # Atualizar números das questões
                for idx, q in enumerate(questoes):
                    q["numero"] = idx + 1
                
                # Gerar ZIP com prova e gabarito
                gerador = GeradorProva()
                zip_buffer, nome_base = gerador.gerar_zip_prova(
                    escola=escola,
                    turma=turma_selecionada,
                    ano=ano_escolar,
                    disciplinas=[disciplina],
                    professor=professor,
                    questoes=questoes,
                    qtd_questoes=num_questoes,
                    data_prova=datetime.now()
                )
                
                st.session_state.zip_buffer = zip_buffer
                st.session_state.nome_base = nome_base
                
                origem = "local" if buscar_questoes_localmente(descritores_selecionados, num_questoes) else ("supabase" if buscar_questoes_supabase(descritores_selecionados, num_questoes) else "automática")
                st.success(f"✅ Prova gerada com {num_questoes} questões! (Fonte: {origem})")
                st.balloons()
    
    # ========== DOWNLOAD ==========
    if st.session_state.zip_buffer:
        st.subheader("📥 Download")
        
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            st.download_button(
                label="📥 BAIXAR PROVA + GABARITO (ZIP)",
                data=st.session_state.zip_buffer,
                file_name=f"{st.session_state.nome_base}.zip",
                mime="application/zip",
                use_container_width=True,
                type="primary"
            )
        
        st.info("📌 O arquivo ZIP contém:\n- **PROVA.pdf** (para aplicar aos alunos)\n- **GABARITO_COMENTADO.pdf** (para correção do professor)")
    
    st.markdown("---")
    st.caption("📌 O sistema busca questões primeiro localmente (itens.json), depois no Supabase, e por fim gera automaticamente.")


if __name__ == "__main__":
    show()
