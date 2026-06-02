import json
import os
from typing import List, Dict, Any
import streamlit as st

class DescritoresService:
    """Serviço para gerenciar descritores/habilidades dos arquivos JSON"""
    
    def __init__(self):
        current_dir = os.path.dirname(os.path.abspath(__file__))
        self.data_path = os.path.join(os.path.dirname(current_dir), 'data')
        self.cache = {}
    
    def _load_json(self, filename: str) -> Dict:
        if filename in self.cache:
            return self.cache[filename]
        
        filepath = os.path.join(self.data_path, filename)
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                data = json.load(f)
                self.cache[filename] = data
                return data
        except Exception as e:
            st.error(f"Erro ao carregar {filename}: {e}")
            return {}
    
    def get_descritores_bncc(self, ano: str, disciplina: str) -> List[Dict]:
        """Busca descritores BNCC - estrutura: bncc.json[Disciplina][ano]"""
        data = self._load_json('bncc.json')
        
        if not data:
            return self._get_mock_descritores("BNCC", ano, disciplina)
        
        descritores = []
        
        # Mapeia ano (1º -> "1º", 5º -> "5º")
        ano_key = ano.replace("º Ano", "º") if "º" in ano else ano
        
        # Procura pela disciplina
        for disciplina_key, anos_data in data.items():
            if disciplina.lower() in disciplina_key.lower():
                if ano_key in anos_data:
                    for item in anos_data[ano_key]:
                        descritores.append({
                            "codigo": item.get("codigo", ""),
                            "descricao": item.get("habilidade", item.get("descricao", "")),
                            "disciplina": disciplina
                        })
        
        return descritores if descritores else self._get_mock_descritores("BNCC", ano, disciplina)
    
    def get_descritores_cnca(self, ano: str, disciplina: str) -> List[Dict]:
        """Busca descritores CNCA - estrutura: cnca.json[CodigoAno][Disciplina]"""
        data = self._load_json('cnca.json')
        
        if not data:
            return self._get_mock_descritores("CNCA", ano, disciplina)
        
        descritores = []
        
        # Mapeia ano: 1º Ano -> "1EF"
        ano_map = {
            "1º Ano": "1EF", "2º Ano": "2EF", "3º Ano": "3EF",
            "4º Ano": "4EF", "5º Ano": "5EF"
        }
        ano_key = ano_map.get(ano, ano.replace("º Ano", "EF"))
        
        if ano_key in data:
            if disciplina in data[ano_key]:
                for item in data[ano_key][disciplina]:
                    descritores.append({
                        "codigo": item.get("codigo", ""),
                        "descricao": item.get("habilidade", ""),
                        "disciplina": disciplina,
                        "tipo": item.get("tipo", "central")
                    })
        
        return descritores if descritores else self._get_mock_descritores("CNCA", ano, disciplina)
    
    def get_descritores_saeb(self, ano: str, disciplina: str) -> List[Dict]:
        """Busca descritores SAEB - estrutura: saeb.json[CodigoAno][Disciplina]"""
        data = self._load_json('saeb.json')
        
        if not data:
            return self._get_mock_descritores("SAEB", ano, disciplina)
        
        descritores = []
        
        # Mapeia ano: 2º Ano -> "2EF", 5º Ano -> "5EF"
        ano_map = {"2º Ano": "2EF", "5º Ano": "5EF"}
        ano_key = ano_map.get(ano, "")
        
        # Para outros anos, tenta buscar
        if not ano_key:
            for key in data.keys():
                if ano[0] in key:
                    ano_key = key
                    break
        
        if ano_key and ano_key in data:
            # Ajusta disciplina: "Língua Portuguesa" ou "Português"
            disc_key = "Língua Portuguesa" if "Português" in disciplina else disciplina
            if disc_key in data[ano_key]:
                for item in data[ano_key][disc_key]:
                    descritores.append({
                        "codigo": item.get("codigo", ""),
                        "descricao": item.get("habilidade", ""),
                        "disciplina": disciplina,
                        "eixo": item.get("eixo", "")
                    })
        
        return descritores if descritores else self._get_mock_descritores("SAEB", ano, disciplina)
    
    def get_descritores_matriz_unificada(self, ano: str, disciplina: str) -> List[Dict]:
        """Busca descritores da matriz unificada"""
        data = self._load_json('matriz_unificada.json')
        
        if not data:
            return self._get_mock_descritores("MATRIZ", ano, disciplina)
        
        descritores = []
        matrizes = data.get("matrizes", {})
        
        for key, value in matrizes.items():
            if isinstance(value, dict):
                if "habilidade" in value:
                    descritores.append({
                        "codigo": key,
                        "descricao": value.get("habilidade", ""),
                        "disciplina": disciplina,
                        "ut": value.get("ut", "")
                    })
        
        return descritores if descritores else self._get_mock_descritores("MATRIZ", ano, disciplina)
    
    def get_descritores_by_item(self, item: str, ano: str, disciplina: str) -> List[Dict]:
        """Método principal - busca descritores baseado no item selecionado"""
        if item == "BNCC":
            return self.get_descritores_bncc(ano, disciplina)
        elif item == "CNCA":
            return self.get_descritores_cnca(ano, disciplina)
        elif item == "SAEB":
            return self.get_descritores_saeb(ano, disciplina)
        else:
            return self.get_descritores_matriz_unificada(ano, disciplina)
    
    def get_anos_disponiveis(self) -> List[str]:
        return ["1º Ano", "2º Ano", "3º Ano", "4º Ano", "5º Ano", 
                "6º Ano", "7º Ano", "8º Ano", "9º Ano"]
    
    def get_disciplinas_by_ano(self, ano: str) -> List[str]:
        if not ano:
            return ["Português", "Matemática"]
        try:
            ano_num = int(ano[0])
        except:
            ano_num = 0
        
        if ano_num <= 4:
            return ["Português", "Matemática"]
        else:
            return ["Ciências", "Geografia", "História", "Matemática", "Português"]
    
    def get_itens_by_ano(self, ano: str) -> List[str]:
        if not ano:
            return ["BNCC", "CNCA"]
        try:
            ano_num = int(ano[0])
        except:
            ano_num = 0
        
        if ano_num == 1 or ano_num == 3 or ano_num == 4:
            return ["BNCC", "CNCA"]
        elif ano_num == 2 or ano_num == 5:
            return ["BNCC", "CNCA", "SAEB"]
        else:
            return ["BNCC", "SAEB"]
    
    def _get_mock_descritores(self, item: str, ano: str, disciplina: str) -> List[Dict]:
        ano_num = ano[0] if ano else "0"
        disc_abrev = disciplina[:3].upper() if disciplina else "GER"
        return [
            {"codigo": f"{item}_{ano_num}{disc_abrev}_001", 
             "descricao": f"Descritor 1 - Habilidade de {disciplina} para {ano} - {item}",
             "disciplina": disciplina},
            {"codigo": f"{item}_{ano_num}{disc_abrev}_002", 
             "descricao": f"Descritor 2 - Habilidade de {disciplina} para {ano} - {item}",
             "disciplina": disciplina},
        ]


descritores_service = DescritoresService()
