"""
Sistema de Registro de Atividades - LADOS 2.0
"""

import json
import os
from datetime import datetime
from typing import Dict, List, Optional

# Arquivo para armazenar atividades
ATIVIDADES_FILE = "data/atividades.json"

# Tipos de atividades
class TipoAtividade:
    LOGIN = "login"
    LOGOUT = "logout"
    GERAR_PROVA = "gerar_prova"
    CORRIGIR_PROVA = "corrigir_prova"
    DOWNLOAD_RELATORIO = "download_relatorio"
    DOWNLOAD_PROVA = "download_prova"
    ACESSO_SISTEMA = "acesso_sistema"

def inicializar_arquivo_atividades():
    """Cria arquivo de atividades se não existir"""
    os.makedirs(os.path.dirname(ATIVIDADES_FILE), exist_ok=True)
    
    if not os.path.exists(ATIVIDADES_FILE):
        with open(ATIVIDADES_FILE, 'w', encoding='utf-8') as f:
            json.dump([], f)

def registrar_atividade(username: str, tipo: str, detalhes: Dict = None):
    """Registra uma atividade do usuário"""
    inicializar_arquivo_atividades()
    
    # Carregar atividades existentes (usando utf-8-sig)
    with open(ATIVIDADES_FILE, 'r', encoding='utf-8-sig') as f:
        atividades = json.load(f)
    
    # Criar nova atividade
    nova_atividade = {
        "username": username,
        "tipo": tipo,
        "timestamp": datetime.now().isoformat(),
        "data": datetime.now().strftime("%d/%m/%Y"),
        "hora": datetime.now().strftime("%H:%M:%S"),
        "detalhes": detalhes or {}
    }
    
    # Adicionar e salvar (manter últimas 1000 atividades)
    atividades.insert(0, nova_atividade)
    atividades = atividades[:1000]  # Limitar histórico
    
    with open(ATIVIDADES_FILE, 'w', encoding='utf-8') as f:
        json.dump(atividades, f, ensure_ascii=False, indent=2)

def get_atividades_usuario(username: str, limite: int = 20) -> List[Dict]:
    """Retorna atividades de um usuário específico"""
    inicializar_arquivo_atividades()
    
    with open(ATIVIDADES_FILE, 'r', encoding='utf-8-sig') as f:
        todas_atividades = json.load(f)
    
    atividades_usuario = [a for a in todas_atividades if a["username"] == username]
    return atividades_usuario[:limite]

def get_ultimas_atividades(limite: int = 10) -> List[Dict]:
    """Retorna as últimas atividades de todos os usuários"""
    inicializar_arquivo_atividades()
    
    with open(ATIVIDADES_FILE, 'r', encoding='utf-8-sig') as f:
        atividades = json.load(f)
    
    return atividades[:limite]

def get_atividades_por_tipo(tipo: str, limite: int = 50) -> List[Dict]:
    """Retorna atividades filtradas por tipo"""
    inicializar_arquivo_atividades()
    
    with open(ATIVIDADES_FILE, 'r', encoding='utf-8-sig') as f:
        todas_atividades = json.load(f)
    
    filtradas = [a for a in todas_atividades if a["tipo"] == tipo]
    return filtradas[:limite]

# Labels para exibição
LABELS_ATIVIDADES = {
    TipoAtividade.LOGIN: "🔐 Login no sistema",
    TipoAtividade.LOGOUT: "🚪 Logout do sistema",
    TipoAtividade.GERAR_PROVA: "📝 Gerou uma prova",
    TipoAtividade.CORRIGIR_PROVA: "✏️ Corrigiu uma prova",
    TipoAtividade.DOWNLOAD_RELATORIO: "📊 Baixou um relatório",
    TipoAtividade.DOWNLOAD_PROVA: "📥 Baixou uma prova",
    TipoAtividade.ACESSO_SISTEMA: "💻 Acessou o sistema"
}

def formatar_atividade(atividade: Dict) -> str:
    """Formata uma atividade para exibição"""
    tipo = atividade["tipo"]
    label = LABELS_ATIVIDADES.get(tipo, tipo)
    
    detalhes = atividade.get("detalhes", {})
    info_extra = ""
    
    if tipo == TipoAtividade.GERAR_PROVA and detalhes:
        info_extra = f" - {detalhes.get('qtd_questoes', 'N/A')} questões, {detalhes.get('disciplinas', 'N/A')}"
    elif tipo == TipoAtividade.DOWNLOAD_PROVA and detalhes:
        info_extra = f" - {detalhes.get('arquivo', 'prova.zip')}"
    elif tipo == TipoAtividade.DOWNLOAD_RELATORIO and detalhes:
        info_extra = f" - {detalhes.get('tipo_relatorio', 'Relatório')}"
    
    return f"{label}{info_extra} - {atividade['data']} às {atividade['hora']}"
