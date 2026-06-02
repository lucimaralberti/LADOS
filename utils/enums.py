from enum import Enum
from typing import Optional

class Disciplina(str, Enum):
    """Disciplinas escolares"""
    LP = "LP"
    MAT = "MAT"
    CIEN = "CIEN"
    GEO = "GEO"
    HIST = "HIST"

class AnoEscolar(str, Enum):
    """Anos do Ensino Fundamental"""
    EF1 = "1EF"; EF2 = "2EF"; EF3 = "3EF"; EF4 = "4EF"; EF5 = "5EF"
    EF6 = "6EF"; EF7 = "7EF"; EF8 = "8EF"; EF9 = "9EF"
    
    def para_chave_saeb(self) -> str:
        if self in [AnoEscolar.EF1, AnoEscolar.EF2]: return "2EF"
        elif self in [AnoEscolar.EF3, AnoEscolar.EF4, AnoEscolar.EF5]: return "5EF"
        else: return "9EF"

class TipoErro(str, Enum):
    """Tipos de erro por disciplina"""
    # Língua Portuguesa
    LP_DECODIFICACAO = "lp_decodificacao"
    LP_FLUENCIA = "lp_fluencia"
    LP_LEITURA_LITERAL = "lp_leitura_literal"
    LP_INFERENCIA = "lp_inferencia"
    LP_VOCABULARIO = "lp_vocabulario"
    LP_TEMA = "lp_tema"
    LP_FINALIDADE = "lp_finalidade"
    LP_PRODUCAO = "lp_producao"
    # Matemática
    MT_CONTAGEM = "mt_contagem"
    MT_VALOR_POSICIONAL = "mt_valor_posicional"
    MT_OPERACAO = "mt_operacao"
    MT_OPERACAO_INCORRETA = "mt_operacao_incorreta"
    MT_INTERPRETACAO = "mt_interpretacao"
    MT_PADROES = "mt_padroes"
    MT_GEOMETRIA = "mt_geometria"
    MT_MEDIDAS = "mt_medidas"
    MT_DADOS = "mt_dados"
    NAO_CLASSIFICADO = "nao_classificado"
    
    @classmethod
    def from_string(cls, value: str) -> Optional["TipoErro"]:
        try:
            return cls(value)
        except ValueError:
            return cls.NAO_CLASSIFICADO

class NivelProficiencia(str, Enum):
    """Níveis de proficiência SAEB"""
    ABAIXO_BASICO = "Abaixo do Básico"
    BASICO = "Básico"
    PROFICIENTE = "Proficiente"
    AVANCADO = "Avançado"
    
    def cor(self) -> str:
        return {
            self.ABAIXO_BASICO: "#EF4444",
            self.BASICO: "#F59E0B",
            self.PROFICIENTE: "#10B981",
            self.AVANCADO: "#3B82F6"
        }.get(self, "#6B7280")

class TipoRelatorio(str, Enum):
    INDIVIDUAL = "individual"
    TURMA = "turma"
    ESCOLA = "escola"
    GERAL = "geral"

class StatusAplicacao(str, Enum):
    PENDENTE = "pendente"
    EM_ANDAMENTO = "em_andamento"
    CONCLUIDA = "concluida"
    CANCELADA = "cancelada"
