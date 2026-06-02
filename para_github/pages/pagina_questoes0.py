import streamlit as st
import json
import os
import io
import zipfile
import random
from datetime import datetime
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import cm
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from core.auth import get_current_user

# ============================================================
# FUNÇÃO - EXTRAÇÃO AVANÇADA DE HABILIDADES (COM DEBUG)
# ============================================================

def carregar_descritores_por_tipo_item(tipo_item):
    """Carrega descritores do arquivo correspondente com debug"""
    
    # Caminho base corrigido
    base_path = os.getcwd()
    
    arquivos = {
        "BNCC": "bncc.json",
        "CNCA": "cnca.json",
        "SAEB": "saeb.json"
    }
    
    nome_arquivo = arquivos.get(tipo_item)
    
    if not nome_arquivo:
        return [f"{tipo_item} - Habilidade 1", f"{tipo_item} - Habilidade 2"]
    
    # Caminho completo
    caminho = os.path.join(base_path, "data", nome_arquivo)
    
    # DEBUG (ajuda a identificar problemas)
    with st.expander("🔍 DEBUG DESCRITORES", expanded=False):
        st.write("📂 Base Path:", base_path)
        st.write("📄 Arquivo:", nome_arquivo)
        st.write("🛣️ Caminho Completo:", caminho)
        st.write("✅ Arquivo Existe?", os.path.exists(caminho))
    
    if not os.path.exists(caminho):
        st.error(f"❌ Arquivo não encontrado: {caminho}")
        return [f"{tipo_item} - Habilidade 1", f"{tipo_item} - Habilidade 2"]
    
    try:
        with open(caminho, "r", encoding="utf-8") as f:
            dados = json.load(f)
        
        habilidades = []
        
        # Extração recursiva
        def extrair_habilidades(obj):
            if isinstance(obj, dict):
                for chave, valor in obj.items():
                    if chave in ["_metadata", "versao", "data_criacao", "info"]:
                        continue
                    
                    if isinstance(valor, str) and len(valor) > 20:
                        palavras_chave = [
                            "reconhecer", "identificar", "comparar", "analisar",
                            "interpretar", "distinguir", "relacionar", "ler",
                            "escrever", "compreender", "aplicar", "resolver",
                            "calcular", "classificar", "ordenar", "nomear"
                        ]
                        if any(p in valor.lower() for p in palavras_chave):
                            codigo = ""
                            if "codigo" in obj:
                                codigo = obj.get("codigo", "")
                            elif chave.isupper():
                                codigo = chave
                            if codigo:
                                habilidades.append(f"{codigo} - {valor}")
                            else:
                                habilidades.append(valor)
                    extrair_habilidades(valor)
            elif isinstance(obj, list):
                for item in obj:
                    extrair_habilidades(item)
        
        # BNCC
        if tipo_item == "BNCC":
            for disciplina, conteudo in dados.items():
                if isinstance(conteudo, dict):
                    for ano, habilidades_por_ano in conteudo.items():
                        if isinstance(habilidades_por_ano, dict):
                            for codigo, descricao in habilidades_por_ano.items():
                                if isinstance(descricao, str) and len(descricao) > 15:
                                    habilidades.append(f"{codigo} - {descricao}")
        
        # CNCA
        elif tipo_item == "CNCA":
            for ano, conteudo in dados.items():
                if isinstance(conteudo, list):
                    for item in conteudo:
                        if isinstance(item, dict):
                            codigo = item.get("codigo") or item.get("id") or ""
                            descricao = item.get("descricao") or item.get("habilidade") or item.get("texto") or ""
                            if descricao and len(descricao) > 10:
                                if codigo:
                                    habilidades.append(f"{codigo} - {descricao}")
                                else:
                                    habilidades.append(descricao)
                        elif isinstance(item, str) and len(item) > 15:
                            habilidades.append(item)
        
        # SAEB
        elif tipo_item == "SAEB":
            for ano, conteudo in dados.items():
                if isinstance(conteudo, dict):
                    for codigo, descricao in conteudo.items():
                        if isinstance(descricao, str) and len(descricao) > 15:
                            habilidades.append(f"{codigo} - {descricao}")
        
        # Fallback recursivo
        if not habilidades:
            extrair_habilidades(dados)
        
        # Limpeza
        habilidades = [h for h in habilidades if h and len(h) > 10]
        habilidades = list(dict.fromkeys(habilidades))
        
        if habilidades:
            # st.success(f"✅ {len(habilidades)} habilidades carregadas")  # LOG REMOVIDO
            with st.expander(f"📖 Exemplos de {tipo_item}", expanded=False):
                for h in habilidades[:5]:
                    st.write(f"- {h[:120]}")
            return habilidades[:50]
        else:
            st.warning(f"⚠️ Nenhuma habilidade encontrada em {nome_arquivo}")
    
    except Exception as e:
        st.error(f"❌ Erro ao ler {nome_arquivo}: {e}")
    
    return [f"{tipo_item} - Exemplo de habilidade 1", f"{tipo_item} - Exemplo de habilidade 2"]

