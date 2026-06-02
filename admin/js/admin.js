/* ============================================
   ADMIN PANEL - SISTEMA DE DIAGNÓSTICO
   ============================================ */

const MOCK_DATA = {
    usuarios: { total: 145, professores: 12, alunos: 128, admins: 5 },
    questoes: { total: 548, lp: 274, mat: 274, ativas: 535 },
    escolas: { total: 12, ativas: 10 },
    turmas: { total: 48 },
    provas: { total: 234, aplicadas: 189, corrigidas: 156 },
    correcoes: { total: 2340, thisMonth: 187 },
    status: { score: 94.5, nivel: "saudavel" },
    
    distribuicao: {
        lp: { facil: 120, medio: 100, dificil: 54 },
        mat: { facil: 80, medio: 90, dificil: 50 }
    },
    
    alertas: [
        { id: 1, nivel: "medium", titulo: "Questão com multiplicação no 1º ano", descricao: "Q_1EF01_M_030 utiliza multiplicação (3x6) no 1º ano", acao: "Resolver" },
        { id: 2, nivel: "low", titulo: "Metadados incompletos", descricao: "5 questões sem contexto definido", acao: "Revisar" },
        { id: 3, nivel: "low", titulo: "Questões sem temas transversais", descricao: "12 questões não possuem temas associados", acao: "Classificar" }
    ],
    
    problematicas: [
        { id: "Q_1EF01_M_030", problema: "Multiplicação no 1º ano", gravidade: "media" },
        { id: "Q_1EF02_P_016", problema: "Letras maiúsculas inconsistentes", gravidade: "baixa" }
    ],
    
    modulos: [
        { id: "gerador_provas", nome: "Gerador de Provas", status: "active", descricao: "Gera provas automaticamente a partir do banco de questões" },
        { id: "analise_estatistica", nome: "Análise Estatística", status: "active", descricao: "Calcula métricas de desempenho e TRI" },
        { id: "exportador", nome: "Exportador de Dados", status: "inactive", descricao: "Exporta relatórios em múltiplos formatos" }
    ],
    
    usuariosLista: [
        { id: 1, nome: "Ana Silva", email: "ana@escola.com", perfil: "professor", status: "ativo" },
        { id: 2, nome: "Carlos Santos", email: "carlos@escola.com", perfil: "aluno", status: "ativo" },
        { id: 3, nome: "admin@admin.com", email: "admin@sistema.com", perfil: "admin", status: "ativo" }
    ],
    
    logs: [
        { data: "2026-05-09 10:30:00", tipo: "info", mensagem: "Correção automática aplicada em Q_1EF08_M_024" },
        { data: "2026-05-09 08:15:00", tipo: "success", mensagem: "Backup automático concluído" },
        { data: "2026-05-08 14:20:00", tipo: "warning", mensagem: "Alerta: Questão Q_1EF01_M_030 com multiplicação" }
    ]
};

let currentPage = "inicio";

document.addEventListener("DOMContentLoaded", () => {
    initializeNavigation();
    loadPage("inicio");
});

function initializeNavigation() {
    const navItems = document.querySelectorAll(".nav-item");
    navItems.forEach(item => {
        item.addEventListener("click", (e) => {
            e.preventDefault();
            const page = item.dataset.page;
            if (page) {
                setActiveNavItem(item);
                loadPage(page);
            }
        });
    });
}

function setActiveNavItem(activeItem) {
    document.querySelectorAll(".nav-item").forEach(item => {
        item.classList.remove("active");
    });
    activeItem.classList.add("active");
}

function loadPage(page) {
    currentPage = page;
    switch(page) {
        case "inicio": renderDashboard(); break;
        case "auditoria": renderAuditoria(); break;
        case "saude": renderSaude(); break;
        case "configuracoes": renderConfiguracoes(); break;
        default: renderDashboard();
    }
}

