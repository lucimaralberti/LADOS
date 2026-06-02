"""
Configurações Globais do LADOS
Caminhos, paths, constantes e configurações do sistema
"""

import os

# ====================== CONFIGURAÇÃO DO PDFKIT ======================
path_wkhtmltopdf = r'C:\Program Files\wkhtmltopdf\bin\wkhtmltopdf.exe'
if not os.path.exists(path_wkhtmltopdf):
    path_wkhtmltopdf = r'C:\Program Files (x86)\wkhtmltopdf\bin\wkhtmltopdf.exe'

WKHTMLTOPDF_CONFIG = path_wkhtmltopdf if os.path.exists(path_wkhtmltopdf) else None

# ====================== CAMINHOS DO SISTEMA ======================
DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data")
RESULTADOS_DIR = os.path.join(DATA_DIR, "resultados")
QUESTIONS_FILE = os.path.join(DATA_DIR, "questoes.json")
ITEMS_FILE = os.path.join(DATA_DIR, "itens.json")
CORRECOES_FILE = os.path.join(RESULTADOS_DIR, "correcoes.json")

# ====================== CONFIGURAÇÕES DE OCR ======================
OCR_IMAGE_WIDTH = 1200
OCR_IMAGE_HEIGHT = 1600
OCR_MIN_RADIUS = 10
OCR_MAX_RADIUS = 25
OCR_FILLED_THRESHOLD = 120

# ====================== CONFIGURAÇÕES DE DESEMPENHO ======================
NIVEIS_CONCEITO = {
    "MB": {"min": 90, "nome": "Muito Bom"},
    "B": {"min": 70, "nome": "Bom"},
    "S": {"min": 50, "nome": "Satisfatório"},
    "I": {"min": 0, "nome": "Insatisfatório"}
}

NIVEIS_PROFICIENCIA = {
    "Avançado": {"min": 90, "cor": "#10B981"},
    "Proficiente": {"min": 70, "cor": "#3B82F6"},
    "Básico": {"min": 50, "cor": "#F59E0B"},
    "Inicial": {"min": 30, "cor": "#F97316"},
    "Crítico": {"min": 0, "cor": "#EF4444"}
}

def calcular_conceito(percentual: float) -> str:
    """Calcula o conceito (MB, B, S, I) baseado no percentual"""
    for conceito, dados in NIVEIS_CONCEITO.items():
        if percentual >= dados["min"]:
            return conceito
    return "I"

def calcular_nivel_proficiencia(percentual: float) -> str:
    """Calcula o nível de proficiência baseado no percentual"""
    for nivel, dados in NIVEIS_PROFICIENCIA.items():
        if percentual >= dados["min"]:
            return nivel
    return "Crítico"
