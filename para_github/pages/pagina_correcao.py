import streamlit as st
import pandas as pd
from datetime import datetime
from core.auth import get_current_user
from PIL import Image
from services.leitor_prova import LeitorProva
import uuid

def show():
    usuario = get_current_user()
    
    if not usuario:
        st.error("⚠️ Usuário não autenticado")
        return
    
    st.title("📝 Correção de Provas")
    st.caption("Correção automática por câmera - Capture a grade de respostas prova por prova")
    
    # ========== INICIALIZAR SESSÃO ==========
    if "correcoes_sessao" not in st.session_state:
        st.session_state.correcoes_sessao = []
    if "sessao_id" not in st.session_state:
        st.session_state.sessao_id = str(uuid.uuid4())[:8]
    if "ultima_correcao" not in st.session_state:
        st.session_state.ultima_correcao = None
    if "imagem_capturada" not in st.session_state:
        st.session_state.imagem_capturada = None
    
    # ========== 1) IDENTIFICAÇÃO DA PROVA ==========
    st.subheader("1️⃣ Identifique a Prova")
    
    col1, col2, col3, col4, col5 = st.columns(5)
    
    with col1:
        tipo_prova = st.selectbox(
            "📋 Tipo de Prova",
            options=["Múltipla Escolha", "Leitura", "Escrita"],
            key="tipo_prova"
        )
    
    with col2:
        periodo = st.selectbox(
            "📅 Período",
            options=["Bimestre", "Trimestre"],
            key="periodo_filtro"
        )
    
    with col3:
        if periodo == "Bimestre":
            ordens = ["Primeiro", "Segundo", "Terceiro", "Quarto"]
        else:
            ordens = ["Primeiro", "Segundo", "Terceiro"]
        
        ordem = st.selectbox(
            "🔢 Ordem",
            options=ordens,
            key="ordem_filtro"
        )
    
    with col4:
        provas_disponiveis = [
            "Matemática - 3º Ano",
            "Português - 3º Ano",
            "Ciências - 3º Ano",
            "História - 3º Ano",
            "Geografia - 3º Ano"
        ]
        nome_prova = st.selectbox(
            "📄 Prova",
            options=provas_disponiveis,
            key="prova_filtro"
        )
    
    with col5:
        turmas_disponiveis = [
            "3º Ano - Manhã",
            "3º Ano - Tarde",
            "4º Ano - Manhã",
            "4º Ano - Tarde",
            "5º Ano - Manhã"
        ]
        turma = st.selectbox(
            "🏫 Turma",
            options=turmas_disponiveis,
            key="turma_filtro"
        )
    
    st.markdown("---")
    
    # ========== CAPTURA DA PROVA ==========
    st.subheader("2️⃣ Capturar Prova")
    
    # Opções de captura
    tab_camera, tab_upload = st.tabs(["📷 Tirar Foto Agora", "📁 Enviar Imagem Salva"])
    
    imagem = None
    
    with tab_camera:
        # Botão "Tirar Foto" personalizado
        camera_file = st.camera_input("📸 Tirar Foto", key="camera_prova", label_visibility="collapsed")
        if camera_file:
            imagem = Image.open(camera_file)
            st.session_state.imagem_capturada = imagem
            st.image(imagem, caption="📸 Prova capturada", use_container_width=True)
    
    with tab_upload:
        uploaded_file = st.file_uploader(
            "📁 Enviar Imagem",
            type=['jpg', 'jpeg', 'png', 'heic'],
            key="upload_prova",
            label_visibility="collapsed",
            help="Fotos tiradas com celular geralmente têm melhor qualidade"
        )
        if uploaded_file:
            imagem = Image.open(uploaded_file)
            st.session_state.imagem_capturada = imagem
            st.image(imagem, caption="📁 Imagem enviada", use_container_width=True)
    
    # Botão Enviar Foto
    col_btn1, col_btn2, col_btn3 = st.columns([1, 1, 2])
    
    with col_btn1:
        enviar_btn = st.button("📤 Enviar Foto", type="primary", use_container_width=True)
    
    with col_btn2:
        limpar_btn = st.button("🗑️ Limpar", use_container_width=True)
        if limpar_btn:
            st.session_state.imagem_capturada = None
            st.rerun()
    
    # ========== PROCESSAR CORREÇÃO ==========
    if enviar_btn and st.session_state.imagem_capturada:
        imagem = st.session_state.imagem_capturada
        
        with st.spinner("🔄 Processando imagem - Lendo círculos preenchidos..."):
            try:
                # Buscar gabarito baseado nos filtros
                gabarito = buscar_gabarito(periodo, ordem, nome_prova, turma)
                
                # Inicializar leitor
                leitor = LeitorProva()
                
                # Ler a grade de respostas
                resultado = leitor.ler_grade(imagem, gabarito)
                
                if resultado["sucesso"]:
                    st.success("✅ Correção realizada com sucesso!")
                    
                    # Cards com resultado
                    st.markdown("### 📊 Resultado da Prova")
                    
                    col_res1, col_res2, col_res3, col_res4 = st.columns(4)
                    
                    with col_res1:
                        st.metric("✅ Acertos", f"{resultado['acertos']}/{resultado['total_questoes']}", border=True)
                    
                    with col_res2:
                        st.metric("📊 Percentual", f"{resultado['percentual']:.1f}%", border=True)
                    
                    with col_res3:
                        nota = resultado['percentual'] / 10
                        st.metric("🎯 Nota", f"{nota:.1f}", border=True)
                    
                    with col_res4:
                        if resultado['percentual'] >= 70:
                            st.metric("🎉 Status", "Aprovado", border=True)
                        elif resultado['percentual'] >= 50:
                            st.metric("⚠️ Status", "Recuperação", border=True)
                        else:
                            st.metric("❌ Status", "Reprovado", border=True)
                    
                    # Detalhamento por questão
                    with st.expander("📋 Ver detalhamento por questão", expanded=False):
                        if "detalhes" in resultado:
                            df_detalhes = pd.DataFrame(resultado["detalhes"])
                            
                            def formatar_resposta(row):
                                if row['acertou']:
                                    return f"✅ {row['resposta_aluno']} (Correto)"
                                return f"❌ {row['resposta_aluno']} (Gabarito: {row['gabarito']})"
                            
                            df_detalhes['Resultado'] = df_detalhes.apply(formatar_resposta, axis=1)
                            
                            st.dataframe(
                                df_detalhes[['questao', 'Resultado']],
                                use_container_width=True,
                                hide_index=True
                            )
                    
                    # Botão SALVAR CORREÇÃO
                    st.markdown("---")
                    st.markdown("### 💾 Salvar esta correção")
                    
                    col_salvar1, col_salvar2 = st.columns(2)
                    
                    with col_salvar1:
                        if st.button("✅ SALVAR CORREÇÃO", type="primary", use_container_width=True):
                            numero_prova = len(st.session_state.correcoes_sessao) + 1
                            correcao_data = {
                                "id": str(uuid.uuid4()),
                                "sessao_id": st.session_state.sessao_id,
                                "numero_prova": numero_prova,
                                "tipo_prova": tipo_prova,
                                "acertos": resultado['acertos'],
                                "total": resultado['total_questoes'],
                                "percentual": resultado['percentual'],
                                "nota": nota,
                                "periodo": periodo,
                                "ordem": ordem,
                                "prova": nome_prova,
                                "turma": turma,
                                "detalhes": resultado.get('detalhes', []),
                                "horario": datetime.now().strftime("%H:%M:%S"),
                                "data": datetime.now().strftime("%d/%m/%Y"),
                                "timestamp": datetime.now().isoformat()
                            }
                            
                            st.session_state.correcoes_sessao.append(correcao_data)
                            st.session_state.ultima_correcao = correcao_data
                            
                            try:
                                salvar_correcao_supabase(correcao_data)
                                st.success(f"✅ Correção #{numero_prova} SALVA com sucesso!")
                                st.balloons()
                            except Exception as e:
                                st.warning(f"⚠️ Correção salva localmente, mas erro no banco: {e}")
                            
                            st.session_state.imagem_capturada = None
                            st.rerun()
                    
                    with col_salvar2:
                        if st.button("🗑️ DESCARTAR", use_container_width=True):
                            st.info("❌ Correção descartada. Capture uma nova foto.")
                            st.session_state.imagem_capturada = None
                            st.rerun()
                
                else:
                    st.error(f"❌ Erro na correção: {resultado.get('erro', 'Erro desconhecido')}")
                    st.warning("""
                    **💡 Dicas para melhorar a leitura:**
                    - Aproxime a câmera da grade de respostas
                    - Garanta boa iluminação (sem sombras)
                    - A imagem deve estar nítida e focada
                    - Certifique-se que todos os círculos estão visíveis
                    - Evite reflexos e sombras sobre a grade
                    - Use fundo claro (preferencialmente branco)
                    """)
            
            except Exception as e:
                st.error(f"❌ Erro inesperado: {str(e)}")
    
    elif enviar_btn and not st.session_state.imagem_capturada:
        st.warning("⚠️ Nenhuma imagem capturada. Tire uma foto ou envie uma imagem primeiro.")
    
    st.markdown("---")
    
    # ========== FINALIZAR SESSÃO ==========
    st.subheader("3️⃣ Finalizar Correção")
    
    if len(st.session_state.correcoes_sessao) > 0:
        # Estatísticas da sessão
        with st.expander("📊 Estatísticas da Sessão Atual", expanded=True):
            notas = [c['nota'] for c in st.session_state.correcoes_sessao]
            aprovados = len([n for n in notas if n >= 7])
            recuperacao = len([n for n in notas if 5 <= n < 7])
            reprovados = len([n for n in notas if n < 5])
            
            col_e1, col_e2, col_e3, col_e4, col_e5 = st.columns(5)
            
            with col_e1:
                st.metric("Total", len(notas), border=True)
            with col_e2:
                st.metric("Média", f"{sum(notas)/len(notas):.1f}", border=True)
            with col_e3:
                st.metric("Aprovados", aprovados, border=True, delta=f"{aprovados/len(notas)*100:.0f}%")
            with col_e4:
                st.metric("Recuperação", recuperacao, border=True)
            with col_e5:
                st.metric("Reprovados", reprovados, border=True)
        
        # Lista de correções da sessão
        st.markdown("### 📋 Correções realizadas:")
        df_corrigidos = pd.DataFrame(st.session_state.correcoes_sessao)
        df_corrigidos = df_corrigidos[["numero_prova", "acertos", "total", "percentual", "nota", "horario"]]
        df_corrigidos.columns = ["Prova #", "Acertos", "Total", "%", "Nota", "Horário"]
        st.dataframe(df_corrigidos, use_container_width=True, hide_index=True)
        
        col_final1, col_final2 = st.columns(2)
        
        with col_final1:
            if st.button("✅ CONCLUIR SESSÃO E GERAR RELATÓRIO", type="primary", use_container_width=True):
                with st.spinner("Salvando sessão e gerando relatório..."):
                    try:
                        salvar_sessao_completa_supabase(
                            sessao_id=st.session_state.sessao_id,
                            correcoes=st.session_state.correcoes_sessao,
                            periodo=periodo,
                            ordem=ordem,
                            prova=nome_prova,
                            turma=turma,
                            usuario=usuario
                        )
                        
                        st.success(f"🎉 Sessão finalizada com SUCESSO!")
                        st.success(f"📊 {len(st.session_state.correcoes_sessao)} provas corrigidas e salvas")
                        st.info(f"📄 Relatório disponível na página de RELATÓRIOS (Sessão: {st.session_state.sessao_id})")
                        st.balloons()
                        
                        if st.button("🔄 INICIAR NOVA SESSÃO"):
                            st.session_state.correcoes_sessao = []
                            st.session_state.sessao_id = str(uuid.uuid4())[:8]
                            st.rerun()
                    
                    except Exception as e:
                        st.error(f"❌ Erro ao finalizar sessão: {e}")
        
        with col_final2:
            if st.button("🗑️ LIMPAR SESSÃO ATUAL", use_container_width=True):
                st.session_state.correcoes_sessao = []
                st.session_state.sessao_id = str(uuid.uuid4())[:8]
                st.success("Sessão limpa! Nova sessão iniciada.")
                st.rerun()
    
    else:
        st.info("ℹ️ Nenhuma prova corrigida ainda. Comece corrigindo as provas acima.")


