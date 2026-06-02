from typing import List, Dict, Optional
from repositories.turma_repo import TurmaRepository
from domain.modelos.turma import Turma
from domain.avaliacao.agregador_turma import AgregadorTurma
from repositories.resultados_repo import ResultadosRepository
from utils.logger import get_logger

logger = get_logger(__name__)

class TurmaService:
    """Serviço para gestão de turmas e seus resultados pedagógicos"""
    
    def __init__(self, turma_repo: TurmaRepository, resultados_repo: ResultadosRepository):
        self.turma_repo = turma_repo
        self.resultados_repo = resultados_repo
        self.agregador = AgregadorTurma()
    
    def criar_turma(self, nome: str, ano: str, escola_id: str, professor_id: str) -> Turma:
        """Cria uma nova turma"""
        turma = Turma(
            nome=nome,
            ano=ano,
            escola_id=escola_id,
            professor_id=professor_id
        )
        self.turma_repo.salvar(turma)
        logger.info(f"Turma criada: {turma.nome} (ID: {turma.id})")
        return turma
    
    def obter_dashboard_turma(self, turma_id: str) -> Dict:
        """Gera dados para dashboard da turma"""
        resultados = self.resultados_repo.buscar_por_turma(turma_id)
        
        if not resultados:
            return {"turma_id": turma_id, "mensagem": "Nenhum resultado encontrado"}
        
        agregado = self.agregador.agregar_resultados(resultados)
        
        return {
            "turma_id": turma_id,
            "total_avaliacoes": len(resultados),
            "media_geral": agregado.get("media_geral", 0),
            "descritores_criticos": agregado.get("descritores_criticos", []),
            "recomendacoes": agregado.get("recomendacoes", [])
        }