function renderDashboard() {
    const html = `
        <div class="top-bar">
            <h1 class="page-title">📊 INÍCIO</h1>
            <div class="date-time">${new Date().toLocaleString("pt-BR")}</div>
        </div>
        
        <div class="stats-grid">
            <div class="stat-card">
                <div class="stat-icon">👥</div>
                <div class="stat-value">${MOCK_DATA.usuarios.total}</div>
                <div class="stat-label">Usuários cadastrados</div>
                <small>👨‍🏫 ${MOCK_DATA.usuarios.professores} profs | 👨‍🎓 ${MOCK_DATA.usuarios.alunos} alunos</small>
            </div>
            <div class="stat-card">
                <div class="stat-icon">📋</div>
                <div class="stat-value">${MOCK_DATA.questoes.total}</div>
                <div class="stat-label">Questões</div>
                <small>📖 LP: ${MOCK_DATA.questoes.lp} | 🔢 MAT: ${MOCK_DATA.questoes.mat}</small>
            </div>
            <div class="stat-card">
                <div class="stat-icon">🏫</div>
                <div class="stat-value">${MOCK_DATA.escolas.total}</div>
                <div class="stat-label">Escolas</div>
                <small>📚 ${MOCK_DATA.turmas.total} turmas ativas</small>
            </div>
            <div class="stat-card">
                <div class="stat-icon">📝</div>
                <div class="stat-value">${MOCK_DATA.correcoes.total}</div>
                <div class="stat-label">Correções realizadas</div>
                <small>📈 +${MOCK_DATA.correcoes.thisMonth} neste mês</small>
            </div>
            <div class="stat-card">
                <div class="stat-icon">✅</div>
                <div class="stat-value">${MOCK_DATA.status.score}%</div>
                <div class="stat-label">Status geral</div>
                <small><span class="status-indicator status-ok"></span> Sistema Saudável</small>
            </div>
        </div>
        
        <div class="charts-row">
            <div class="chart-card">
                <div class="chart-title">📊 Distribuição por Dificuldade - LP</div>
                <div class="bar-chart">
                    <div class="bar-item">
                        <div class="bar-label">Fácil</div>
                        <div class="bar-fill"><div class="bar-progress" style="width: ${(MOCK_DATA.distribuicao.lp.facil / 274 * 100)}%">${MOCK_DATA.distribuicao.lp.facil}</div></div>
                    </div>
                    <div class="bar-item">
                        <div class="bar-label">Médio</div>
                        <div class="bar-fill"><div class="bar-progress" style="width: ${(MOCK_DATA.distribuicao.lp.medio / 274 * 100)}%">${MOCK_DATA.distribuicao.lp.medio}</div></div>
                    </div>
                    <div class="bar-item">
                        <div class="bar-label">Difícil</div>
                        <div class="bar-fill"><div class="bar-progress" style="width: ${(MOCK_DATA.distribuicao.lp.dificil / 274 * 100)}%">${MOCK_DATA.distribuicao.lp.dificil}</div></div>
                    </div>
                </div>
            </div>
            <div class="chart-card">
                <div class="chart-title">📊 Distribuição por Dificuldade - MAT</div>
                <div class="bar-chart">
                    <div class="bar-item">
                        <div class="bar-label">Fácil</div>
                        <div class="bar-fill"><div class="bar-progress" style="width: ${(MOCK_DATA.distribuicao.mat.facil / 220 * 100)}%">${MOCK_DATA.distribuicao.mat.facil}</div></div>
                    </div>
                    <div class="bar-item">
                        <div class="bar-label">Médio</div>
                        <div class="bar-fill"><div class="bar-progress" style="width: ${(MOCK_DATA.distribuicao.mat.medio / 220 * 100)}%">${MOCK_DATA.distribuicao.mat.medio}</div></div>
                    </div>
                    <div class="bar-item">
                        <div class="bar-label">Difícil</div>
                        <div class="bar-fill"><div class="bar-progress" style="width: ${(MOCK_DATA.distribuicao.mat.dificil / 220 * 100)}%">${MOCK_DATA.distribuicao.mat.dificil}</div></div>
                    </div>
                </div>
            </div>
        </div>
        
        <div class="chart-card">
            <div class="chart-title">⚠️ Alertas do Sistema</div>
            <div class="alert-list">
                ${MOCK_DATA.alertas.map(alerta => `
                    <div class="alert-item alert-${alerta.nivel}">
                        <div class="alert-icon">${alerta.nivel === "critical" ? "🔴" : alerta.nivel === "medium" ? "🟡" : "🔵"}</div>
                        <div class="alert-content">
                            <div class="alert-title">${alerta.titulo}</div>
                            <div class="alert-description">${alerta.descricao}</div>
                        </div>
                        <button class="alert-btn" onclick="resolverAlerta(${alerta.id})">${alerta.acao}</button>
                    </div>
                `).join("")}
            </div>
        </div>
        
        <div class="chart-card mt-20">
            <div class="chart-title">📋 Últimas Atividades</div>
            <table class="data-table">
                <thead><tr><th>Data/Hora</th><th>Tipo</th><th>Mensagem</th></tr></thead>
                <tbody>
                    ${MOCK_DATA.logs.slice(0,5).map(log => `
                        <tr>
                            <td>${log.data}</td>
                            <td><span class="status-${log.tipo}">●</span> ${log.tipo}</td>
                            <td>${log.mensagem}</td>
                        </tr>
                    `).join("")}
                </tbody>
            </table>
        </div>
    `;
    document.querySelector(".main-content").innerHTML = html;
}

