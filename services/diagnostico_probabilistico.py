from typing import List, Dict, Optional
from domain.avaliacao.avaliador_agregado import AvaliadorAgregado
from domain.diagnostico.analisador_probabilistico import AnalisadorProbabilistico
from domain.avaliacao.calibrador_continuo import CalibradorContinuo
from domain.intervencao.recomendador import Recomendador
from services.dados_service import dados_service
from repositories.protocol import ItensRepositoryProtocol
from domain.modelos.resultado_continuo import ResultadoItemContinuo
from utils.logger import get_logger

logger = get_logger(__name__)

class DiagnosticoServiceProbabilistico:
    """Serviço de diagnóstico probabilístico - COMPLETAMENTE SEM BOOLEAN"""
    
    def __init__(self, itens_repo: ItensRepositoryProtocol):
        self.itens_repo = itens_repo
        self.avaliador = AvaliadorAgregado(itens_repo)
        self.analisador = AnalisadorProbabilistico()
        self.calibrador = CalibradorContinuo(itens_repo)
        self.recomendador = Recomendador()
        self.dados = dados_service
    
    def processar_avaliacao(self, respostas_agregadas: Dict[str, Dict], turma_id: str) -> Dict:
        """Processa avaliação completa (sem booleanos)"""
        logger.info(f"Processando avaliação probabilística para turma {turma_id}")
        
        # 1. Avaliar (resultados contínuos)
        resultados = self.avaliador.avaliar(respostas_agregadas, turma_id)
        
        # 2. Calcular média
        media = self.avaliador.calcular_media_turma(resultados)
        
        # 3. Analisar por descritor (contínuo)
        por_descriptor = self.analisador.analisar_por_descriptor(resultados)
        
        # 4. Analisar erros (contínuo)
        erros = self.analisador.analisar_erros(resultados)
        
        # 5. Identificar descritores críticos
        criticos = self.analisador.identificar_descritores_criticos(resultados)
        
        # 6. Analisar padrão da turma
        padrao = self.analisador.analisar_padrao_erros(resultados)
        
        # 7. Calibrar itens (contínuo)
        self.calibrador.registrar_aplicacao_continua(resultados)
        
        # 8. Recomendações
        recomendacoes = self.recomendador.recomendar(erros, criticos)
        
        # 9. Classificação SAEB
        classificacao = self.dados.get_nivel_saeb("5EF", "LP", media)
        
        return {
            "turma_id": turma_id,
            "media_geral": round(media, 1),
            "nivel": classificacao.get("nivel", "Indeterminado"),
            "descricao_nivel": classificacao.get("descricao", ""),
            "por_descriptor": {k: v.model_dump() if hasattr(v, 'model_dump') else v 
                              for k, v in por_descriptor.items()},
            "erros_principais": {k.value: round(v, 1) for k, v in erros.items()},
            "descritores_criticos": criticos,
            "padrao_turma": padrao,
            "recomendacoes": recomendacoes,
            "metodologia": "probabilistica_continua"
        }

def get_diagnostico_probabilistico(itens_repo):
    return DiagnosticoServiceProbabilistico(itens_repo)
