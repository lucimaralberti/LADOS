from typing import List, Dict, Optional
from domain.avaliacao.avaliador_agregado import AvaliadorAgregado
from domain.diagnostico.analisador import Analisador
from domain.diagnostico.classificador import Classificador
from domain.diagnostico.analisador_bloom import AnalisadorBloom
from domain.intervencao.recomendador import Recomendador
from domain.avaliacao.agregador_turma import AgregadorTurma
from services.relatorio_pdf import GeradorRelatorioPDF
from services.dados_service import dados_service
from repositories.protocol import ItensRepositoryProtocol
from repositories.resultados_repo import ResultadosRepository
from domain.modelos.avaliacao_agregada import AvaliacaoAgregada
from domain.modelos.turma import Turma
from domain.modelos.diagnostico_turma import DiagnosticoTurma
from utils.enums import NivelProficiencia
from utils.logger import get_logger

logger = get_logger(__name__)

class DiagnosticoServiceAgregado:
    """Serviço de diagnóstico para dados agregados (nível turma)"""
    
    def __init__(
        self,
        itens_repo: ItensRepositoryProtocol,
        resultados_repo: Optional[ResultadosRepository] = None
    ):
        self.itens_repo = itens_repo
        self.resultados_repo = resultados_repo or ResultadosRepository()
        self.avaliador_agregado = AvaliadorAgregado(itens_repo)
        self.analisador = Analisador()
        self.classificador = Classificador()
        self.analisador_bloom = AnalisadorBloom()
        self.recomendador = Recomendador()
        self.agregador = AgregadorTurma()
        self.pdf_gerador = GeradorRelatorioPDF()
        self.dados = dados_service
        
        logger.info("DiagnosticoServiceAgregado inicializado")
    
    def processar_avaliacao_agregada(self, respostas_agregadas: Dict[str, Dict], turma_id: str) -> AvaliacaoAgregada:
        """Processa uma avaliação a partir de dados agregados (SEM SIMULAÇÃO)"""
        logger.info(f"Processando avaliação agregada para turma {turma_id}")
        
        avaliacao = self.avaliador_agregado.avaliar(respostas_agregadas, turma_id)
        
        # Salvar no repositório (convertendo para formato compatível)
        # TODO: adaptar resultados_repo para aceitar AvaliacaoAgregada
        
        logger.info(f"Avaliação processada: média={avaliacao.media_taxa_acerto:.1%}")
        return avaliacao
    
    def calcular_media_turma(self, avaliacoes: List[AvaliacaoAgregada]) -> float:
        """Calcula média ponderada da turma a partir de avaliações agregadas"""
        if not avaliacoes:
            return 0.0
        
        total_peso = 0
        total_pontos = 0
        
        for avaliacao in avaliacoes:
            peso = len(avaliacao.itens)  # peso pelo número de questões
            pontuacao = avaliacao.pontuacao_ponderada(self.itens_repo)
            total_peso += peso
            total_pontos += pontuacao * peso
        
        return (total_pontos / total_peso) if total_peso > 0 else 0.0
    
    def obter_diagnostico_turma_agregado(self, turma_id: str, avaliacoes: List[AvaliacaoAgregada]) -> DiagnosticoTurma:
        """Obtém diagnóstico da turma a partir de avaliações agregadas"""
        if not avaliacoes:
            logger.warning(f"Nenhuma avaliação agregada para turma {turma_id}")
            return DiagnosticoTurma(
                turma_id=turma_id,
                media_geral=0,
                nivel_geral=NivelProficiencia.ABAIXO_BASICO,
                descricao_nivel="Sem dados suficientes"
            )
        
        # Calcular média geral
        media_geral = self.calcular_media_turma(avaliacoes)
        
        # Coletar todos os itens para análise de descritores
        todos_itens_agg = []
        for avaliacao in avaliacoes:
            todos_itens_agg.extend(avaliacao.itens)
        
        # Converter para formato que o Analisador entende
        # (precisamos de ResultadoItem para análise de descritor)
        from domain.modelos.resultado import ResultadoItem
        
        resultados_itens = []
        for item_agg in todos_itens_agg:
            item = self.itens_repo.buscar_por_id(item_agg.item_id)
            if item:
                # Usar taxa de acerto para determinar se "acertou" (probabilístico)
                # Para análise de descritor, consideramos acertou se taxa > 0.5
                # Isso ainda é uma simplificação, mas melhor que simular resposta única
                resultados_itens.append(ResultadoItem(
                    item_id=item_agg.item_id,
                    resposta="",
                    correta=item_agg.taxa_acerto > 0.5,
                    descritor=item.descritor,
                    habilidade=item.habilidade,
                    pontuacao=item_agg.taxa_acerto * item.dificuldade
                ))
        
        # Análises
        por_descriptor = self.analisador.analisar_por_descriptor(resultados_itens)
        erros = self.analisador.analisar_erros(resultados_itens)
        criticos = self.analisador.identificar_descritores_criticos(resultados_itens)
        
        # Classificação SAEB
        classificacao = self.dados.get_nivel_saeb("5EF", "LP", media_geral)
        nivel_geral = NivelProficiencia.ABAIXO_BASICO
        for nivel in NivelProficiencia:
            if nivel.value == classificacao["nivel"]:
                nivel_geral = nivel
                break
        
        # Recomendações
        recomendacoes = self.recomendador.recomendar(erros, criticos)
        
        return DiagnosticoTurma(
            turma_id=turma_id,
            media_geral=round(media_geral, 1),
            nivel_geral=nivel_geral,
            descricao_nivel=classificacao.get("descricao", ""),
            total_avaliacoes=len(avaliacoes),
            por_descriptor=por_descriptor,
            descritores_criticos=criticos,
            recomendacoes=recomendacoes,
            trilha_recuperacao=criticos[:3] if criticos else []
        )

# Instância global
diagnostico_agregado = None

def get_diagnostico_agregado(itens_repo, resultados_repo=None):
    global diagnostico_agregado
    if diagnostico_agregado is None:
        diagnostico_agregado = DiagnosticoServiceAgregado(itens_repo, resultados_repo)
    return diagnostico_agregado