# ============================================================
# FUNÇÕES AUXILIARES
# ============================================================

def get_disciplinas_por_ano(ano):
    if ano in [1, 2, 3, 4]:
        return ["Matemática", "Língua Portuguesa"]
    elif ano in [5, 6, 7, 8, 9]:
        return ["Matemática", "Língua Portuguesa", "Ciências", "Geografia", "História"]
    return ["Matemática", "Língua Portuguesa"]

def get_tipos_descriptor_por_ano(ano):
    if ano == 1:
        return ["BNCC", "CNCA"]
    elif ano == 2:
        return ["BNCC", "CNCA", "SAEB"]
    elif ano == 3:
        return ["BNCC", "CNCA"]
    elif ano == 4:
        return ["BNCC", "CNCA"]
    elif ano == 5:
        return ["BNCC", "CNCA", "SAEB"]
    elif ano in [6, 7, 8, 9]:
        return ["BNCC", "SAEB"]
    return ["BNCC"]

# ============================================================
# FUNÇÕES DE PDF
# ============================================================

def gerar_pdf_prova(questoes, titulo, turma, disciplina, ano):
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4)
    styles = getSampleStyleSheet()
    elements = []
    
    titulo_style = ParagraphStyle('TitleStyle', parent=styles['Heading1'], fontSize=16, textColor=colors.HexColor('#1e3c72'), alignment=1, spaceAfter=20)
    
    elements.append(Paragraph(f"<b>{titulo}</b>", titulo_style))
    elements.append(Paragraph(f"Turma: {turma}", styles['Normal']))
    elements.append(Paragraph(f"Disciplina: {disciplina} - {ano}º Ano", styles['Normal']))
    elements.append(Paragraph(f"Data: {datetime.now().strftime('%d/%m/%Y')}", styles['Normal']))
    elements.append(Spacer(1, 0.5*cm))
    
    for i, q in enumerate(questoes, 1):
        elements.append(Paragraph(f"<b>Questão {i}</b>", styles['Heading2']))
        elements.append(Paragraph(q.get("enunciado", "Texto da questão"), styles['Normal']))
        alt = q.get("alternativas", ["A) ", "B) ", "C) ", "D) "])
        for j, a in enumerate(alt):
            elements.append(Paragraph(f"{chr(65+j)}) {a}", styles['Normal']))
        elements.append(Spacer(1, 0.3*cm))
    
    doc.build(elements)
    buffer.seek(0)
    return buffer

