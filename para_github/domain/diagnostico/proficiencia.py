"""Proficiencia - Classifica niveis baseados na escala SAEB"""

from typing import Dict, Any
from utils.enums import AnoEscolar


class Proficiencia:
    TABELA_SAEB: Dict[str, list] = {
        "2EF": [
            {"nivel": "Abaixo do Basico", "min": 0, "max": 49, "cor": "#EF4444"},
            {"nivel": "Basico", "min": 50, "max": 69, "cor": "#F59E0B"},
            {"nivel": "Proficiente", "min": 70, "max": 89, "cor": "#10B981"},
            {"nivel": "Avancado", "min": 90, "max": 100, "cor": "#3B82F6"}
        ],
        "5EF": [
            {"nivel": "Abaixo do Basico", "min": 0, "max": 49, "cor": "#EF4444"},
            {"nivel": "Basico", "min": 50, "max": 69, "cor": "#F59E0B"},
            {"nivel": "Proficiente", "min": 70, "max": 89, "cor": "#10B981"},
            {"nivel": "Avancado", "min": 90, "max": 100, "cor": "#3B82F6"}
        ],
        "9EF": [
            {"nivel": "Abaixo do Basico", "min": 0, "max": 49, "cor": "#EF4444"},
            {"nivel": "Basico", "min": 50, "max": 69, "cor": "#F59E0B"},
            {"nivel": "Proficiente", "min": 70, "max": 89, "cor": "#10B981"},
            {"nivel": "Avancado", "min": 90, "max": 100, "cor": "#3B82F6"}
        ]
    }
    
    @classmethod
    def classificar(cls, percentual: float, ano: AnoEscolar) -> Dict[str, Any]:
        escala = ano.para_chave_saeb()
        tabela = cls.TABELA_SAEB.get(escala, cls.TABELA_SAEB["5EF"])
        
        for nivel in tabela:
            if nivel["min"] <= percentual <= nivel["max"]:
                return {
                    "nivel": nivel["nivel"],
                    "percentual": percentual,
                    "escala_usada": escala,
                    "cor": nivel["cor"]
                }
        
        return {
            "nivel": "Indeterminado",
            "percentual": percentual,
            "escala_usada": escala,
            "cor": "#6B7280"
        }
