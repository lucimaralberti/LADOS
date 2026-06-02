"""
services/servico_geracao_prova.py
Serviço para geração de prova com filtros por:
- Ano escolar
- Disciplina(s)
- Tipo de matriz (BNCC/CNCA/SAEB)
- Descritores específicos (máx 5)
- Número de questões
"""

from typing import List, Dict, Optional, Tuple
from repositories.itens_repo import ItensRepository
from domain.modelos.item import Item
from utils.enums import Disciplina, AnoEscolar
from utils.logger import get_logger
import json
from pathlib import Path

logger = get_logger(__name__)

class ServicoGeracaoProva:
    """Serviço para geração de provas com filtros avançados"""
    
    def __init__(self, itens_repo: ItensRepository):
        self.itens_repo = itens_repo
        self._carregar_matrizes()
    
    def _carregar_matrizes(self):
        """Carrega as matrizes curriculares"""
        self.matrizes = {
            "BNCC": self._carregar_json("data/bncc.json"),
            "CNCA": self._carregar_json("data/cnca.json"),
            "SAEB": self._carregar_json("data/mapeamento.json")
        }
    
    def _carregar_json(self, caminho: str) -> Dict:
        path = Path(caminho)
        if path.exists():
            with open(path, "r", encoding="utf-8") as f:
                return json.load(f)
        return {}
    
    def obter_disciplinas_por_ano(self, ano: str) -> List[str]:
        """Retorna disciplinas disponíveis por ano escolar"""
        ano_num = int(ano.replace("EF", ""))
        
        if ano_num <= 4:  # 1EF ao 4EF
            return ["LP", "MAT"]
        elif ano_num == 5:  # 5EF
            return ["LP", "MAT", "CIEN", "GEO", "HIST"]
        else:  # 6EF ao 9EF
            return ["LP", "MAT", "CIEN", "GEO", "HIST", "CH", "CN"]
    
    def obter_descritores_por_matriz(self, matriz: str, ano: str, disciplina: str) -> List[Dict]:
        """Retorna descritores disponíveis por matriz, ano e disciplina"""
        descritores = []
        
        if matriz == "CNCA":
            # CNCA: anos 1EF ao 5EF
            dados = self.matrizes.get("CNCA", {}).get(ano, {})
            if disciplina == "LP":
                disc_key = "Língua Portuguesa"
            elif disciplina == "MAT":
                disc_key = "Matemática"
            else:
                return []
            
            for item in dados.get(disc_key, []):
                descritores.append({
                    "codigo": item.get("codigo"),
                    "habilidade": item.get("habilidade"),
                    "tipo": item.get("tipo", "central")
                })
        
        elif matriz == "SAEB":
            # SAEB: descritores do mapeamento
            for codigo, dados in self.matrizes.get("SAEB", {}).items():
                if codigo.startswith(f"{disciplina}_") and dados.get("ano") == ano:
                    descritores.append({
                        "codigo": codigo,
                        "habilidade": dados.get("descricao", ""),
                        "dominio": dados.get("dominio", "")
                    })
        
        elif matriz == "BNCC":
            # BNCC: códigos BNCC
            dados = self.matrizes.get("BNCC", {}).get(disciplina, {}).get(ano, [])
            for item in dados:
                descritores.append({
                    "codigo": item.get("codigo"),
                    "habilidade": item.get("habilidade")
                })
        
        return descritores[:50]  # Limitar para performance
    
    def gerar_prova(self, ano: str, disciplinas: List[str], tipo_matriz: str,
                    descritores: List[str], num_questoes: int) -> Tuple[List[Item], Dict]:
        """Gera prova com os filtros especificados"""
        
        # Buscar itens pelos descritores
        itens_selecionados = []
        for descritor in descritores:
            itens = self.itens_repo.buscar_por_descriptor(descritor)
            itens_selecionados.extend(itens)
        
        # Remover duplicatas
        itens_selecionados = list({item.id: item for item in itens_selecionados}.values())
        
        # Selecionar aleatoriamente conforme quantidade
        import random
        if len(itens_selecionados) > num_questoes:
            itens_selecionados = random.sample(itens_selecionados, num_questoes)
        
        # Calcular distribuição por disciplina
        distribuicao = {}
        for disc in disciplinas:
            distribuicao[disc] = len([i for i in itens_selecionados if i.disciplina.value == disc])
        
        return itens_selecionados, {
            "ano": ano,
            "disciplinas": disciplinas,
            "tipo_matriz": tipo_matriz,
            "descritores_selecionados": descritores,
            "total_questoes": len(itens_selecionados),
            "distribuicao_por_disciplina": distribuicao
        }

# Instância global
servico_geracao = None

def get_servico_geracao(itens_repo):
    global servico_geracao
    if servico_geracao is None:
        servico_geracao = ServicoGeracaoProva(itens_repo)
    return servico_geracao
