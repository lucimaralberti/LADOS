import json
from pathlib import Path
from typing import Dict

class GeradorProvaSAEB:
    def __init__(self, caminho_saeb: str = "data/saeb.json"):
        self.caminho = Path(caminho_saeb)
        self.matriz = {}
        self._carregar()
    
    def _carregar(self):
        if self.caminho.exists():
            try:
                with open(self.caminho, "r", encoding="utf-8") as f:
                    self.matriz = json.load(f)
            except Exception as e:
                print(f"Erro ao carregar matriz SAEB: {e}")
    
    def distribuir_por_pesos(self, ano: str, disciplina: str, total_questoes: int) -> Dict[str, int]:
        disciplina_map = {
            "LP": "Língua Portuguesa",
            "MAT": "Matemática",
            "CN": "Ciências da Natureza",
            "CH": "Ciências Humanas"
        }
        disc_nome = disciplina_map.get(disciplina, "")
        dados_ano = self.matriz.get(ano, {})
        dados_disc = dados_ano.get(disc_nome, [])
        
        if not dados_disc:
            # Retorna distribuição padrão se não encontrar
            return {"LP_5EF_D02": max(1, total_questoes // 2), "LP_5EF_D03": max(1, total_questoes // 2)}
        
        pesos = {item["codigo"]: max(0.01, item.get("peso", 0.05)) for item in dados_disc}
        total_peso = sum(pesos.values())
        
        if total_peso <= 0:
            return {}
        
        distribuicao = {}
        for codigo, peso in pesos.items():
            qtd = max(1, round((peso / total_peso) * total_questoes))
            distribuicao[codigo] = qtd
        
        # Ajustar para bater o total
        soma = sum(distribuicao.values())
        if soma != total_questoes and distribuicao:
            primeiro = list(distribuicao.keys())[0]
            distribuicao[primeiro] += (total_questoes - soma)
            if distribuicao[primeiro] < 1:
                distribuicao[primeiro] = 1
        
        return distribuicao
