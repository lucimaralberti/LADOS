# -*- coding: utf-8 -*-
"""
Mapeador de Matrizes BNCC, CNCA e SAEB
Permite buscar questoes por equivalencia entre as matrizes
"""

import json
from pathlib import Path
from typing import List, Dict, Set, Optional

class MapeadorMatrizes:
    def buscar_equivalentes_simples(self, descritor: str, tipo: str) -> bool:
        """Verifica se um descritor pertence ao tipo solicitado"""
        for codigo, relacao in self.mapeamento.items():
            if codigo == descritor or descritor in codigo:
                if tipo == "cnca" and relacao.get("cnca"):
                    return True
                elif tipo == "bncc" and relacao.get("bncc"):
                    return True
                elif tipo == "saeb" and relacao.get("saeb"):
                    return True
        return False
    """Gerencia a equivalencia entre BNCC, CNCA e SAEB"""
    
    def __init__(self, mapeamento_path: str = "data/mapeamento_descritores.json"):
        self.mapeamento_path = Path(mapeamento_path)
        self.mapeamento = self._carregar_mapeamento()
    
    def _carregar_mapeamento(self) -> Dict:
        """Carrega o arquivo de mapeamento descritores"""
        if self.mapeamento_path.exists():
            with open(self.mapeamento_path, "r", encoding="utf-8") as f:
                dados = json.load(f)
                return dados.get("mapeamento_descritores", {})
        return {}
    
    def buscar_equivalentes(self, descritor: str, tipo: str) -> Set[str]:
        """
        Busca descritores equivalentes nas outras matrizes
        
        Args:
            descritor: O codigo do descritor (ex: '2EF07_P', 'EF02LP07', 'D1')
            tipo: Tipo do descritor ('bncc', 'cnca', 'saeb')
        
        Returns:
            Conjunto de descritores equivalentes (incluindo o original)
        """
        equivalentes = set()
        equivalentes.add(descritor)
        
        for codigo, relacao in self.mapeamento.items():
            # Buscar por CNCA
            if tipo == "cnca" and relacao.get("cnca") == descritor:
                equivalentes.add(codigo)
                for bncc in relacao.get("bncc", []):
                    equivalentes.add(bncc)
                for saeb in relacao.get("saeb", []):
                    equivalentes.add(saeb)
            
            # Buscar por BNCC
            elif tipo == "bncc" and descritor in relacao.get("bncc", []):
                equivalentes.add(codigo)
                if relacao.get("cnca"):
                    equivalentes.add(relacao["cnca"])
                for saeb in relacao.get("saeb", []):
                    equivalentes.add(saeb)
            
            # Buscar por SAEB
            elif tipo == "saeb" and descritor in relacao.get("saeb", []):
                equivalentes.add(codigo)
                if relacao.get("cnca"):
                    equivalentes.add(relacao["cnca"])
                for bncc in relacao.get("bncc", []):
                    equivalentes.add(bncc)
        
        return equivalentes
    
    def buscar_questoes_por_matriz(self, questoes: List[Dict], 
                                    descritor_selecionado: str, 
                                    tipo_matriz: str) -> List[Dict]:
        """
        Filtra questoes que correspondem ao descritor ou seus equivalentes
        
        Args:
            questoes: Lista de questoes do itens.json
            descritor_selecionado: O descritor escolhido na interface
            tipo_matriz: 'bncc', 'cnca' ou 'saeb'
        
        Returns:
            Lista de questoes filtradas
        """
        if not descritor_selecionado:
            return questoes
        
        # Buscar equivalentes
        equivalentes = self.buscar_equivalentes(descritor_selecionado, tipo_matriz)
        
        # Filtrar questoes
        filtradas = []
        for q in questoes:
            descritor_q = q.get("descritor", "")
            if descritor_q in equivalentes:
                filtradas.append(q)
        
        return filtradas
    
    def obter_descritores_disponiveis(self, tipo: str, questoes: List[Dict]) -> List[str]:
        """
        Retorna lista de descritores disponiveis no banco para um determinado tipo
        
        Args:
            tipo: 'bncc', 'cnca' ou 'saeb'
            questoes: Lista de questoes do itens.json
        
        Returns:
            Lista de descritores disponiveis
        """
        descritores = set()
        
        for q in questoes:
            descritor_q = q.get("descritor", "")
            for codigo, relacao in self.mapeamento.items():
                if descritor_q == codigo:
                    if tipo == "bncc":
                        for bncc in relacao.get("bncc", []):
                            descritores.add(bncc)
                    elif tipo == "cnca" and relacao.get("cnca"):
                        descritores.add(relacao["cnca"])
                    elif tipo == "saeb":
                        for saeb in relacao.get("saeb", []):
                            descritores.add(saeb)
        
        return sorted(list(descritores))


if __name__ == "__main__":
    print("Testando MapeadorMatrizes...")
    mapeador = MapeadorMatrizes()
    
    print("Mapeador carregado com sucesso!")
    print(f"Total de descritores mapeados: {len(mapeador.mapeamento)}")