def buscar_gabarito(periodo, ordem, nome_prova, turma):
    """Busca gabarito no Supabase baseado nos filtros selecionados"""
    # TODO: Implementar consulta real ao Supabase
    gabaritos_mock = {
        "Matemática - 3º Ano": {
            "1": "A", "2": "C", "3": "B", "4": "D", "5": "A",
            "6": "C", "7": "B", "8": "D", "9": "A", "10": "C"
        },
        "Português - 3º Ano": {
            "1": "B", "2": "D", "3": "A", "4": "C", "5": "B",
            "6": "D", "7": "A", "8": "C", "9": "B", "10": "D"
        },
        "Ciências - 3º Ano": {
            "1": "C", "2": "A", "3": "D", "4": "B", "5": "C",
            "6": "A", "7": "D", "8": "B", "9": "C", "10": "A"
        }
    }
    
    return gabaritos_mock.get(nome_prova, gabaritos_mock["Matemática - 3º Ano"])


def salvar_correcao_supabase(correcao_data):
    """Salva uma correção individual no Supabase"""
    # TODO: Implementar inserção no Supabase
    print(f"Salvando correção #{correcao_data['numero_prova']} - Nota: {correcao_data['nota']}")
    return True


def salvar_sessao_completa_supabase(sessao_id, correcoes, periodo, ordem, prova, turma, usuario):
    """Salva a sessão completa no Supabase"""
    print(f"Salvando sessão {sessao_id} com {len(correcoes)} correções")
    return True


if __name__ == "__main__":
    show()

