"""Calibrador - Servico para calibracao em lote de itens"""

from backend.repositories.protocol import ItensRepositoryProtocol


class Calibrador:
    def __init__(self, itens_repo: ItensRepositoryProtocol):
        self.itens_repo = itens_repo
        self.peso_historico = 0.7
        self.minimo_respostas = 10
    
    def calibrar_itens_subutilizados(self):
        itens = self.itens_repo.listar_todos()
        calibrados = 0
        for item in itens:
            if item.total_aplicacoes >= self.minimo_respostas:
                item.recalcular_dificuldade(self.peso_historico)
                self.itens_repo.atualizar_item(item)
                calibrados += 1
        return {
            "total_itens": len(itens),
            "itens_calibrados": calibrados,
            "media_aplicacoes": sum(i.total_aplicacoes for i in itens) / len(itens) if itens else 0
        }

