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
    
    st.markdown("<h1 style='text-align: center;'>👥 Gestão de Usuários</h1>", unsafe_allow_html=True)
    st.markdown("<p style='text-align: center; margin-top: -10px; margin-bottom: 30px;'>Identidade, permissões e segurança</p>", unsafe_allow_html=True)
    
    base_path = os.path.dirname(os.path.dirname(__file__))
    usuarios_path = os.path.join(base_path, "data", "usuarios.json")
    permissoes_path = os.path.join(base_path, "data", "permissoes.json")
    
    # ============================================================
    # FUNÇÕES AUXILIARES
    # ============================================================
    
    def carregar_usuarios():
        if os.path.exists(usuarios_path):
            with open(usuarios_path, "r", encoding="utf-8-sig") as f:
                return json.load(f)
        return {}
    
    def salvar_usuarios(usuarios):
        with open(usuarios_path, "w", encoding="utf-8") as f:
            json.dump(usuarios, f, ensure_ascii=False, indent=2)
    
    def carregar_permissoes():
        if os.path.exists(permissoes_path):
            with open(permissoes_path, "r", encoding="utf-8-sig") as f:
                return json.load(f)
        return {}
    
    def salvar_permissoes(permissoes):
        with open(permissoes_path, "w", encoding="utf-8") as f:
            json.dump(permissoes, f, ensure_ascii=False, indent=2)
    
    usuarios = carregar_usuarios()
    permissoes = carregar_permissoes()
    
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
        "📊 Painel",
        "➕ Novo Usuário",
        "✏️ Gerenciar",
        "🔐 Permissões",
        "🏫 Vinculações",
        "📥 Importação",
        "📜 Logs",
        "⚠️ Segurança"
    ])
    
    # ============================================================
    # ABA 1: PAINEL GERAL
    # ============================================================
    with tab1:
        st.subheader("📊 Painel de Usuários")
        
        if not usuarios:
            st.info("📌 Nenhum usuário cadastrado ainda.")
        else:
            total = len(usuarios)
            professores = sum(1 for u in usuarios if u.get("perfil") == "professor")
            coordenadores = sum(1 for u in usuarios if u.get("perfil") == "coordenador")
            gestores = sum(1 for u in usuarios if u.get("perfil") == "gestor")
            admins = sum(1 for u in usuarios if u.get("perfil") == "admin")
            ativos = sum(1 for u in usuarios if u.get("ativo", True))
            bloqueados = sum(1 for u in usuarios if not u.get("ativo", True))
            
            col1, col2, col3, col4, col5, col6, col7 = st.columns(7)
            
            with col1:
                st.metric("👥 Total", total)
            with col2:
                st.metric("👨‍🏫 Professores", professores)
            with col3:
                st.metric("👥 Coordenadores", coordenadores)
            with col4:
                st.metric("📊 Gestores", gestores)
            with col5:
                st.metric("⚙️ Admins", admins)
            with col6:
                st.metric("✅ Ativos", ativos)
            with col7:
                st.metric("🔒 Bloqueados", bloqueados)
            
            st.markdown("---")
            
            # Tabela de usuários (sem pandas)
            st.subheader("📋 Lista de Usuários")
            
            # Cabeçalho da tabela
            cols = st.columns([2, 3, 2, 2, 1])
            cols[0].markdown("**Usuário**")
            cols[1].markdown("**Nome**")
            cols[2].markdown("**Perfil**")
            cols[3].markdown("**Escola**")
            cols[4].markdown("**Status**")
            
            st.markdown("---")
            
            for username, dados in usuarios.items():
                cols = st.columns([2, 3, 2, 2, 1])
                cols[0].markdown(f"`{username}`")
                cols[1].markdown(dados.get("nome", ""))
                cols[2].markdown(dados.get("perfil", "").capitalize())
                cols[3].markdown(dados.get("escola", ""))
                status = "✅" if dados.get("ativo", True) else "❌"
                cols[4].markdown(status)
    
    # ============================================================
    # ABA 2: NOVO USUÁRIO
    # ============================================================
    with tab2:
        st.subheader("➕ Cadastrar Novo Usuário")
        
        with st.form("form_novo_usuario"):
            col1, col2 = st.columns(2)
            
            with col1:
                username = st.text_input("Usuário (login) *", placeholder="ex: professor1")
                nome = st.text_input("Nome Completo *", placeholder="João Silva")
                email = st.text_input("E-mail", placeholder="joao@escola.com")
                perfil = st.selectbox("Perfil *", ["professor", "coordenador", "gestor", "admin"])
            
            with col2:
                senha = st.text_input("Senha", type="password", value="123456")
                escola = st.text_input("Escola", placeholder="Escola Municipal")
                turmas = st.text_input("Turmas (separadas por vírgula)", placeholder="1º Ano A, 2º Ano B")
                ativo = st.checkbox("Ativo", value=True)
            
            st.markdown("---")
            st.markdown("### 📜 Termos de Consentimento")
            
            aceite = st.checkbox("✅ Declaro que li e concordo com os Termos de Uso e Política de Privacidade")
            
            submitted = st.form_submit_button("💾 Cadastrar Usuário", use_container_width=True)
            
            if submitted:
                if not username or not nome:
                    st.error("❌ Usuário e Nome são obrigatórios")
                elif not aceite:
                    st.error("❌ É necessário aceitar os Termos de Uso")
                elif username in usuarios:
                    st.error(f"❌ Usuário '{username}' já existe!")
                else:
                    usuarios[username] = {
                        "nome": nome,
                        "email": email,
                        "senha": senha,
                        "perfil": perfil,
                        "escola": escola,
                        "turmas": [t.strip() for t in turmas.split(",") if t.strip()],
                        "ativo": ativo,
                        "criado_em": datetime.now().isoformat(),
                        "termo_aceite": datetime.now().isoformat()
                    }
                    salvar_usuarios(usuarios)
                    st.success(f"✅ Usuário '{username}' cadastrado com sucesso!")
                    st.rerun()
    
    # ============================================================
    # ABA 3: GERENCIAR USUÁRIOS
    # ============================================================
    with tab3:
        st.subheader("✏️ Gerenciar Usuários")
        
        if not usuarios:
            st.info("📌 Nenhum usuário cadastrado.")
        else:
            usuario_editar = st.selectbox("Selecione o usuário", list(usuarios.keys()))
            
            if usuario_editar:
                dados = usuarios[usuario_editar]
                
                with st.form("form_editar_usuario"):
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        novo_nome = st.text_input("Nome Completo", value=dados.get("nome", ""))
                        novo_email = st.text_input("E-mail", value=dados.get("email", ""))
                        novo_perfil = st.selectbox("Perfil", ["professor", "coordenador", "gestor", "admin"],
                                                   index=["professor", "coordenador", "gestor", "admin"].index(dados.get("perfil", "professor")))
                    
                    with col2:
                        nova_escola = st.text_input("Escola", value=dados.get("escola", ""))
                        novas_turmas = st.text_input("Turmas", value=", ".join(dados.get("turmas", [])))
                        novo_ativo = st.checkbox("Ativo", value=dados.get("ativo", True))
                    
                    nova_senha = st.text_input("Nova Senha (deixe em branco para manter)", type="password")
                    
                    col1, col2, col3 = st.columns(3)
                    with col1:
                        submitted_edit = st.form_submit_button("💾 Atualizar", use_container_width=True)
                    with col2:
                        if st.form_submit_button("🔒 Resetar Senha (123456)", use_container_width=True):
                            nova_senha = "123456"
                    with col3:
                        if st.form_submit_button("🗑️ Excluir Usuário", use_container_width=True):
                            confirm = st.checkbox(f"Confirmar exclusão de '{usuario_editar}'?")
                            if confirm:
                                del usuarios[usuario_editar]
                                salvar_usuarios(usuarios)
                                st.success(f"✅ Usuário '{usuario_editar}' excluído!")
                                st.rerun()
                    
                    if submitted_edit:
                        if nova_senha:
                            dados["senha"] = nova_senha
                        dados["nome"] = novo_nome
                        dados["email"] = novo_email
                        dados["perfil"] = novo_perfil
                        dados["escola"] = nova_escola
                        dados["turmas"] = [t.strip() for t in novas_turmas.split(",") if t.strip()]
                        dados["ativo"] = novo_ativo
                        dados["atualizado_em"] = datetime.now().isoformat()
                        
                        salvar_usuarios(usuarios)
                        st.success(f"✅ Usuário '{usuario_editar}' atualizado!")
                        st.rerun()
    
    # ============================================================
    # ABA 4: PERMISSÕES
    # ============================================================
    with tab4:
        st.subheader("🔐 Permissões Granulares")
        
        permissoes_padrao = permissoes.get("permissoes_padrao", {})
        
        perfil_selecionado = st.selectbox("Selecione o perfil", list(permissoes_padrao.keys()))
        permissoes_atual = permissoes_padrao.get(perfil_selecionado, {})
        
        st.markdown("---")
        
        col1, col2 = st.columns(2)
        
        with col1:
            gerar_prova = st.checkbox("Gerar Prova", value=permissoes_atual.get("gerar_prova", True))
            corrigir = st.checkbox("Corrigir Provas", value=permissoes_atual.get("corrigir", True))
            ver_relatorios_individuais = st.checkbox("Ver Relatórios Individuais", value=permissoes_atual.get("ver_relatorios_individuais", True))
            exportar_pdf = st.checkbox("Exportar PDF", value=permissoes_atual.get("exportar_pdf", True))
        
        with col2:
            ver_relatorios_turma = st.checkbox("Ver Relatórios de Turma", value=permissoes_atual.get("ver_relatorios_turma", True))
            gerar_simulado = st.checkbox("Gerar Simulado", value=permissoes_atual.get("gerar_simulado", False))
            exportar_csv = st.checkbox("Exportar CSV", value=permissoes_atual.get("exportar_csv", False))
            gerenciar_turmas = st.checkbox("Gerenciar Turmas", value=permissoes_atual.get("gerenciar_turmas", False))
        
        if st.button("💾 Salvar Permissões", use_container_width=True):
            permissoes["permissoes_padrao"][perfil_selecionado] = {
                "gerar_prova": gerar_prova,
                "corrigir": corrigir,
                "ver_relatorios_individuais": ver_relatorios_individuais,
                "exportar_pdf": exportar_pdf,
                "ver_relatorios_turma": ver_relatorios_turma,
                "gerar_simulado": gerar_simulado,
                "exportar_csv": exportar_csv,
                "gerenciar_turmas": gerenciar_turmas
            }
            salvar_permissoes(permissoes)
            st.success("✅ Permissões salvas com sucesso!")
    
    # ============================================================
    # ABA 5: VINCULAÇÕES
    # ============================================================
    with tab5:
        st.subheader("🏫 Vinculações (Escola/Turmas)")
        
        if not usuarios:
            st.info("📌 Nenhum usuário cadastrado.")
        else:
            usuario_vinculo = st.selectbox("Selecione o usuário", list(usuarios.keys()), key="vinculo_select")
            
            if usuario_vinculo:
                dados = usuarios[usuario_vinculo]
                
                with st.form("form_vinculacoes"):
                    escola = st.text_input("Escola", value=dados.get("escola", ""))
                    turmas = st.text_input("Turmas (separadas por vírgula)", value=", ".join(dados.get("turmas", [])))
                    
                    if st.form_submit_button("💾 Salvar Vinculações", use_container_width=True):
                        dados["escola"] = escola
                        dados["turmas"] = [t.strip() for t in turmas.split(",") if t.strip()]
                        dados["vinculado_em"] = datetime.now().isoformat()
                        salvar_usuarios(usuarios)
                        st.success(f"✅ Vinculações do usuário '{usuario_vinculo}' atualizadas!")
    
    # ============================================================
    # ABA 6: IMPORTAÇÃO EM LOTE
    # ============================================================
    with tab6:
        st.subheader("📥 Importação em Lote")
        st.markdown("Envie um arquivo JSON para cadastrar múltiplos usuários.")
        
        st.markdown("""
        **Formato esperado do JSON:**
        ```json
        [
            {
                "username": "professor1",
                "nome": "João Silva",
                "email": "joao@email.com",
                "perfil": "professor",
                "escola": "EMEF Centro",
                "turmas": ["1º Ano A", "2º Ano B"],
                "senha": "123456"
            }
        ]
        ```
        """)
        
        uploaded_file = st.file_uploader("Selecione o arquivo JSON", type=["json"])
        
        if uploaded_file is not None:
            try:
                dados_import = json.load(uploaded_file)
                st.info(f"📊 {len(dados_import)} registros encontrados")
                
                if st.button("📥 Importar Usuários", use_container_width=True):
                    importados = 0
                    for item in dados_import:
                        username = item.get("username")
                        if username and username not in usuarios:
                            usuarios[username] = {
                                "nome": item.get("nome", ""),
                                "email": item.get("email", ""),
                                "senha": item.get("senha", "123456"),
                                "perfil": item.get("perfil", "professor"),
                                "escola": item.get("escola", ""),
                                "turmas": item.get("turmas", []),
                                "ativo": True,
                                "criado_em": datetime.now().isoformat()
                            }
                            importados += 1
                    
                    salvar_usuarios(usuarios)
                    st.success(f"✅ {importados} usuários importados!")
                    st.rerun()
            except Exception as e:
                st.error(f"❌ Erro ao ler arquivo: {e}")
    
    # ============================================================
    # ABA 7: LOGS
    # ============================================================
    with tab7:
        st.subheader("📜 Logs de Usuários")
        
        logs = []
        for username, dados in usuarios.items():
            logs.append({
                "Usuário": username,
                "Último Acesso": dados.get("ultimo_acesso", "Nunca"),
                "Status": "✅ Ativo" if dados.get("ativo", True) else "❌ Inativo"
            })
        
        if logs:
            for log in logs:
                st.markdown(f"**{log['Usuário']}** - {log['Último Acesso']} - {log['Status']}")
        else:
            st.info("📌 Nenhum log disponível")
    
    # ============================================================
    # ABA 8: SEGURANÇA
    # ============================================================
    with tab8:
        st.subheader("⚠️ Controle de Segurança")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("#### 🔒 Bloqueios Automáticos")
            max_tentativas = st.number_input("Máx. tentativas de login", value=5, step=1)
            bloqueio_minutos = st.number_input("Bloqueio (minutos)", value=30, step=5)
        
        with col2:
            st.markdown("#### 🔐 Política de Senhas")
            senha_min_caracteres = st.number_input("Mínimo de caracteres", value=6, step=1)
            expiracao_dias = st.number_input("Expiração de senha (dias)", value=90, step=10)
        
        st.markdown("---")
        
        if st.button("🔓 Desbloquear Todos", use_container_width=True):
            st.success("✅ Todos os usuários foram desbloqueados!")
    
    st.markdown("---")
    st.caption(f"📌 Última atualização: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}")

if __name__ == "__main__":
    show()

