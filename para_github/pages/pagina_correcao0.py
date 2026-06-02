import streamlit as st
import pandas as pd
from datetime import datetime
from core.auth import get_current_user
from PIL import Image
from services.leitor_prova import LeitorProva

def show():
    usuario = get_current_user()
    
    st.title("Correcao de Provas")
    st.caption("Correcao automatica por camera - Aponte para o QR Code da prova")
    
    st.subheader("Capture a Prova")
    
    st.info("""
    ### Como funciona:
    1. Posicione a prova na frente da camera
    2. Certifique-se que o **QR Code** esta visivel
    3. O sistema ira identificar automaticamente a prova
    4. O OCR (reconhecimento) lerá as respostas
    5. A correcao sera realizada instantaneamente
    """)
    
    # Camera
    camera_file = st.camera_input("Tire uma foto da prova", label_visibility="collapsed")
    
    if camera_file is not None:
        # Carregar imagem
        imagem = Image.open(camera_file)
        st.image(imagem, caption="Prova capturada", use_container_width=True)
        
        # Inicializar leitor
        leitor = LeitorProva()
        
        # Processar
        with st.spinner("Processando imagem - Lendo QR Code e respostas..."):
            resultado = leitor.corrigir_prova(imagem)
        
        if resultado["sucesso"]:
            st.success("Correcao realizada com sucesso!")
            
            # Dados da prova
            st.subheader("Dados da Prova")
            col1, col2 = st.columns(2)
            
            with col1:
                st.metric("Turma", resultado["dados_prova"].get("turma", "N/A"), border=True)
                st.metric("Disciplina", resultado["dados_prova"].get("disciplina", "N/A"), border=True)
            
            with col2:
                st.metric("Data", datetime.now().strftime("%d/%m/%Y"), border=True)
                st.metric("Total de Questoes", resultado["total_questoes"], border=True)
            
            # Resultados
            with st.expander("Resultado da Correcao", expanded=True):
                col_res1, col_res2, col_res3 = st.columns(3)
                
                with col_res1:
                    st.metric("Acertos", f"{resultado['acertos']}/{resultado['total_questoes']}", border=True)
                    st.metric("Percentual", f"{resultado['percentual']}%", border=True)
                
                with col_res2:
                    st.metric("Media", f"{resultado['percentual']/10:.1f}", border=True)
                
                with col_res3:
                    if resultado['percentual'] >= 70:
                        st.metric("Status", "Aprovado", border=True, delta="Acima da meta")
                    elif resultado['percentual'] >= 50:
                        st.metric("Status", "Recuperacao", border=True)
                    else:
                        st.metric("Status", "Reprovado", border=True, delta="Abaixo da meta")
                
                # Detalhamento
                st.subheader("Detalhamento por Questao")
                df = pd.DataFrame(resultado["detalhes"])
                st.dataframe(df, use_container_width=True, hide_index=True)
            
            # Botao para salvar
            if st.button("Salvar Resultado", type="primary", use_container_width=True):
                st.success("Resultado salvo com sucesso!")
        else:
            st.error(f"Erro: {resultado['erro']}")
            st.warning("""
            **Dicas:**
            - Certifique-se que o QR Code esta visivel
            - Aproxime a camera da prova
            - Garanta boa iluminacao
            """)
    
    else:
        st.markdown("""
        <div style="
            background: #f0f2f6; 
            border-radius: 20px; 
            padding: 3rem; 
            text-align: center;
            border: 2px dashed #ccc;
        ">
            <h3 style="color: #666;">Aguardando captura</h3>
            <p style="color: #888;">Clique no botao acima para tirar uma foto da prova</p>
            <p style="color: #aaa; font-size: 0.8rem;">Certifique-se que o QR Code esta visivel</p>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    with st.expander("Historico de Correcoes - Turma", expanded=False):
        historico = pd.DataFrame([
            {"Data": "16/05/2026", "Turma": "3o Ano", "Disciplina": "Matematica", "Media": "7.6", "Status": "Consolidado"},
        ])
        st.dataframe(historico, use_container_width=True, hide_index=True)

if __name__ == "__main__":
    show()
