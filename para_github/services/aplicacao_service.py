"""Serviço intermediário entre API e Domínio"""

from typing import Dict, List, Optional
from repositories.itens_repo import ItensRepository
from repositories.resultados_repo import ResultadosRepository
from services.diagnostico_service import DiagnosticoService
from services.gerador_prova_inteligente import GeradorProvaInteligente
from domain.modelos.turma import Turma
from config import settings
from utils.logger import get_logger

logger = get_logger(__name__)

class AplicacaoService:
    """Camada intermediária que desacopla a API do domínio"""
    
    def __init__(self):
        self.itens_repo = ItensRepository(str(settings.itens_file))
        self.resultados_repo = ResultadosRepository(str(settings.resultados_file))
        self.diagnostico_service = DiagnosticoService(self.itens_repo, self.resultados_repo)
        self.gerador_prova = GeradorProvaInteligente(self.itens_repo)
    
    def listar_itens(self, ano: Optional[str] = None, disciplina: Optional[str] = None) -> Dict:
        """Lista itens com filtros"""
        itens = self.itens_repo.listar_todos()
        
        if ano:
            itens = [i for i in itens if i.ano.value == ano]
        if disciplina:
            itens = [i for i in itens if i.disciplina.value == disciplina]
        
        return {
            "total": len(itens),
            "itens": [{
                "id": i.id,
                "enunciado": i.enunciado[:100] + "...",
                "descritor": i.descritor,
                "dificuldade": i.dificuldade
            } for i in itens[:50]]
        }
    
    def gerar_prova(self, ano: str, disciplina: str, total_questoes: int = 20) -> Dict:
        """Gera uma prova balanceada"""
        questoes = self.gerador_prova.gerar_prova_balanceada(ano, disciplina, total_questoes)
        
        return {
            "total_questoes": len(questoes),
            "questoes": [{
                "id": q.id,
                "enunciado": q.enunciado,
                "alternativas": q.alternativas,
                "descritor": q.descritor,
                "nivel_bloom": q.nivel_bloom
            } for q in questoes]
        }
    
    def processar_avaliacao_turma(self, turma_id: str, respostas_itens: Dict[str, Dict]) -> Dict:
        """Processa avaliação de turma (agregada)"""
        # Converter respostas agregadas
        respostas_individuais = {}
        for item_id, dados in respostas_itens.items():
            total = dados.get("total_respostas", 0)
            acertos = dados.get("total_acertos", 0)
            taxa = acertos / total if total > 0 else 0
            respostas_individuais[item_id] = "A" if taxa > 0.5 else "B"
        
        resultado = self.diagnostico_service.processar_prova(
            respostas_individuais, turma_id, aplicar_aplicacoes=False
        )
        
        diagnostico = self.diagnostico_service.obter_diagnostico_completo(turma_id)
        
        return {
            "turma_id": turma_id,
            "media_geral": diagnostico.media_geral,
            "nivel": diagnostico.nivel_geral.value if hasattr(diagnostico.nivel_geral, 'value') else str(diagnostico.nivel_geral),
            "total_avaliacoes": diagnostico.total_avaliacoes,
            "descritores_criticos": diagnostico.descritores_criticos[:5],
            "recomendacoes": diagnostico.recomendacoes[:3]
        }
    
    def obter_diagnostico(self, turma_id: str) -> Dict:
        """Obtém diagnóstico de uma turma"""
        diagnostico = self.diagnostico_service.obter_diagnostico_completo(turma_id)
        
        return {
            "turma_id": diagnostico.turma_id,
            "media_geral": diagnostico.media_geral,
            "nivel": diagnostico.nivel_geral.value if hasattr(diagnostico.nivel_geral, 'value') else str(diagnostico.nivel_geral),
            "descricao_nivel": diagnostico.descricao_nivel,
            "total_avaliacoes": diagnostico.total_avaliacoes,
            "descritores_criticos": diagnostico.descritores_criticos,
            "recomendacoes": diagnostico.recomendacoes
        }

# Instância global
aplicacao = AplicacaoService()
