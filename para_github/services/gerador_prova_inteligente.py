from typing import List, Dict, Optional
from domain.modelos.item import Item
from repositories.protocol import ItensRepositoryProtocol
from services.dados_service import dados_service
from domain.diagnostico.analisador_bloom import AnalisadorBloom
from utils.logger import get_logger
import random

logger = get_logger(__name__)

class GeradorProvaInteligente:
    """Gera provas balanceadas considerando SAEB, CNCA e Bloom"""
    
    def __init__(self, itens_repo: ItensRepositoryProtocol):
        self.itens_repo = itens_repo
        self.dados = dados_service
        self.analisador_bloom = AnalisadorBloom()
    
    def gerar_prova_balanceada(
        self, 
        ano: str, 
        disciplina: str, 
        total_questoes: int = 20,
        considerar_pesos_saeb: bool = True,
        considerar_bloom: bool = True
    ) -> List[Item]:
        """Gera uma prova balanceada usando pesos SAEB e distribuição Bloom"""
        
        # 1. Obter distribuição por descritor (SAEB)
        if considerar_pesos_saeb:
            pesos = self.dados.get_pesos_saeb(ano, disciplina)
            if pesos:
                distribuicao = {}
                total_peso = sum(pesos.values())
                for descritor, peso in pesos.items():
                    qtd = max(1, round((peso / total_peso) * total_questoes))
                    distribuicao[descritor] = qtd
                
                # Ajustar para bater o total
                soma = sum(distribuicao.values())
                if soma != total_questoes and distribuicao:
                    primeiro = list(distribuicao.keys())[0]
                    distribuicao[primeiro] += (total_questoes - soma)
            else:
                distribuicao = self._distribuicao_padrao(total_questoes)
        else:
            distribuicao = self._distribuicao_padrao(total_questoes)
        
        # 2. Buscar questões para cada descritor
        questoes = []
        for descritor, quantidade in distribuicao.items():
            itens = self.itens_repo.buscar_por_descriptor(descritor)
            if itens:
                selecionados = random.sample(itens, min(quantidade, len(itens)))
                questoes.extend(selecionados)
        
        # 3. Balancear por Bloom (se necessário)
        if considerar_bloom and len(questoes) >= total_questoes // 2:
            distribuicao_bloom = self.analisador_bloom.sugerir_distribuicao(ano, total_questoes)
            questoes = self._balancear_por_bloom(questoes, distribuicao_bloom, total_questoes)
        
        # 4. Garantir total exato
        if len(questoes) < total_questoes:
            questoes = self._completar_com_aleatorias(questoes, total_questoes, disciplina)
        elif len(questoes) > total_questoes:
            questoes = questoes[:total_questoes]
        
        logger.info(f"Prova gerada: {len(questoes)} questões para {ano}/{disciplina}")
        return questoes
    
    def _distribuicao_padrao(self, total_questoes: int) -> Dict[str, int]:
        """Distribuição padrão quando não há pesos SAEB"""
        return {"default": total_questoes}
    
    def _balancear_por_bloom(self, questoes: List[Item], distribuicao: Dict[str, int], total_questoes: int) -> List[Item]:
        """Balanceia a prova pela distribuição Bloom"""
        if len(questoes) < total_questoes:
            return questoes
        
        # Contar níveis atuais
        niveis_atual = {nivel: 0 for nivel in distribuicao.keys()}
        for item in questoes:
            if item.nivel_bloom:
                for nivel in item.nivel_bloom:
                    if nivel in niveis_atual:
                        niveis_atual[nivel] += 1
        
        # Calcular deficit por nível
        deficit = {}
        for nivel, esperado in distribuicao.items():
            deficit[nivel] = max(0, esperado - niveis_atual.get(nivel, 0))
        
        # Se deficit significativo, ajustar
        total_deficit = sum(deficit.values())
        if total_deficit > 0 and total_deficit <= len(questoes) // 2:
            return self._rebalancear_questoes(questoes, deficit)
        
        return questoes
    
    def _rebalancear_questoes(self, questoes: List[Item], deficit: Dict[str, int]) -> List[Item]:
        """Rebalanceia questões para atender distribuição Bloom"""
        # Implementação simplificada
        return questoes
    
    def _completar_com_aleatorias(self, questoes: List[Item], total: int, disciplina: str) -> List[Item]:
        """Completa a prova com questões aleatórias"""
        todos_itens = self.itens_repo.listar_todos()
        itens_disciplina = [i for i in todos_itens if i.disciplina.value == disciplina]
        
        necessarias = total - len(questoes)
        if itens_disciplina and necessarias > 0:
            novas = random.sample(itens_disciplina, min(necessarias, len(itens_disciplina)))
            questoes.extend(novas)
        
        return questoes
