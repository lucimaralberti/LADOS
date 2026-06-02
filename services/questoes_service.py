import streamlit as st

"""
Serviço de Busca de Questões - LADOS 2.0
"""

import json
import random
import os


@st.cache_data(ttl=3600)
def buscar_questoes(descritores, quantidade):
    """
    Busca questões no banco de itens
    """
    # Carregar itens.json
    caminho = "data/itens.json"
    if not os.path.exists(caminho):
        return []
    
    with open(caminho, 'r', encoding='utf-8') as f:
        dados = json.load(f)
    
    itens = dados.get('itens', [])
    
    # Filtrar por descritores
    filtrados = [item for item in itens if item.get('descritor') in descritores]
    
    # Sortear aleatoriamente
    if len(filtrados) < quantidade:
        quantidade = len(filtrados)
    
    selecionados = random.sample(filtrados, quantidade) if filtrados else []
    
    return selecionados