function renderAuditoria() {
    const html = `
        <div class="top-bar">
            <h1 class="page-title">🔍 AUDITORIA</h1>
            <div class="date-time">${new Date().toLocaleString("pt-BR")}</div>
        </div>
        
        <div class="stats-grid">
            <div class="stat-card">
                <div class="stat-icon">✅</div>
                <div class="stat-value">98.5%</div>
                <div class="stat-label">Integridade do Banco</div>
            </div>
            <div class="stat-card">
                <div class="stat-icon">⚠️</div>
                <div class="stat-value">7</div>
                <div class="stat-label">Anomalias Detectadas</div>
            </div>
            <div class="stat-card">
                <div class="stat-icon">📊</div>
                <div class="stat-value">5</div>
                <div class="stat-label">Lacunas Curriculares</div>
            </div>
            <div class="stat-card">
                <div class="stat-icon">📝</div>
                <div class="stat-value">156</div>
                <div class="stat-label">Alterações Registradas</div>
            </div>
        </div>
        
        <div class="chart-card">
            <div class="chart-title">📋 Questões Problemáticas</div>
            <table class="data-table">
                <thead><tr><th>ID da Questão</th><th>Problema Identificado</th><th>Gravidade</th><th>Ação</th></tr></thead>
                <tbody>
                    ${MOCK_DATA.problematicas.map(q => `
                        <tr>
                            <td><code>${q.id}</code></td>
                            <td>${q.problema}</td>
                            <td><span class="status-${q.gravidade === "media" ? "warning" : "ok"}">●</span> ${q.gravidade}</td>
                            <td><button class="btn btn-sm btn-primary" onclick="detalharQuestao('${q.id}')">Detalhar</button></td>
                        </tr>
                    `).join("")}
                </tbody>
            </table>
        </div>
        
        <div class="chart-card mt-20">
            <div class="chart-title">📊 Cobertura por Descritor</div>
            <div class="bar-chart">
                <div class="bar-item">
                    <div class="bar-label">2EF07_P</div>
                    <div class="bar-fill"><div class="bar-progress" style="width: 100%">5/5</div></div>
                </div>
                <div class="bar-item">
                    <div class="bar-label">1EF01_P</div>
                    <div class="bar-fill"><div class="bar-progress" style="width: 85%">22/26</div></div>
                </div>
                <div class="bar-item">
                    <div class="bar-label">1EF05_M</div>
                    <div class="bar-fill"><div class="bar-progress" style="width: 70%">21/30</div></div>
                </div>
            </div>
        </div>
    `;
    document.querySelector(".main-content").innerHTML = html;
}

