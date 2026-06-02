import json
from pathlib import Path
from typing import List, Dict

class TrilhaRecuperacao:
    def __init__(self, caminho: str = "data/pre_requisitos.json"):
        self.caminho = Path(caminho)
        self.pre_requisitos = {}
        self._carregar()
    
    def _carregar(self):
        if self.caminho.exists():
            try:
                with open(self.caminho, "r", encoding="utf-8") as f:
                    self.pre_requisitos = json.load(f)
                print(f"   📚 Trilhas carregadas: {len(self.pre_requisitos)} descritores com plano")
            except Exception as e:
                print(f"   ⚠️ Erro ao carregar pre-requisitos: {e}")
        else:
            print(f"   ⚠️ Arquivo {self.caminho} não encontrado")
    
    def obter_trilha_recuperacao(self, descritor: str) -> List[str]:
        dados = self.pre_requisitos.get(descritor, {})
        return dados.get("trilha_recuperacao", [])
    
    def gerar_plano_recuperacao(self, descritores_com_erro: List[str]) -> List[Dict]:
        plano = []
        for descritor in descritores_com_erro:
            trilha = self.obter_trilha_recuperacao(descritor)
            if trilha:
                plano.append({
                    "descritor": descritor,
                    "trilha": trilha,
                    "prioridade": "Alta" if len(trilha) > 3 else "Média",
                    "etapas": len(trilha)
                })
            else:
                # Criar trilha padrão para descritores sem mapeamento
                plano.append({
                    "descritor": descritor,
                    "trilha": [
                        "Identificar a habilidade específica não desenvolvida",
                        "Reforçar com atividades direcionadas",
                        "Aplicar avaliação diagnóstica",
                        "Revisar e consolidar"
                    ],
                    "prioridade": "Média",
                    "etapas": 4
                })
        return sorted(plano, key=lambda x: x["etapas"], reverse=True)
    
    def exibir_plano(self, plano: List[Dict]):
        if plano:
            print("\n   🎯 Plano de Recuperação Sugerido:")
            for p in plano:
                print(f"\n      📌 {p['descritor']} - Prioridade: {p['prioridade']}")
                for i, etapa in enumerate(p['trilha'][:3], 1):
                    print(f"         {i}. {etapa}")
        else:
            print("\n   ✅ Nenhuma trilha de recuperação necessária no momento")
