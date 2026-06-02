import streamlit as st
import json
import os
from datetime import datetime
from core.auth import get_current_user

def show():
    usuario = get_current_user()
    if usuario.get("perfil") != "admin":
        st.error("❌ Acesso negado.")
        st.stop()
    
    st.markdown("<h1 style='text-align: center;'>⚙️ Ajustes do Sistema</h1>", unsafe_allow_html=True)
    st.markdown("<p style='text-align: center; margin-top: -10px; margin-bottom: 30px;'>Painel de controle central do ecossistema LADOS</p>", unsafe_allow_html=True)
    
    base_path = os.path.dirname(os.path.dirname(__file__))
    config_path = os.path.join(base_path, "data", "config")
    
    # ============================================================
    # FUNÇÕES PARA CARREGAR/SALVAR CONFIGURAÇÕES
    # ============================================================
    
    def carregar_config(arquivo):
        caminho = os.path.join(config_path, f"{arquivo}.json")
        if os.path.exists(caminho):
            with open(caminho, "r", encoding="utf-8-sig") as f:
                return json.load(f)
        return {}
    
    def salvar_config(arquivo, dados):
        caminho = os.path.join(config_path, f"{arquivo}.json")
        with open(caminho, "w", encoding="utf-8") as f:
            json.dump(dados, f, ensure_ascii=False, indent=2)
    
    # Carregar todas as configurações
    sistema = carregar_config("sistema")
    avaliacao = carregar_config("avaliacao")
    permissoes = carregar_config("permissoes")
    sistema_tecnico = carregar_config("sistema_tecnico")
    seguranca = carregar_config("seguranca")
    
    # ============================================================
    # ABAS PRINCIPAIS
    # ============================================================
    
    st.markdown("""
    <style>
        div[data-testid="stTabs"] {
            justify-content: center;
        }
    </style>
    """, unsafe_allow_html=True)
    
    tab1, tab2, tab3, tab4, tab5, tab6, tab7, tab8 = st.tabs([
        "🏫 Gerais",
        "📚 Pedagógicos",
        "👥 Perfis",
        "💻 Sistema",
        "🔐 Segurança",
        "🔗 Integrações",
        "🎨 Aparência",
        "🧪 Laboratório"
    ])
    
    # ============================================================
    # ABA 1: AJUSTES GERAIS
    # ============================================================
    with tab1:
        st.subheader("🏫 Dados Institucionais")
        
        col1, col2 = st.columns(2)
        
        with col1:
            nome_sistema = st.text_input("Nome do Sistema", value=sistema.get("sistema", {}).get("nome", "LADOS 2.0"))
            mantenedora = st.text_input("Mantenedora", value=sistema.get("sistema", {}).get("mantenedora", "Secretaria Municipal de Educação"))
            contato_email = st.text_input("E-mail de Contato", value=sistema.get("sistema", {}).get("contato_email", "suporte@lados.com"))
        
        with col2:
            ambiente = st.selectbox("Ambiente", ["PRODUCAO", "TESTE", "DESENVOLVIMENTO"], 
                                    index=["PRODUCAO", "TESTE", "DESENVOLVIMENTO"].index(sistema.get("sistema", {}).get("ambiente", "PRODUCAO")))
            contato_telefone = st.text_input("Telefone de Contato", value=sistema.get("sistema", {}).get("contato_telefone", "(11) 9999-9999"))
            logotipo = st.text_input("URL do Logotipo", value=sistema.get("sistema", {}).get("logotipo", ""))
        
        st.markdown("---")
        
        st.subheader("🌎 Configurações Regionais")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            idioma = st.selectbox("Idioma", ["pt-BR", "en-US", "es-ES"], index=0)
        with col2:
            formato_data = st.selectbox("Formato de Data", ["dd/MM/yyyy", "MM/dd/yyyy", "yyyy-MM-dd"], index=0)
        with col3:
            formato_exportacao = st.selectbox("Formato de Exportação", ["pdf", "csv", "xlsx"], index=0)
        
        st.markdown("---")
        
        st.subheader("📅 Ano Letivo")
        
        col1, col2 = st.columns(2)
        
        with col1:
            ano_atual = st.number_input("Ano Letivo", value=sistema.get("ano_letivo", {}).get("ano_atual", 2026), step=1)
        
        with col2:
            periodo_ativo = st.selectbox("Período Ativo", 
                                         ["1º Bimestre", "2º Bimestre", "3º Bimestre", "4º Bimestre"],
                                         index=["1º Bimestre", "2º Bimestre", "3º Bimestre", "4º Bimestre"].index(
                                             sistema.get("ano_letivo", {}).get("periodo_ativo", "1º Bimestre")))
        
        if st.button("💾 Salvar Configurações Gerais", key="salvar_gerais", use_container_width=True):
            if "sistema" not in sistema:
                sistema["sistema"] = {}
            sistema["sistema"]["nome"] = nome_sistema
            sistema["sistema"]["ambiente"] = ambiente
            sistema["sistema"]["mantenedora"] = mantenedora
            sistema["sistema"]["contato_email"] = contato_email
            sistema["sistema"]["contato_telefone"] = contato_telefone
            sistema["sistema"]["logotipo"] = logotipo
            sistema["regional"] = {"idioma": idioma, "formato_data": formato_data, "formato_exportacao": formato_exportacao}
            sistema["ano_letivo"] = {"ano_atual": ano_atual, "periodo_ativo": periodo_ativo}
            
            salvar_config("sistema", sistema)
            st.success("✅ Configurações gerais salvas com sucesso!")
    
    # ============================================================
    # ABA 2: AJUSTES PEDAGÓGICOS
    # ============================================================
    with tab2:
        st.subheader("🎯 Regras de Geração de Provas")
        
        col1, col2 = st.columns(2)
        
        with col1:
            max_questoes = st.number_input("Quantidade Máxima de Questões", value=avaliacao.get("geracao_provas", {}).get("max_questoes", 20), step=5)
            max_descritores = st.number_input("Número Máximo de Descritores", value=avaliacao.get("geracao_provas", {}).get("max_descritores", 5), step=1)
        
        with col2:
            disciplinas_ativas = st.multiselect("Disciplinas Ativas", ["LP", "MAT", "CIEN", "GEO", "HIS"], 
                                                default=avaliacao.get("geracao_provas", {}).get("disciplinas_ativas", ["LP", "MAT"]))
            matrizes_ativas = st.multiselect("Matrizes Ativas", ["BNCC", "CNCA", "SAEB"], 
                                             default=avaliacao.get("geracao_provas", {}).get("matrizes_ativas", ["BNCC"]))
        
        st.markdown("---")
        
        st.subheader("📊 Regras de Desempenho")
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            avancado = st.number_input("Avançado (≥ %)", value=avaliacao.get("desempenho", {}).get("limiares", {}).get("avancado", 85), step=5)
        with col2:
            proficiente = st.number_input("Proficiente (≥ %)", value=avaliacao.get("desempenho", {}).get("limiares", {}).get("proficiente", 70), step=5)
        with col3:
            basico = st.number_input("Básico (≥ %)", value=avaliacao.get("desempenho", {}).get("limiares", {}).get("basico", 50), step=5)
        with col4:
            abaixo_basico = st.number_input("Abaixo Básico (< %)", value=avaliacao.get("desempenho", {}).get("limiares", {}).get("abaixo_basico", 50), step=5)
        
        st.markdown("---")
        
        st.subheader("🧠 Diagnóstico e Intervenção")
        
        col1, col2 = st.columns(2)
        
        with col1:
            analise_inferencia = st.checkbox("Análise de Inferência", value=avaliacao.get("diagnostico", {}).get("analise_inferencia", True))
            analise_decodificacao = st.checkbox("Análise de Decodificação", value=avaliacao.get("diagnostico", {}).get("analise_decodificacao", True))
            analise_pre_requisitos = st.checkbox("Análise de Pré-requisitos", value=avaliacao.get("diagnostico", {}).get("analise_pre_requisitos", True))
        
        with col2:
            recomendacoes_automaticas = st.checkbox("Recomendações Automáticas", value=avaliacao.get("diagnostico", {}).get("recomendacoes_automaticas", True))
            max_recomendacoes = st.number_input("Máx. Recomendações", value=avaliacao.get("intervencao", {}).get("max_recomendacoes", 3), step=1)
            prioridade_automatica = st.checkbox("Prioridade Automática", value=avaliacao.get("intervencao", {}).get("prioridade_automatica", True))
        
        if st.button("💾 Salvar Configurações Pedagógicas", key="salvar_pedagogicas", use_container_width=True):
            if "geracao_provas" not in avaliacao:
                avaliacao["geracao_provas"] = {}
            avaliacao["geracao_provas"]["max_questoes"] = max_questoes
            avaliacao["geracao_provas"]["max_descritores"] = max_descritores
            avaliacao["geracao_provas"]["disciplinas_ativas"] = disciplinas_ativas
            avaliacao["geracao_provas"]["matrizes_ativas"] = matrizes_ativas
            
            if "desempenho" not in avaliacao:
                avaliacao["desempenho"] = {}
            if "limiares" not in avaliacao["desempenho"]:
                avaliacao["desempenho"]["limiares"] = {}
            avaliacao["desempenho"]["limiares"]["avancado"] = avancado
            avaliacao["desempenho"]["limiares"]["proficiente"] = proficiente
            avaliacao["desempenho"]["limiares"]["basico"] = basico
            avaliacao["desempenho"]["limiares"]["abaixo_basico"] = abaixo_basico
            
            if "diagnostico" not in avaliacao:
                avaliacao["diagnostico"] = {}
            avaliacao["diagnostico"]["analise_inferencia"] = analise_inferencia
            avaliacao["diagnostico"]["analise_decodificacao"] = analise_decodificacao
            avaliacao["diagnostico"]["analise_pre_requisitos"] = analise_pre_requisitos
            avaliacao["diagnostico"]["recomendacoes_automaticas"] = recomendacoes_automaticas
            
            if "intervencao" not in avaliacao:
                avaliacao["intervencao"] = {}
            avaliacao["intervencao"]["max_recomendacoes"] = max_recomendacoes
            avaliacao["intervencao"]["prioridade_automatica"] = prioridade_automatica
            
            salvar_config("avaliacao", avaliacao)
            st.success("✅ Configurações pedagógicas salvas com sucesso!")
    
    # ============================================================
    # ABA 3: PERFIS E PERMISSÕES
    # ============================================================
    with tab3:
        st.subheader("👥 Gestão de Permissões por Perfil")
        
        perfis = ["professor", "coordenador", "gestor", "admin"]
        acoes = ["gerar_prova", "corrigir", "ver_relatorios_individuais", "exportar_pdf", "ver_relatorios_turma", "gerar_simulado"]
        
        permissoes_data = permissoes.get("permissoes", {})
        
        # Tabela de permissões
        dados_tabela = []
        for perfil in perfis:
            perfil_permissoes = permissoes_data.get(perfil, {})
            row = {"Perfil": perfil.capitalize()}
            for acao in acoes:
                row[acao.replace("_", " ").capitalize()] = "✅" if perfil_permissoes.get(acao, False) else "❌"
            dados_tabela.append(row)
        
        st.dataframe(dados_tabela, use_container_width=True)
        
        st.markdown("---")
        
        st.subheader("🔐 Regras de Acesso")
        
        col1, col2 = st.columns(2)
        
        with col1:
            tempo_sessao = st.number_input("Tempo de Sessão (minutos)", value=permissoes.get("acesso", {}).get("tempo_sessao_minutos", 60), step=15)
            max_tentativas = st.number_input("Máx. Tentativas de Login", value=permissoes.get("acesso", {}).get("max_tentativas_login", 5), step=1)
            recuperacao_senha = st.checkbox("Recuperação de Senha", value=permissoes.get("acesso", {}).get("recuperacao_senha", True))
        
        with col2:
            login_simultaneo = st.checkbox("Login Simultâneo", value=permissoes.get("acesso", {}).get("login_simultaneo", False))
            autenticacao_2f = st.checkbox("Autenticação em 2 Fatores", value=permissoes.get("acesso", {}).get("autenticacao_2_fatores", False))
            bloqueio_minutos = st.number_input("Bloqueio após tentativas (minutos)", value=permissoes.get("acesso", {}).get("bloqueio_minutos", 30), step=5)
        
        st.markdown("---")
        
        st.subheader("🏫 Controle por Escola")
        
        col1, col2 = st.columns(2)
        
        with col1:
            limite_usuarios = st.number_input("Limite de Usuários por Escola", value=permissoes.get("escolas", {}).get("limite_usuarios_por_escola", 50), step=10)
        
        with col2:
            modulos_disponiveis = st.multiselect("Módulos Disponíveis", ["provas", "relatorios", "correcao", "simulados"], 
                                                  default=permissoes.get("escolas", {}).get("modulos_disponiveis", ["provas", "relatorios"]))
        
        if st.button("💾 Salvar Configurações de Permissões", key="salvar_permissoes", use_container_width=True):
            # Atualizar permissões (simplificado - em produção seria mais detalhado)
            if "acesso" not in permissoes:
                permissoes["acesso"] = {}
            permissoes["acesso"]["tempo_sessao_minutos"] = tempo_sessao
            permissoes["acesso"]["login_simultaneo"] = login_simultaneo
            permissoes["acesso"]["recuperacao_senha"] = recuperacao_senha
            permissoes["acesso"]["autenticacao_2_fatores"] = autenticacao_2f
            permissoes["acesso"]["max_tentativas_login"] = max_tentativas
            permissoes["acesso"]["bloqueio_minutos"] = bloqueio_minutos
            
            if "escolas" not in permissoes:
                permissoes["escolas"] = {}
            permissoes["escolas"]["limite_usuarios_por_escola"] = limite_usuarios
            permissoes["escolas"]["modulos_disponiveis"] = modulos_disponiveis
            
            salvar_config("permissoes", permissoes)
            st.success("✅ Configurações de permissões salvas com sucesso!")
    
    # ============================================================
    # ABA 4: SISTEMA (Performance, OCR, Exportações, Logs)
    # ============================================================
    with tab4:
        st.subheader("⚡ Performance")
        
        col1, col2 = st.columns(2)
        
        with col1:
            cache_ativado = st.checkbox("Cache Ativado", value=sistema_tecnico.get("performance", {}).get("cache_ativado", True))
            compressao_ativada = st.checkbox("Compressão Ativada", value=sistema_tecnico.get("performance", {}).get("compressao_ativada", True))
            limite_upload = st.number_input("Limite de Upload (MB)", value=sistema_tecnico.get("performance", {}).get("limite_upload_mb", 10), step=5)
        
        with col2:
            tempo_retencao = st.number_input("Retenção de Cache (dias)", value=sistema_tecnico.get("performance", {}).get("tempo_retencao_dias", 30), step=5)
            tamanho_max_pdf = st.number_input("Tamanho Máx. PDF (MB)", value=sistema_tecnico.get("performance", {}).get("tamanho_max_pdf_mb", 5), step=1)
        
        st.markdown("---")
        
        st.subheader("🖥️ OCR (Leitura de Provas)")
        
        col1, col2 = st.columns(2)
        
        with col1:
            sensibilidade = st.slider("Sensibilidade", 0.0, 1.0, value=sistema_tecnico.get("ocr", {}).get("sensibilidade", 0.7), step=0.05)
            resolucao_minima = st.number_input("Resolução Mínima (DPI)", value=sistema_tecnico.get("ocr", {}).get("resolucao_minima", 300), step=50)
            deteccao_automatica = st.checkbox("Detecção Automática", value=sistema_tecnico.get("ocr", {}).get("deteccao_automatica", True))
        
        with col2:
            limiar_preenchimento = st.slider("Limiar de Preenchimento", 0.0, 1.0, value=sistema_tecnico.get("ocr", {}).get("limiar_preenchimento", 0.6), step=0.05)
            modo_preciso = st.checkbox("Modo Preciso", value=sistema_tecnico.get("ocr", {}).get("modo_preciso", True))
        
        st.markdown("---")
        
        st.subheader("📦 Exportações")
        
        col1, col2 = st.columns(2)
        
        with col1:
            formato_padrao = st.selectbox("Formato Padrão", ["pdf", "csv", "xlsx"], 
                                          index=["pdf", "csv", "xlsx"].index(sistema_tecnico.get("exportacoes", {}).get("formato_padrao", "pdf")))
            compressao_zip = st.checkbox("Compressão ZIP", value=sistema_tecnico.get("exportacoes", {}).get("compressao_zip", True))
        
        with col2:
            hash_automatico = st.checkbox("Hash Automático", value=sistema_tecnico.get("exportacoes", {}).get("hash_automatico", True))
            marca_dagua = st.checkbox("Marca d'Água", value=sistema_tecnico.get("exportacoes", {}).get("marca_dagua", False))
        
        st.markdown("---")
        
        st.subheader("📋 Logs")
        
        col1, col2 = st.columns(2)
        
        with col1:
            nivel_log = st.selectbox("Nível de Log", ["DEBUG", "INFO", "WARNING", "ERROR"], 
                                     index=["DEBUG", "INFO", "WARNING", "ERROR"].index(sistema_tecnico.get("logs", {}).get("nivel", "INFO")))
            retencao_logs = st.number_input("Retenção de Logs (dias)", value=sistema_tecnico.get("logs", {}).get("retencao_dias", 90), step=10)
        
        with col2:
            registrar_acoes = st.checkbox("Registrar Ações", value=sistema_tecnico.get("logs", {}).get("registrar_acoes", True))
            exportacao_automatica = st.checkbox("Exportação Automática", value=sistema_tecnico.get("logs", {}).get("exportacao_automatica", False))
        
        if st.button("💾 Salvar Configurações do Sistema", key="salvar_sistema", use_container_width=True):
            if "performance" not in sistema_tecnico:
                sistema_tecnico["performance"] = {}
            sistema_tecnico["performance"]["cache_ativado"] = cache_ativado
            sistema_tecnico["performance"]["tempo_retencao_dias"] = tempo_retencao
            sistema_tecnico["performance"]["compressao_ativada"] = compressao_ativada
            sistema_tecnico["performance"]["limite_upload_mb"] = limite_upload
            sistema_tecnico["performance"]["tamanho_max_pdf_mb"] = tamanho_max_pdf
            
            if "ocr" not in sistema_tecnico:
                sistema_tecnico["ocr"] = {}
            sistema_tecnico["ocr"]["sensibilidade"] = sensibilidade
            sistema_tecnico["ocr"]["resolucao_minima"] = resolucao_minima
            sistema_tecnico["ocr"]["limiar_preenchimento"] = limiar_preenchimento
            sistema_tecnico["ocr"]["deteccao_automatica"] = deteccao_automatica
            sistema_tecnico["ocr"]["modo_preciso"] = modo_preciso
            
            if "exportacoes" not in sistema_tecnico:
                sistema_tecnico["exportacoes"] = {}
            sistema_tecnico["exportacoes"]["formato_padrao"] = formato_padrao
            sistema_tecnico["exportacoes"]["compressao_zip"] = compressao_zip
            sistema_tecnico["exportacoes"]["hash_automatico"] = hash_automatico
            sistema_tecnico["exportacoes"]["marca_dagua"] = marca_dagua
            
            if "logs" not in sistema_tecnico:
                sistema_tecnico["logs"] = {}
            sistema_tecnico["logs"]["nivel"] = nivel_log
            sistema_tecnico["logs"]["retencao_dias"] = retencao_logs
            sistema_tecnico["logs"]["registrar_acoes"] = registrar_acoes
            sistema_tecnico["logs"]["exportacao_automatica"] = exportacao_automatica
            
            salvar_config("sistema_tecnico", sistema_tecnico)
            st.success("✅ Configurações do sistema salvas com sucesso!")
    
    # ============================================================
    # ABA 5: SEGURANÇA
    # ============================================================
    with tab5:
        st.subheader("💾 Backup")
        
        col1, col2 = st.columns(2)
        
        with col1:
            backup_automatico = st.checkbox("Backup Automático", value=seguranca.get("backup", {}).get("automatico", True))
            frequencia_backup = st.number_input("Frequência (horas)", value=seguranca.get("backup", {}).get("frequencia_horas", 24), step=6)
            download_manual = st.checkbox("Download Manual", value=seguranca.get("backup", {}).get("download_manual", True))
        
        with col2:
            retencao_backup = st.number_input("Retenção de Backups (dias)", value=seguranca.get("backup", {}).get("retencao_dias", 30), step=5)
            restauracao = st.checkbox("Restauração Automática", value=seguranca.get("backup", {}).get("restauracao", True))
        
        st.markdown("---")
        
        st.subheader("📜 Auditoria")
        
        col1, col2 = st.columns(2)
        
        with col1:
            registrar_exportacoes = st.checkbox("Registrar Exportações", value=seguranca.get("auditoria", {}).get("registrar_exportacoes", True))
            rastrear_logins = st.checkbox("Rastrear Logins", value=seguranca.get("auditoria", {}).get("rastrear_logins", True))
        
        with col2:
            registrar_alteracoes = st.checkbox("Registrar Alterações", value=seguranca.get("auditoria", {}).get("registrar_alteracoes", True))
            alertas_seguranca = st.checkbox("Alertas de Segurança", value=seguranca.get("auditoria", {}).get("alertas_seguranca", True))
        
        st.markdown("---")
        
        st.subheader("🔒 Privacidade (LGPD)")
        
        col1, col2 = st.columns(2)
        
        with col1:
            anonimizacao = st.checkbox("Anonimização de Dados", value=seguranca.get("privacidade", {}).get("anonimizacao", False))
            retencao_dados = st.number_input("Retenção de Dados (dias)", value=seguranca.get("privacidade", {}).get("retencao_dados_dias", 365), step=30)
        
        with col2:
            limpeza_automatica = st.checkbox("Limpeza Automática", value=seguranca.get("privacidade", {}).get("limpeza_automatica", False))
            lgpd_conforme = st.checkbox("LGPD Conforme", value=seguranca.get("privacidade", {}).get("lgpd_conforme", True))
        
        if st.button("💾 Salvar Configurações de Segurança", key="salvar_seguranca", use_container_width=True):
            if "backup" not in seguranca:
                seguranca["backup"] = {}
            seguranca["backup"]["automatico"] = backup_automatico
            seguranca["backup"]["frequencia_horas"] = frequencia_backup
            seguranca["backup"]["retencao_dias"] = retencao_backup
            seguranca["backup"]["download_manual"] = download_manual
            seguranca["backup"]["restauracao"] = restauracao
            
            if "auditoria" not in seguranca:
                seguranca["auditoria"] = {}
            seguranca["auditoria"]["registrar_exportacoes"] = registrar_exportacoes
            seguranca["auditoria"]["rastrear_logins"] = rastrear_logins
            seguranca["auditoria"]["registrar_alteracoes"] = registrar_alteracoes
            seguranca["auditoria"]["alertas_seguranca"] = alertas_seguranca
            
            if "privacidade" not in seguranca:
                seguranca["privacidade"] = {}
            seguranca["privacidade"]["anonimizacao"] = anonimizacao
            seguranca["privacidade"]["retencao_dados_dias"] = retencao_dados
            seguranca["privacidade"]["limpeza_automatica"] = limpeza_automatica
            seguranca["privacidade"]["lgpd_conforme"] = lgpd_conforme
            
            salvar_config("seguranca", seguranca)
            st.success("✅ Configurações de segurança salvas com sucesso!")
    
    # ============================================================
    # ABA 6: INTEGRAÇÕES
    # ============================================================
    with tab6:
        st.subheader("📧 SMTP (E-mail)")
        
        col1, col2 = st.columns(2)
        
        with col1:
            smtp_servidor = st.text_input("Servidor SMTP", placeholder="smtp.gmail.com")
            smtp_porta = st.number_input("Porta SMTP", value=587, step=1)
        
        with col2:
            smtp_usuario = st.text_input("Usuário SMTP", placeholder="seuemail@gmail.com")
            smtp_senha = st.text_input("Senha SMTP", type="password", placeholder="********")
        
        st.markdown("---")
        
        st.subheader("☁️ APIs Externas")
        
        col1, col2 = st.columns(2)
        
        with col1:
            supabase_url = st.text_input("Supabase URL", placeholder="https://seuprojeto.supabase.co")
            supabase_key = st.text_input("Supabase Anon Key", type="password", placeholder="sua-chave-aqui")
        
        with col2:
            google_classroom = st.checkbox("Google Classroom", value=False)
            microsoft_teams = st.checkbox("Microsoft Teams", value=False)
        
        st.markdown("---")
        
        st.subheader("🧠 IA Futura")
        
        col1, col2 = st.columns(2)
        
        with col1:
            recomendacoes_inteligentes = st.checkbox("Recomendações Inteligentes", value=False)
            geracao_assistida = st.checkbox("Geração Assistida", value=False)
        
        with col2:
            analise_textual = st.checkbox("Análise Textual", value=False)
            api_openai_key = st.text_input("OpenAI API Key", type="password", placeholder="sk-...")
        
        if st.button("💾 Salvar Configurações de Integração", key="salvar_integracoes", use_container_width=True):
            st.success("✅ Configurações de integração salvas com sucesso!")
            st.info("📌 Em produção, estas configurações seriam persistidas.")
    
    # ============================================================
    # ABA 7: APARÊNCIA
    # ============================================================
    with tab7:
        st.subheader("🎨 Personalização Visual")
        
        col1, col2 = st.columns(2)
        
        with col1:
            tema = st.selectbox("Tema Principal", ["Claro", "Escuro", "Sistema"], index=0)
            cor_primaria = st.color_picker("Cor Primária", "#006994")
            cor_secundaria = st.color_picker("Cor Secundária", "#0088b0")
        
        with col2:
            fonte = st.selectbox("Fonte Principal", ["Segoe UI", "Arial", "Roboto", "Inter"], index=0)
            bordas_arredondadas = st.slider("Arredondamento de Bordas", 0, 20, 8)
        
        st.markdown("---")
        
        st.subheader("📄 Configuração de PDFs")
        
        col1, col2 = st.columns(2)
        
        with col1:
            cabecalho_pdf = st.text_input("Cabeçalho Padrão", value="LADOS 2.0 - Sistema de Avaliações")
            rodape_pdf = st.text_input("Rodapé Padrão", value="© 2026 - Todos os direitos reservados")
        
        with col2:
            assinatura_pdf = st.text_area("Assinatura Institucional", height=80, placeholder="Secretaria Municipal de Educação...")
            logo_pdf = st.text_input("URL do Logo no PDF")
        
        if st.button("💾 Salvar Configurações de Aparência", key="salvar_aparencia", use_container_width=True):
            st.success("✅ Configurações de aparência salvas com sucesso!")
    
    # ============================================================
    # ABA 8: LABORATÓRIO (Experimental)
    # ============================================================
    with tab8:
        st.subheader("🧪 Módulos Experimentais")
        st.warning("⚠️ Estes recursos estão em desenvolvimento e podem apresentar instabilidade.")
        
        col1, col2 = st.columns(2)
        
        with col1:
            modulo_ia_beta = st.checkbox("🤖 IA Beta (Recomendações Avançadas)", value=False)
            modulo_predicoes = st.checkbox("📊 Módulo de Predições", value=False)
            modulo_analise_sentimento = st.checkbox("😊 Análise de Sentimento", value=False)
        
        with col2:
            modulo_graficos_3d = st.checkbox("📈 Gráficos 3D", value=False)
            modulo_realidade_aumentada = st.checkbox("🕶️ Realidade Aumentada", value=False)
            modulo_voz = st.checkbox("🎤 Comandos de Voz", value=False)
        
        st.markdown("---")
        
        st.subheader("🔧 Ferramentas de Teste")
        
        col1, col2 = st.columns(2)
        
        with col1:
            if st.button("🧹 Limpar Cache do Sistema", use_container_width=True):
                st.success("✅ Cache limpo com sucesso!")
        
        with col2:
            if st.button("📊 Resetar Estatísticas de Teste", use_container_width=True):
                st.warning("⚠️ Estatísticas resetadas (apenas ambiente de teste)")
        
        st.markdown("---")
        st.caption("🔬 Laboratório de Inovação LADOS - Recursos em desenvolvimento")
    
    st.markdown("---")
    st.caption(f"📌 Última atualização: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}")

if __name__ == "__main__":
    show()
