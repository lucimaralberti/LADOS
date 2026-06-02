from typing import List, Dict, Optional
from domain.modelos.plano_intervencao import PlanoDeIntervencao, NivelPrioridade
from domain.modelos.avaliacao_verificacao import AvaliacaoVerificacao
from domain.intervencao.recomendador import Recomendador
from repositories.itens_repo import ItensRepository
from repositories.resultados_repo import ResultadosRepository
from domain.diagnostico.analisador import Analisador
from utils.logger import get_logger
import json
from pathlib import Path

logger = get_logger(__name__)

class IntervencaoService:
    """Serviço para gerenciar intervenções pedagógicas e planos de aula"""
    
    def __init__(self, itens_repo: ItensRepository, resultados_repo: ResultadosRepository):
        self.itens_repo = itens_repo
        self.resultados_repo = resultados_repo
        self.recomendador = Recomendador()
        self.analisador = Analisador()
        self._planos: List[PlanoDeIntervencao] = []
        self._avaliacoes: List[AvaliacaoVerificacao] = []
        self._carregar_dados()
    
    def _carregar_dados(self):
        """Carrega planos e avaliações salvos"""
        planos_file = Path("data/planos_intervencao.json")
        if planos_file.exists():
            try:
                with open(planos_file, "r", encoding="utf-8") as f:
                    dados = json.load(f)
                self._planos = [PlanoDeIntervencao.model_validate(p) for p in dados]
                logger.info(f"Carregados {len(self._planos)} planos de intervenção")
            except Exception as e:
                logger.error(f"Erro ao carregar planos: {e}")
        
        avaliacoes_file = Path("data/avaliacoes_verificacao.json")
        if avaliacoes_file.exists():
            try:
                with open(avaliacoes_file, "r", encoding="utf-8") as f:
                    dados = json.load(f)
                self._avaliacoes = [AvaliacaoVerificacao.model_validate(a) for a in dados]
                logger.info(f"Carregadas {len(self._avaliacoes)} avaliações de verificação")
            except Exception as e:
                logger.error(f"Erro ao carregar avaliações: {e}")
    
    def _salvar_planos(self):
        """Salva planos de intervenção"""
        planos_file = Path("data/planos_intervencao.json")
        try:
            planos_file.parent.mkdir(exist_ok=True)
            with open(planos_file, "w", encoding="utf-8") as f:
                json.dump([p.to_dict() for p in self._planos], f, indent=2, ensure_ascii=False)
        except Exception as e:
            logger.error(f"Erro ao salvar planos: {e}")
    
    def _salvar_avaliacoes(self):
        """Salva avaliações de verificação"""
        avaliacoes_file = Path("data/avaliacoes_verificacao.json")
        try:
            avaliacoes_file.parent.mkdir(exist_ok=True)
            with open(avaliacoes_file, "w", encoding="utf-8") as f:
                json.dump([a.to_dict() for a in self._avaliacoes], f, indent=2, ensure_ascii=False)
        except Exception as e:
            logger.error(f"Erro ao salvar avaliações: {e}")
    
    def gerar_plano_para_turma(self, turma_id: str, diagnostico: Dict) -> Optional[PlanoDeIntervencao]:
        """Gera plano de intervenção para uma turma baseado no diagnóstico"""
        descritores_criticos = diagnostico.get("descritores_criticos", [])
        if not descritores_criticos:
            logger.info(f"Turma {turma_id} não tem descritores críticos")
            return None
        
        plano = self.recomendador.gerar_plano_intervencao(turma_id, descritores_criticos)
        if plano:
            self._planos.append(plano)
            self._salvar_planos()
        
        return plano
    
    def registrar_aplicacao_plano(self, plano_id: str) -> bool:
        """Registra que o plano foi aplicado"""
        for plano in self._planos:
            if plano.id == plano_id:
                plano.aplicado = True
                from datetime import datetime
                plano.data_aplicacao = datetime.now()
                self._salvar_planos()
                logger.info(f"Plano {plano_id} registrado como aplicado")
                return True
        return False
    
    def criar_avaliacao_verificacao(self, turma_id: str, plano_id: str, 
                                     descritores: List[str], questoes_ids: List[str]) -> AvaliacaoVerificacao:
        """Cria uma avaliação de verificação para testar a eficácia da intervenção"""
        avaliacao = AvaliacaoVerificacao(
            turma_id=turma_id,
            plano_intervencao_id=plano_id,
            descritores_avaliados=descritores,
            itens_ids=questoes_ids
        )
        self._avaliacoes.append(avaliacao)
        self._salvar_avaliacoes()
        logger.info(f"Avaliação de verificação criada para turma {turma_id}")
        return avaliacao
    
    def calcular_evolucao(self, turma_id: str, diagnostico_antes: Dict, diagnostico_depois: Dict) -> Dict:
        """Calcula a evolução da turma após a intervenção"""
        media_antes = diagnostico_antes.get("media_geral", 0)
        media_depois = diagnostico_depois.get("media_geral", 0)
        variacao = media_depois - media_antes
        
        return {
            "turma_id": turma_id,
            "media_antes": round(media_antes, 1),
            "media_depois": round(media_depois, 1),
            "variacao": round(variacao, 1),
            "percentual_melhoria": round((variacao / media_antes * 100) if media_antes > 0 else 0, 1),
            "status": "melhorou" if variacao > 0 else ("piorou" if variacao < 0 else "estavel"),
            "recomendacao": "Continuar intervenção" if variacao < 5 else "Avançar para próximo tópico"
        }
