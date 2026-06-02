from typing import List, Dict, Optional
from datetime import datetime
from backend.core.modelos.resultado import ResultadoItem, ResultadoProva
from backend.repositories.protocol import ItensRepositoryProtocol

class Avaliador:
    def __init__(self, itens_repo: ItensRepositoryProtocol):
        self.itens_repo = itens_repo
    
    def corrigir(
        self, 
        respostas: Dict[str, str], 
        turma_id: str = "turma_padrao",
        registrar_aplicacoes: bool = False
    ) -> ResultadoProva:
        """Corrige uma prova e retorna ResultadoProva
        
        Args:
            respostas: Dicionário {item_id: resposta}
            turma_id: Identificador da turma
            registrar_aplicacoes: Se deve registrar aplicações no repositório
        """
        resultados = []
        itens_nao_encontrados = []
        
        for item_id, resposta in respostas.items():
            item = self.itens_repo.buscar_por_id(item_id)
            if not item:
                itens_nao_encontrados.append(item_id)
                continue
            
            correta = (resposta == item.gabarito)
            pontuacao = item.pontuacao_item(correta)
            
            resultados.append(ResultadoItem(
                item_id=item_id,
                resposta=resposta,
                correta=correta,
                descritor=item.descritor,
                habilidade=item.habilidade,
                tipo_erro=item.tipo_erro_provavel if not correta else None,
                pontuacao=pontuacao
            ))
            
            if registrar_aplicacoes:
                self.itens_repo.registrar_aplicacao(item_id, correta)
        
        if itens_nao_encontrados:
            print(f"   ⚠️ Itens não encontrados: {itens_nao_encontrados}")
        
        return ResultadoProva(
            turma_id=turma_id,
            aplicacao_id=f"app_{datetime.now().timestamp()}",
            data=datetime.now(),
            itens=resultados
        )
    
    def calcular_proficiencia_simples(self, resultados: List[ResultadoItem]) -> float:
        if not resultados:
            return 0.0
        return sum(r.pontuacao for r in resultados) / len(resultados)