function renderSaude() {
    const html = `
        <div class="top-bar">
            <h1 class="page-title">🏥 SAÚDE DO SISTEMA</h1>
            <div class="date-time">Último diagnóstico: ${new Date().toLocaleString("pt-BR")}</div>
        </div>
        
        <div class="stats-grid">
            <div class="stat-card" onclick="executarDiagnostico()" style="cursor: pointer;">
                <div class="stat-icon">🔍</div>
                <div class="stat-value">Executar</div>
                <div class="stat-label">Diagnóstico Completo</div>
                <small>Clique para verificar o sistema</small>
            </div>
            <div class="stat-card" onclick="aplicarCorrecoes()" style="cursor: pointer;">
                <div class="stat-icon">⚡</div>
                <div class="stat-value">Auto-Correção</div>
                <div class="stat-label">Corrigir problemas</div>
                <small>Correções automáticas seguras</small>
            </div>
            <div class="stat-card" onclick="criarBackup()" style="cursor: pointer;">
                <div class="stat-icon">💾</div>
                <div class="stat-value">Backup</div>
                <div class="stat-label">Criar Snapshot</div>
                <small>Último: ${MOCK_DATA.logs[0].data}</small>
            </div>
            <div class="stat-card" onclick="gerarRelatorioSaude()" style="cursor: pointer;">
                <div class="stat-icon">📋</div>
                <div class="stat-value">Relatório</div>
                <div class="stat-label">Exportar Saúde</div>
                <small>PDF / JSON / CSV</small>
            </div>
        </div>
        
        <div class="charts-row">
            <div class="chart-card">
                <div class="chart-title">🩺 Score de Saúde por Módulo</div>
                <div class="bar-chart">
                    <div class="bar-item"><div class="bar-label">Banco de Questões</div><div class="bar-fill"><div class="bar-progress" style="width: 94%">94%</div></div></div>
                    <div class="bar-item"><div class="bar-label">API/Servidor</div><div class="bar-fill"><div class="bar-progress" style="width: 99%">99%</div></div></div>
                    <div class="bar-item"><div class="bar-label">Interface</div><div class="bar-fill"><div class="bar-progress" style="width: 96%">96%</div></div></div>
                    <div class="bar-item"><div class="bar-label">Persistência</div><div class="bar-fill"><div class="bar-progress" style="width: 100%">100%</div></div></div>
                </div>
            </div>
            <div class="chart-card">
                <div class="chart-title">📈 Métricas de Performance</div>
                <div class="bar-chart">
                    <div class="bar-item"><div class="bar-label">Tempo resposta</div><div class="bar-fill"><div class="bar-progress" style="width: 95%">~120ms</div></div></div>
                    <div class="bar-item"><div class="bar-label">Uso CPU</div><div class="bar-fill"><div class="bar-progress" style="width: 28%">28%</div></div></div>
                    <div class="bar-item"><div class="bar-label">Uso Memória</div><div class="bar-fill"><div class="bar-progress" style="width: 42%">42%</div></div></div>
                </div>
            </div>
        </div>
        
        <div class="chart-card">
            <div class="chart-title">🔍 Diagnóstico Detalhado</div>
            <div class="alert-list">
                ${MOCK_DATA.alertas.map(alerta => `
                    <div class="alert-item alert-${alerta.nivel}">
                        <div class="alert-icon">${alerta.nivel === "critical" ? "🔴" : alerta.nivel === "medium" ? "🟡" : "🔵"}</div>
                        <div class="alert-content">
                            <div class="alert-title">${alerta.titulo}</div>
                            <div class="alert-description">${alerta.descricao}</div>
                        </div>
                        <button class="alert-btn" onclick="resolverAlerta(${alerta.id})">${alerta.acao}</button>
                    </div>
                `).join("")}
            </div>
        </div>
        
        <div class="chart-card mt-20">
            <div class="chart-title">🔄 Versionamento e Backups</div>
            <table class="data-table">
                <thead><tr><th>Versão</th><th>Data</th><th>Descrição</th><th>Ações</th></tr></thead>
                <tbody>
                    <tr><td>v2.1.0</td><td>2026-05-09</td><td>Correção de gabaritos</td><td><button class="btn btn-sm btn-primary" onclick="restaurarVersao("2.1.0")">Restaurar</button></td></tr>
                    <tr><td>v2.0.0</td><td>2026-05-01</td><td>Adição de 100 questões</td><td><button class="btn btn-sm btn-primary" onclick="restaurarVersao("2.0.0")">Restaurar</button></td></tr>
                    <tr><td>v1.9.0</td><td>2026-04-15</td><td>Correção de metadados</td><td><button class="btn btn-sm btn-primary" onclick="restaurarVersao("1.9.0")">Restaurar</button></td></tr>
                </tbody>
            </table>
        </div>
    `;
    document.querySelector(".main-content").innerHTML = html;
}

