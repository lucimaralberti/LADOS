import json
from pathlib import Path
from typing import List, Optional
from datetime import datetime
from domain.modelos.resultado import ResultadoProva
from utils.logger import get_logger

logger = get_logger(__name__)

class ResultadosRepository:
    """Repositório para gerenciar resultados de provas - versão corrigida"""
    
    def __init__(self, caminho_arquivo: Optional[str] = None):
        if caminho_arquivo is None:
            from config import settings
            caminho_arquivo = str(settings.resultados_file)
        self.caminho = Path(caminho_arquivo)
        self.resultados: List[ResultadoProva] = []
        self._carregar()
    
    def _carregar(self):
        if self.caminho.exists():
            try:
                with open(self.caminho, "r", encoding="utf-8") as f:
                    dados = json.load(f)
                self.resultados = [ResultadoProva.model_validate(r) for r in dados]
                logger.info(f"Carregados {len(self.resultados)} resultados do arquivo")
            except Exception as e:
                logger.error(f"Erro ao carregar resultados: {e}")
                self.resultados = []
        else:
            logger.info(f"Arquivo {self.caminho} não existe. Iniciando com lista vazia.")
            self.resultados = []
    
    def _salvar(self):
        try:
            self.caminho.parent.mkdir(parents=True, exist_ok=True)
            with open(self.caminho, "w", encoding="utf-8") as f:
                json.dump([r.model_dump() for r in self.resultados], f, indent=2, ensure_ascii=False)
            logger.debug(f"Salvos {len(self.resultados)} resultados")
        except Exception as e:
            logger.error(f"Erro ao salvar resultados: {e}")
    
    def salvar(self, resultado: ResultadoProva) -> bool:
        """Salva um novo resultado"""
        try:
            self.resultados.append(resultado)
            self._salvar()
            logger.info(f"Resultado salvo: {resultado.id} para turma {resultado.turma_id}")
            return True
        except Exception as e:
            logger.error(f"Erro ao salvar resultado: {e}")
            return False
    
    def buscar_por_id(self, resultado_id: str) -> Optional[ResultadoProva]:
        for resultado in self.resultados:
            if resultado.id == resultado_id:
                return resultado
        return None
    
    def buscar_por_turma(self, turma_id: str) -> List[ResultadoProva]:
        return [r for r in self.resultados if r.turma_id == turma_id]
    
    def buscar_por_periodo(self, data_inicio: datetime, data_fim: datetime) -> List[ResultadoProva]:
        return [r for r in self.resultados if data_inicio <= r.data <= data_fim]
    
    def listar_todos(self) -> List[ResultadoProva]:
        return self.resultados.copy()
    
    def contar_por_turma(self, turma_id: str) -> int:
        return len(self.buscar_por_turma(turma_id))
    
    def media_por_turma(self, turma_id: str) -> float:
        resultados = self.buscar_por_turma(turma_id)
        if not resultados:
            return 0.0
        total_acertos = sum(r.total_acertos for r in resultados)
        total_questoes = sum(r.total_itens for r in resultados)
        return (total_acertos / total_questoes * 100) if total_questoes > 0 else 0.0