def gerar_pdf_gabarito(questoes, titulo, turma, disciplina, ano):
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4)
    styles = getSampleStyleSheet()
    elements = []
    
    titulo_style = ParagraphStyle('TitleStyle', parent=styles['Heading1'], fontSize=16, textColor=colors.HexColor('#28a745'), alignment=1, spaceAfter=20)
    
    elements.append(Paragraph(f"<b>GABARITO COMENTADO - {titulo}</b>", titulo_style))
    elements.append(Paragraph(f"Turma: {turma}", styles['Normal']))
    elements.append(Paragraph(f"Disciplina: {disciplina} - {ano}º Ano", styles['Normal']))
    elements.append(Paragraph(f"Data: {datetime.now().strftime('%d/%m/%Y')}", styles['Normal']))
    elements.append(Spacer(1, 0.5*cm))
    
    dados_tabela = [["Questão", "Gabarito"]]
    for i, q in enumerate(questoes, 1):
        dados_tabela.append([str(i), q.get("gabarito", "A")])
    
    tabela = Table(dados_tabela, colWidths=[5*cm, 5*cm])
    tabela.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#1e3c72')),
        ('TEXTCOLOR', (0,0), (-1,0), colors.white),
        ('ALIGN', (0,0), (-1,-1), 'CENTER'),
        ('GRID', (0,0), (-1,-1), 1, colors.grey)
    ]))
    elements.append(tabela)
    elements.append(Spacer(1, 0.5*cm))
    
    for i, q in enumerate(questoes, 1):
        elements.append(Paragraph(f"<b>Questão {i} - Comentário</b>", styles['Heading3']))
        elements.append(Paragraph(f"Esta questão aborda o descritor {q.get('descritor', 'especificado')}.", styles['Normal']))
        elements.append(Spacer(1, 0.3*cm))
    
    doc.build(elements)
    buffer.seek(0)
    return buffer

def criar_zip(prova_pdf, gabarito_pdf, disciplina, ano):
    zip_buffer = io.BytesIO()
    with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zip_file:
        zip_file.writestr(f"prova_{disciplina}_{ano}o_ano.pdf", prova_pdf.getvalue())
        zip_file.writestr(f"gabarito_comentado_{disciplina}_{ano}o_ano.pdf", gabarito_pdf.getvalue())
    zip_buffer.seek(0)
    return zip_buffer

# ============================================================
# PÁGINA PRINCIPAL
# ============================================================