function renderConfiguracoes() {
    const html = `
        <div class="top-bar">
            <h1 class="page-title">⚙️ CONFIGURAÇÕES</h1>
            <div class="date-time">${new Date().toLocaleString("pt-BR")}</div>
        </div>
        
        <div style="display: flex; gap: 10px; margin-bottom: 20px; border-bottom: 2px solid var(--light);">
            <button class="btn" onclick="showConfigTab("modulos")" id="tab-modulos" style="background: var(--secondary); color: white;">🧩 Módulos</button>
            <button class="btn" onclick="showConfigTab("questoes")" id="tab-questoes">📋 Questões</button>
            <button class="btn" onclick="showConfigTab("usuarios")" id="tab-usuarios">👤 Usuários</button>
            <button class="btn" onclick="showConfigTab("sistema")" id="tab-sistema">⚙️ Sistema</button>
        </div>
        
        <div id="modulos-tab" class="config-tab active">
            <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 20px;">
                <h3>🧩 Módulos do Sistema</h3>
                <button class="btn btn-success" onclick="abrirModalCriarModulo()">+ Criar Novo Módulo</button>
            </div>
            <div class="modules-grid">
                ${MOCK_DATA.modulos.map(modulo => `
                    <div class="module-card">
                        <div class="module-header">
                            <span class="module-name">${modulo.nome}</span>
                            <span class="module-status ${modulo.status}">${modulo.status === "active" ? "Ativo" : "Inativo"}</span>
                        </div>
                        <div class="module-description">${modulo.descricao}</div>
                        <div class="module-actions">
                            <button class="btn btn-sm btn-primary" onclick="editarModulo("${modulo.id}")">✏️ Editar</button>
                            ${modulo.status === "active" ? "<button class=\"btn btn-sm btn-warning\" onclick=\"alternarModulo(\"" + modulo.id + "\", \"inactive\")\">⏸️ Desativar</button>" : "<button class=\"btn btn-sm btn-success\" onclick=\"alternarModulo(\"" + modulo.id + "\", \"active\")\">▶️ Ativar</button>"}
                        </div>
                    </div>
                `).join("")}
            </div>
        </div>
        
        <div id="questoes-tab" class="config-tab" style="display: none;">
            <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 20px;">
                <h3>📋 Cadastro de Questões</h3>
                <button class="btn btn-success" onclick="abrirModalNovaQuestao()">+ Nova Questão</button>
            </div>
            
            <div class="chart-card">
                <div class="chart-title">✏️ Nova Questão (Formulário Rápido)</div>
                <form id="form-nova-questao" onsubmit="event.preventDefault(); salvarNovaQuestao();">
                    <div class="form-group">
                        <label>ID da Questão</label>
                        <input type="text" class="form-control" id="questao-id" placeholder="Ex: Q_3EF01_P_006">
                    </div>
                    <div class="form-group">
                        <label>Enunciado</label>
                        <textarea class="form-control" id="questao-enunciado" rows="3" placeholder="Digite o enunciado da questão..."></textarea>
                    </div>
                    <div class="form-group">
                        <label>Ano / Disciplina</label>
                        <select class="form-control" id="questao-ano">
                            <option value="1EF">1º Ano EF</option>
                            <option value="2EF">2º Ano EF</option>
                        </select>
                        <select class="form-control" id="questao-disciplina" style="margin-top: 5px;">
                            <option value="LP">Língua Portuguesa</option>
                            <option value="MAT">Matemática</option>
                        </select>
                    </div>
                    <button type="submit" class="btn btn-primary">Salvar Questão</button>
                </form>
            </div>
            
            <div class="chart-card mt-20">
                <div class="chart-title">📤 Importação em Lote</div>
                <div class="form-group">
                    <label>Arquivo JSON/CSV</label>
                    <input type="file" class="form-control" id="import-file" accept=".json,.csv">
                </div>
                <button class="btn btn-primary" onclick="importarQuestoes()">Importar Questões</button>
                <span style="margin-left: 10px; color: var(--gray);">Ou <a href="#" onclick="exportarTemplate()">baixar modelo</a></span>
            </div>
        </div>
        
        <div id="usuarios-tab" class="config-tab" style="display: none;">
            <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 20px;">
                <h3>👤 Gestão de Usuários</h3>
                <button class="btn btn-success" onclick="abrirModalNovoUsuario()">+ Novo Usuário</button>
            </div>
            <table class="data-table">
                <thead><tr><th>ID</th><th>Nome</th><th>Email</th><th>Perfil</th><th>Status</th><th>Ações</th></tr></thead>
                <tbody>
                    ${MOCK_DATA.usuariosLista.map(user => `
                        <tr>
                            <td>${user.id}</td>
                            <td>${user.nome}</td>
                            <td>${user.email}</td>
                            <td>${user.perfil === "admin" ? "👑 Administrador" : user.perfil === "professor" ? "👨‍🏫 Professor" : "👨‍🎓 Aluno"}</td>
                            <td><span class="status-ok">●</span> ${user.status}</td>
                            <td><button class="btn btn-sm btn-primary" onclick="editarUsuario(${user.id})">✏️</button>
                                <button class="btn btn-sm btn-danger" onclick="suspenderUsuario(${user.id})">⛔</button>
                            </td>
                        </tr>
                    `).join("")}
                </tbody>
            </table>
        </div>
        
        <div id="sistema-tab" class="config-tab" style="display: none;">
            <div class="chart-card">
                <div class="chart-title">⚙️ Parâmetros Gerais</div>
                <form id="form-sistema" onsubmit="event.preventDefault(); salvarConfiguracoes();">
                    <div class="form-group">
                        <label>Nome do Sistema</label>
                        <input type="text" class="form-control" id="sistema-nome" value="Sistema de Questões - LADOS 2.0">
                    </div>
                    <div class="form-group">
                        <label>Backup Automático</label>
                        <select class="form-control" id="sistema-backup">
                            <option>Diário - 03:00</option>
                            <option>Semanal - Domingo</option>
                            <option>Desabilitado</option>
                        </select>
                    </div>
                    <div class="form-group">
                        <label>Tema</label>
                        <select class="form-control" id="sistema-tema">
                            <option>Claro (Padrão)</option>
                            <option>Escuro</option>
                        </select>
                    </div>
                    <button type="submit" class="btn btn-primary">Salvar Configurações</button>
                </form>
            </div>
            
            <div class="chart-card mt-20">
                <div class="chart-title">📋 Logs do Sistema</div>
                <div style="max-height: 300px; overflow-y: auto;">
                    <table class="data-table">
                        <thead><tr><th>Data/Hora</th><th>Nível</th><th>Mensagem</th></tr></thead>
                        <tbody>
                            ${MOCK_DATA.logs.map(log => `
                                </table>
                                    <td>${log.data}</td>
                                    <td><span class="status-${log.tipo}">●</span> ${log.tipo}</td>
                                    <td>${log.mensagem}</td>
                                </tr>
                            `).join("")}
                        </tbody>
                    </table>
                </div>
            </div>
        </div>
    `;
    document.querySelector(".main-content").innerHTML = html;
}

