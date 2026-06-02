# -*- coding: utf-8 -*-
"""
Funções centrais de normalização para o LADOS
Evita repetição de lógica de remoção de acentos
"""

import unicodedata

def normalizar_texto(texto: str) -> str:
    """
    Normaliza texto: minúsculo, sem acentos, espaços viram underscore
    
    Exemplos:
        normalizar_texto("Múltipla Escolha") -> "multipla_escolha"
        normalizar_texto("Ciências") -> "ciencias"
        normalizar_texto("História") -> "historia"
    """
    if not texto:
        return ""
    
    texto = texto.lower().strip()
    
    # Remove acentos (unicode NFD)
    texto = unicodedata.normalize("NFD", texto)
    texto = texto.encode("ascii", "ignore").decode("utf-8")
    
    # Substitui espaços por underscore
    texto = texto.replace(" ", "_")
    
    return texto

def normalizar_disciplina(disciplina: str) -> str:
    """Normaliza nome de disciplina para sigla"""
    if not disciplina:
        return ""
    
    d = normalizar_texto(disciplina)
    
    mapeamento = {
        "lingua_portuguesa": "LP",
        "portugues": "LP",
        "matematica": "MAT",
        "ciencias": "CI",
        "geografia": "GEO",
        "historia": "HIS"
    }
    
    return mapeamento.get(d, d.upper()[:3])

def normalizar_descritor(descritor: str) -> str:
    """Normaliza descritor para comparação"""
    if not descritor:
        return ""
    return normalizar_texto(descritor).upper()
