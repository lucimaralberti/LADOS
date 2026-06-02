"""Classificador SAEB - Versão com curva logística (TRI simplificada)"""

import math
from typing import Dict, Any
from utils.enums import NivelProficiencia
from utils.logger import get_logger

logger = get_logger(__name__)

class ClassificadorSAEB:
    """
    Classificador de proficiência SAEB com curva logística
    Mais próximo da TRI real que sistemas educacionais usam
    """
    
    # Escalas SAEB oficiais (valores reais de proficiência)
    ESCALAS_REAIS = {
        "2EF": {
            "LP": {
                "Abaixo do Básico": (0, 124),
                "Básico": (125, 174),
                "Proficiente": (175, 224),
                "Avançado": (225, 300)
            },
            "MAT": {
                "Abaixo do Básico": (0, 149),
                "Básico": (150, 199),
                "Proficiente": (200, 249),
                "Avançado": (250, 300)
            }
        },
        "5EF": {
            "LP": {
                "Abaixo do Básico": (0, 149),
                "Básico": (150, 199),
                "Proficiente": (200, 249),
                "Avançado": (250, 300)
            },
            "MAT": {
                "Abaixo do Básico": (0, 174),
                "Básico": (175, 224),
                "Proficiente": (225, 274),
                "Avançado": (275, 350)
            }
        },
        "9EF": {
            "LP": {
                "Abaixo do Básico": (0, 199),
                "Básico": (200, 249),
                "Proficiente": (250, 299),
                "Avançado": (300, 350)
            },
            "MAT": {
                "Abaixo do Básico": (0, 224),
                "Básico": (225, 274),
                "Proficiente": (275, 324),
                "Avançado": (325, 400)
            }
        }
    }
    
    @classmethod
    def _curva_logistica(cls, percentual: float, ano: str) -> float:
        """
        Converte percentual em pontuação SAEB usando curva logística
        Fórmula: pontuacao = max_pontos / (1 + e^(-k*(percentual - ponto_medio)))
        """
        # Parâmetros ajustados por ano
        params = {
            "2EF": {"max": 300, "k": 0.08, "ponto_medio": 50},
            "5EF": {"max": 350, "k": 0.07, "ponto_medio": 55},
            "9EF": {"max": 400, "k": 0.06, "ponto_medio": 60}
        }
        p = params.get(ano, params["5EF"])
        
        # Curva logística
        try:
            pontuacao = p["max"] / (1 + math.exp(-p["k"] * (percentual - p["ponto_medio"])))
        except:
            pontuacao = percentual * (p["max"] / 100)
        
        return max(0, min(p["max"], pontuacao))
    
    @classmethod
    def percentual_para_proficiencia(cls, percentual: float, ano: str, disciplina: str = "LP") -> Dict[str, Any]:
        """Converte percentual para nível SAEB usando curva logística"""
        
        # Converter usando curva logística
        pontuacao = cls._curva_logistica(percentual, ano)
        
        # Obter escala real
        escala = cls.ESCALAS_REAIS.get(ano, cls.ESCALAS_REAIS["5EF"]).get(disciplina, cls.ESCALAS_REAIS["5EF"]["LP"])
        
        # Determinar nível
        for nivel, (min_val, max_val) in escala.items():
            if min_val <= pontuacao <= max_val:
                if nivel == "Avançado":
                    nivel_enum = NivelProficiencia.AVANCADO
                    descricao = "Desempenho excepcional. Domina completamente as habilidades esperadas."
                elif nivel == "Proficiente":
                    nivel_enum = NivelProficiencia.PROFICIENTE
                    descricao = "Desempenho adequado. Desenvolveu as habilidades esperadas."
                elif nivel == "Básico":
                    nivel_enum = NivelProficiencia.BASICO
                    descricao = "Desempenho em desenvolvimento. Necessita de reforço."
                else:
                    nivel_enum = NivelProficiencia.ABAIXO_BASICO
                    descricao = "Desempenho insuficiente. Necessita de intervenção imediata."
                
                return {
                    "nivel": nivel_enum.value,
                    "nivel_enum": nivel_enum,
                    "pontuacao_saeb": round(pontuacao, 1),
                    "percentual_original": percentual,
                    "descricao": descricao,
                    "ano": ano,
                    "disciplina": disciplina,
                    "faixa": f"{min_val}-{max_val}",
                    "metodo": "curva_logistica"
                }
        
        return {
            "nivel": "Indeterminado",
            "pontuacao_saeb": round(pontuacao, 1),
            "percentual_original": percentual,
            "descricao": "Dados insuficientes para classificação",
            "ano": ano,
            "disciplina": disciplina
        }
    
    @classmethod
    def proficiencia_para_cor(cls, nivel: str) -> str:
        cores = {
            "Avançado": "#3B82F6",
            "Proficiente": "#10B981",
            "Básico": "#F59E0B",
            "Abaixo do Básico": "#EF4444"
        }
        return cores.get(nivel, "#6B7280")