function showConfigTab(tab) {
    const tabs = ["modulos", "questoes", "usuarios", "sistema"];
    tabs.forEach(t => {
        const el = document.getElementById(`${t}-tab`);
        const btn = document.getElementById(`tab-${t}`);
        if (el) el.style.display = t === tab ? "block" : "none";
        if (btn) {
            btn.style.background = t === tab ? "var(--secondary)" : "var(--light)";
            btn.style.color = t === tab ? "white" : "var(--dark)";
        }
    });
}

function resolverAlerta(id) { alert(`Resolver alerta ${id} (implementar lógica)`); }
function detalharQuestao(id) { alert(`Detalhar questão ${id}`); }
function executarDiagnostico() { alert("Executando diagnóstico completo... (implementar lógica)"); }
function aplicarCorrecoes() { alert("Aplicando correções automáticas... (implementar lógica)"); }
function criarBackup() { alert("Criando backup... (implementar lógica)"); }
function gerarRelatorioSaude() { alert("Gerando relatório de saúde... (implementar lógica)"); }
function abrirModalCriarModulo() { alert("Abrir modal para criar novo módulo (inserir código)"); }
function editarModulo(id) { alert(`Editar módulo ${id}`); }
function alternarModulo(id, status) { alert(`Alternar módulo ${id} para ${status}`); }
function abrirModalNovaQuestao() { alert("Abrir formulário de nova questão"); }
function salvarNovaQuestao() { alert("Salvar nova questão (implementar lógica)"); }
function abrirModalNovoUsuario() { alert("Abrir formulário de novo usuário"); }
function importarQuestoes() { alert("Importar questões do arquivo selecionado"); }
function exportarTemplate() { alert("Exportar template para download"); }
function editarUsuario(id) { alert(`Editar usuário ${id}`); }
function suspenderUsuario(id) { alert(`Suspender usuário ${id}`); }
function salvarConfiguracoes() { alert("Salvar configurações do sistema"); }
function restaurarVersao(versao) { alert(`Restaurar versão ${versao}`); }

window.showConfigTab = showConfigTab;
