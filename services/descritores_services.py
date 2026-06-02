import json
import os
from typing import List, Dict, Any
import streamlit as st

class DescritoresService:
    """Serviço para gerenciar descritores/habilidades dos arquivos JSON"""
    
    def __init__(self):
        self.data_path = os.path.join(os.path.dirname(__file__), '..', 'data')
        self.cache = {}
    
    def _load_json(self, filename: str) -> Dict:
        """Carrega um arquivo JSON com cache"""
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
        """Busca descritores BNCC por ano e disciplina"""
        data = self._load_json('bncc.json')
        
        # Navega pela estrutura do JSON
        # Exemplo de estrutura esperada: bncc.json[ano][disciplina]
        try:
            if ano in data and disciplina in data[ano]:
                return data[ano][disciplina]
        except:
            pass
        
        # Fallback: busca em toda a estrutura
        descritores = []
        for key, value in data.items():
            if isinstance(value, dict):
                if ano in str(key) or disciplina in str(key):
                    descritores.append({"codigo": key, "descricao": str(value)})
        
        return descritores if descritores else self._get_mock_descritores("BNCC", ano, disciplina)
    
    def get_descritores_cnca(self, ano: str, disciplina: str) -> List[Dict]:
        """Busca descritores CNCA por ano e disciplina"""
        data = self._load_json('cnca.json')
        
        try:
            if ano in data and disciplina in data[ano]:
                return data[ano][disciplina]
        except:
            pass
        
        return self._get_mock_descritores("CNCA", ano, disciplina)
    
    def get_descritores_saeb(self, ano: str, disciplina: str) -> List[Dict]:
        """Busca descritores SAEB por ano e disciplina"""
        data = self._load_json('saeb.json')
        
        try:
            if ano in data and disciplina in data[ano]:
                return data[ano][disciplina]
        except:
            pass
        
        return self._get_mock_descritores("SAEB", ano, disciplina)
    
    def get_descritores_matriz_unificada(self, ano: str, disciplina: str, item: str) -> List[Dict]:
        """Busca descritores da matriz unificada"""
        data = self._load_json('matriz_unificada.json')
        
        descritores = []
        for key, value in data.items():
            if isinstance(value, dict):
                if item in str(key) or ano in str(key) or disciplina in str(key):
                    if "codigo" in value and "descricao" in value:
                        descritores.append(value)
                    elif isinstance(value, list):
                        descritores.extend(value)
        
        return descritores if descritores else self._get_mock_descritores(item, ano, disciplina)
    
    def get_descritores_by_item(self, item: str, ano: str, disciplina: str) -> List[Dict]:
        """Método principal - busca descritores baseado no item selecionado"""
        if item == "BNCC":
            return self.get_descritores_bncc(ano, disciplina)
        elif item == "CNCA":
            return self.get_descritores_cnca(ano, disciplina)
        elif item == "SAEB":
            return self.get_descritores_saeb(ano, disciplina)
        else:
            return self.get_descritores_matriz_unificada(ano, disciplina, item)
    
    def get_anos_disponiveis(self) -> List[str]:
        """Retorna anos escolares disponíveis nos arquivos"""
        anos = ["1º Ano", "2º Ano", "3º Ano", "4º Ano", "5º Ano", 
                "6º Ano", "7º Ano", "8º Ano", "9º Ano"]
        return anos
    
    def get_disciplinas_by_ano(self, ano: str) -> List[str]:
        """Retorna disciplinas disponíveis por ano escolar"""
        ano_num = int(ano[0])
        
        if ano_num <= 4:
            return ["Português", "Matemática"]
        else:
            return ["Ciências", "Geografia", "História", "Matemática", "Português"]
    
    def get_itens_by_ano(self, ano: str) -> List[str]:
        """Retorna itens disponíveis por ano escolar"""
        ano_num = int(ano[0])
        
        if ano_num == 1 or ano_num == 3 or ano_num == 4:
            return ["BNCC", "CNCA"]
        elif ano_num == 2 or ano_num == 5:
            return ["BNCC", "CNCA", "SAEB"]
        else:  # 6º ao 9º ano
            return ["BNCC", "SAEB"]
    
    def _get_mock_descritores(self, item: str, ano: str, disciplina: str) -> List[Dict]:
        """Retorna descritores mockados para fallback"""
        return [
            {"codigo": f"{item}_{ano[0]}{disciplina[:3].upper()}_001", 
             "descricao": f"Descritor 1 - Habilidade específica de {disciplina} para {ano} alinhada ao {item}"},
            {"codigo": f"{item}_{ano[0]}{disciplina[:3].upper()}_002", 
             "descricao": f"Descritor 2 - Habilidade específica de {disciplina} para {ano} alinhada ao {item}"},
            {"codigo": f"{item}_{ano[0]}{disciplina[:3].upper()}_003", 
             "descricao": f"Descritor 3 - Habilidade específica de {disciplina} para {ano} alinhada ao {item}"},
        ]


# Instância global
descritores_service = DescritoresService()