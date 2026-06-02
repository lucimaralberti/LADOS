from typing import List, Dict
from domain.modelos.simulado import Simulado
from repositories.itens_repo import ItensRepository
from domain.avaliacao.avaliador import Avaliador
from domain.diagnostico.analisador import Analisador

class SimuladoService:
    def __init__(self, itens_repo: ItensRepository):
        self.itens_repo = itens_repo
        self.avaliador = Avaliador(itens_repo)
        self.analisador = Analisador()
    
    def criar_simulado(self, titulo: str, ano_referencia: str, disciplinas: List[str], 
                       questoes_por_disciplina: int, escola_id: str, criado_por: str) -> Simulado:
        """Cria um novo simulado"""
        total_questoes = len(disciplinas) * questoes_por_disciplina
        simulado = Simulado(
            titulo=titulo,
            ano_referencia=ano_referencia,
            disciplinas=disciplinas,
            total_questoes=total_questoes,
            escola_id=escola_id,
            criado_por=criado_por
        )
        return simulado
    
    def gerar_ids_anonimos(self, simulado: Simulado, quantidade_alunos: int) -> Simulado:
        """Gera IDs anônimos para os alunos"""
        simulado.gerar_ids_anonimos(quantidade_alunos)
        return simulado
    
    def processar_resposta_anonima(self, simulado_id: str, id_anonimo: str, respostas: Dict[str, str]) -> Dict:
        """Processa a resposta de um aluno anônimo"""
        resultado_prova = self.avaliador.corrigir(respostas)
        return {
            "id_anonimo": id_anonimo,
            "simulado_id": simulado_id,
            "acertos": resultado_prova.total_acertos,
            "total": resultado_prova.total_itens,
            "percentual": resultado_prova.percentual_acertos
        }
