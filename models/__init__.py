"""
Modelos de dados - LADOS 2.0
Com validação Pydantic
"""

from datetime import datetime
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field, validator

class Alternativa(BaseModel):
    letra: str = Field(..., pattern="^[A-D]$")
    texto: str
    correta: bool = False

class Questao(BaseModel):
    numero: int = Field(..., ge=1, le=50)
    enunciado: str
    alternativas: List[Alternativa]
    descritor: Optional[str] = None
    disciplina: Optional[str] = None
    gabarito: str = Field(..., pattern="^[A-D]$")
    comentario: Optional[str] = None

class Correcao(BaseModel):
    id: str
    sessao_id: str
    numero_prova: int
    tipo_prova: str
    acertos: int
    total: int
    percentual: float
    nota: float
    periodo: str
    ordem: str
    prova: str
    turma: str
    horario: str
    data: str
    timestamp: str
    detalhes: List[Dict[str, Any]] = []
    
    @validator('nota')
    def nota_valida(cls, v):
        if v < 0 or v > 10:
            raise ValueError(f'Nota inválida: {v}. Deve estar entre 0 e 10')
        return v
    
    @validator('percentual')
    def percentual_valido(cls, v):
        if v < 0 or v > 100:
            raise ValueError(f'Percentual inválido: {v}. Deve estar entre 0 e 100')
        return v

class SessaoCorrecao(BaseModel):
    sessao_id: str
    periodo: str
    ordem: str
    prova: str
    turma: str
    total_alunos: int
    media_geral: float
    usuario_nome: str
    usuario_email: Optional[str] = None
    data: str
    correcoes: List[Correcao] = []

class ConfiguracaoSupabase(BaseModel):
    url: str
    key: str
    modo_demo: bool = False
