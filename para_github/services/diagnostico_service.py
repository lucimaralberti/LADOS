from typing import List, Dict, Optional
from domain.avaliacao.avaliador import Avaliador
from domain.diagnostico.analisador import Analisador
from domain.diagnostico.classificador import Classificador
from domain.diagnostico.analisador_bloom import AnalisadorBloom
from domain.intervencao.recomendador import Recomendador
from domain.avaliacao.agregador_turma import AgregadorTurma
from services.relatorio_pdf import GeradorRelatorioPDF
from services.dados_service import dados_service
from repositories.protocol import ItensRepositoryProtocol
from repositories.resultados_repo import ResultadosRepository
from domain.modelos.resultado import ResultadoProva
from domain.modelos.turma import Turma
from domain.modelos.diagnostico_turma import DiagnosticoTurma
from utils.enums import NivelProficiencia
from utils.logger import get_logger

logger = get_logger(__name__)

class DiagnosticoService:
    """Serviço principal de diagnóstico - com todas as integrações pedagógicas"""
    
    def __init__(
        self,
        itens_repo: ItensRepositoryProtocol,
        resultados_repo: Optional[ResultadosRepository] = None
    ):
        self.itens_repo = itens_repo
        self.resultados_repo = resultados_repo or ResultadosRepository()
        self.avaliador = Avaliador(itens_repo)
        self.analisador = Analisador()
        self.classificador = Classificador()
        self.recomendador = Recomendador()
        self.agregador = AgregadorTurma()
        self.analisador_bloom = AnalisadorBloom()
        self.pdf_gerador = GeradorRelatorioPDF()
        self.dados = dados_service
        
        logger.info("DiagnosticoService inicializado com todas as integrações")
    
    def processar_prova(self, respostas: Dict[str, str], turma_id: str, 
                        aplicar_aplicacoes: bool = True) -> ResultadoProva:
        """Processa uma prova e retorna o resultado"""
        logger.info(f"Processando prova para turma {turma_id}")
        
        resultado = self.avaliador.corrigir(respostas, turma_id, registrar_aplicacoes=aplicar_aplicacoes)
        self.resultados_repo.salvar(resultado)
        
        logger.info(f"Prova processada: {resultado.total_acertos}/{resultado.total_itens} acertos ({resultado.percentual_acertos:.1f}%)")
        return resultado
    
    def obter_diagnostico_completo(self, turma_id: str, turma: Optional[Turma] = None) -> DiagnosticoTurma:
        """Obtém diagnóstico completo e enriquecido da turma"""
        logger.info(f"Obtendo diagnóstico completo da turma {turma_id}")
        
        resultados = self.resultados_repo.buscar_por_turma(turma_id)
        
        if not resultados:
            logger.warning(f"Nenhum resultado encontrado para turma {turma_id}")
            return DiagnosticoTurma(
                turma_id=turma_id,
                media_geral=0,
                nivel_geral=NivelProficiencia.ABAIXO_BASICO,
                descricao_nivel="Sem dados suficientes"
            )
        
        # Análise básica
        agregado = self.agregador.agregar_resultados(resultados)
        media_geral = agregado["media_geral"]
        
        # Classificação SAEB usando escalas reais
        ano = turma.ano if turma else "5EF"
        disciplina = "LP"  # ou detectar da prova
        classificacao_saeb = self.dados.get_nivel_saeb(ano, disciplina, media_geral)
        
        nivel_geral = NivelProficiencia.ABAIXO_BASICO
        for nivel in NivelProficiencia:
            if nivel.value.lower() == classificacao_saeb["nivel"].lower():
                nivel_geral = nivel
                break
        
        # Análise Bloom
        todos_itens = []
        for r in resultados:
            todos_itens.extend(r.itens)
        
        itens_originais = self.itens_repo.listar_todos()
        perfil_bloom = self.analisador_bloom.analisar_perfil_turma(resultados, itens_originais)
        
        # Identificar lacunas de pré-requisitos
        lacunas = []
        for critico in agregado.get("descritores_criticos", [])[:3]:
            descritor = critico.get("descritor", "")
            pre_reqs = self.dados.get_pre_requisitos_lista(descritor)
            if pre_reqs:
                lacunas.append({
                    "descritor": descritor,
                    "pre_requisitos": pre_reqs,
                    "peso_total": sum(p.get("peso", 0) for p in pre_reqs)
                })
        
        # Obter trilha de recuperação
        trilha = []
        if agregado.get("descritores_criticos"):
            principal = agregado["descritores_criticos"][0].get("descritor", "")
            trilha = self.dados.get_trilha_recuperacao(principal)
        
        # Criar diagnóstico completo
        diagnostico = DiagnosticoTurma(
            turma_id=turma_id,
            media_geral=round(media_geral, 1),
            nivel_geral=nivel_geral,
            descricao_nivel=classificacao_saeb.get("descricao", ""),
            total_avaliacoes=len(resultados),
            por_descriptor=agregado.get("por_descriptor", {}),
            por_bloom=perfil_bloom.get("desempenho_por_nivel", {}),
            por_erro=agregado.get("erros_principais", {}),
            descritores_criticos=agregado.get("descritores_criticos", []),
            lacunas_pre_requisitos=lacunas,
            niveis_bloom_criticos=[n["nivel"] for n in perfil_bloom.get("niveis_criticos", [])],
            recomendacoes=agregado.get("recomendacoes", []),
            trilha_recuperacao=trilha
        )
        
        logger.info(f"Diagnóstico concluído: {diagnostico}")
        return diagnostico
    
    def obter_diagnostico_turma(self, turma_id: str) -> Dict:
        """Método legado para compatibilidade"""
        diagnostico = self.obter_diagnostico_completo(turma_id)
        return {
            "turma_id": diagnostico.turma_id,
            "total_avaliacoes": diagnostico.total_avaliacoes,
            "media_geral": diagnostico.media_geral,
            "nivel": diagnostico.nivel_geral.value,
            "descricao_nivel": diagnostico.descricao_nivel,
            "por_descriptor": diagnostico.por_descriptor,
            "descritores_criticos": diagnostico.descritores_criticos,
            "recomendacoes": diagnostico.recomendacoes,
            "perfil_bloom": diagnostico.por_bloom,
            "lacunas_pre_requisitos": diagnostico.lacunas_pre_requisitos,
            "trilha_recuperacao": diagnostico.trilha_recuperacao
        }
    
    def gerar_relatorio_pdf(self, diagnostico: Dict, turma: Turma) -> str:
        """Gera relatório PDF completo com todas as análises"""
        return self.pdf_gerador.gerar_relatorio_turma_completo(
            turma_nome=turma.nome,
            diagnostico=diagnostico
        )