def show():
    usuario = get_current_user()
    
    st.title("📚 Geração de Provas")
    st.markdown("Configure os parâmetros abaixo para gerar uma prova personalizada.")
    st.markdown("---")
    
    # LINHA 1
    col1, col2, col3 = st.columns(3)
    with col1:
        ano_escolar = st.selectbox("ANO ESCOLAR", [1,2,3,4,5,6,7,8,9], format_func=lambda x: f"{x}º Ano", index=4)
    with col2:
        turmas_disponiveis = ["5º Ano A", "5º Ano B", "5º Ano C"]
        turma_selecionada = st.selectbox("TURMA", turmas_disponiveis, index=0)
    with col3:
        tipo_prova = st.selectbox("PROVA", ["Múltipla Escolha", "Escrita", "Leitura"], index=0)
    
    st.markdown("---")
    
    # LINHA 2
    col1, col2, col3 = st.columns(3)
    with col1:
        disciplinas_disponiveis = get_disciplinas_por_ano(ano_escolar)
        disciplina = st.selectbox("DISCIPLINA", disciplinas_disponiveis, index=0)
    with col2:
        tipos_disponiveis = get_tipos_descriptor_por_ano(ano_escolar)
        tipo_descriptor = st.selectbox("TIPO DESCRITOR", tipos_disponiveis, index=0)
    with col3:
        num_questoes = st.selectbox("NÚMERO QUESTÕES", [5, 10, 15, 20], index=0)
    
    st.markdown("---")
    
    # LINHA 3 - BUSCA
    temas_disponiveis = [
        "sustentabilidade", "meio ambiente", "antirracismo", "trânsito",
        "educação fiscal", "educação financeira", "direito das crianças", "Maria da Penha"
    ]
    tema_busca = st.selectbox("BUSCA", [""] + temas_disponiveis, index=0)
    if tema_busca:
        st.info(f"🔍 Buscando questões relacionadas a: **{tema_busca}**")
    
    st.markdown("---")
    
    # LINHA 4 - DESCRITORES (com a função melhorada)
    descritores_opcoes = carregar_descritores_por_tipo_item(tipo_descriptor)
    st.info(f"📖 Carregando descritores da matriz **{tipo_descriptor}**")
    
    descritores_selecionados = st.multiselect(
        "DESCRITORES (selecione quantos desejar)",
        options=descritores_opcoes,
        default=descritores_opcoes[:2] if len(descritores_opcoes) > 1 else descritores_opcoes
    )
    
    if descritores_selecionados:
        st.success(f"✅ {len(descritores_selecionados)} descritor(es) selecionado(s)")
    else:
        st.warning("⚠️ Selecione pelo menos um descritor para gerar a prova")
    
    st.markdown("---")
    
    # LINHA 5 - GERAR PROVA
    st.subheader("🎯 Gerar Prova")
    
    with st.expander("📋 Resumo da configuração", expanded=False):
        st.markdown(f"""
        - **Ano Escolar:** {ano_escolar}º Ano
        - **Turma:** {turma_selecionada}
        - **Tipo de Prova:** {tipo_prova}
        - **Disciplina:** {disciplina}
        - **Tipo Descritor:** {tipo_descriptor}
        - **Número de Questões:** {num_questoes}
        - **Tema:** {tema_busca if tema_busca else "Nenhum"}
        - **Descritores Selecionados:** {len(descritores_selecionados)}
        """)
    
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        gerar_btn = st.button("🎯 GERAR PROVA", use_container_width=True, type="primary")
    
    if "prova_gerada" not in st.session_state:
        st.session_state.prova_gerada = False
        st.session_state.zip_buffer = None
    
    if gerar_btn:
        if descritores_selecionados:
            with st.spinner("🔄 Gerando prova e gabarito..."):
                questoes = []
                for i in range(num_questoes):
                    questoes.append({
                        "enunciado": f"Questão {i+1}: Exemplo sobre {descritores_selecionados[0][:50]}...",
                        "alternativas": ["Alternativa A", "Alternativa B", "Alternativa C", "Alternativa D"],
                        "gabarito": ["A", "B", "C", "D"][i % 4],
                        "descritor": descritores_selecionados[0].split(" - ")[0] if " - " in descritores_selecionados[0] else "DESC001"
                    })
                
                prova_pdf = gerar_pdf_prova(questoes, f"Prova de {disciplina}", turma_selecionada, disciplina, ano_escolar)
                gabarito_pdf = gerar_pdf_gabarito(questoes, f"Prova de {disciplina}", turma_selecionada, disciplina, ano_escolar)
                
                st.session_state.zip_buffer = criar_zip(prova_pdf, gabarito_pdf, disciplina, ano_escolar)
                st.session_state.prova_gerada = True
                st.success(f"✅ Prova gerada com {num_questoes} questões!")
        else:
            st.error("❌ Selecione pelo menos um descritor!")
    
    # LINHA 6 - DOWNLOAD ZIP
    if st.session_state.prova_gerada and st.session_state.zip_buffer:
        st.subheader("📥 Download")
        st.download_button(
            label="📥 BAIXAR PROVA + GABARITO (ZIP)",
            data=st.session_state.zip_buffer,
            file_name=f"prova_{disciplina}_{ano_escolar}o_ano_{tipo_descriptor}.zip",
            mime="application/zip",
            use_container_width=True
        )
    
    st.markdown("---")
    st.caption("📌 O sistema seleciona automaticamente as questões baseadas nos descritores selecionados.")

if __name__ == "__main__":
    show()


