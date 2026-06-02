"""
LAYOUT PADRÃO - LADOS 2.0
Versão estável e funcional
"""

import streamlit as st

def configurar_pagina(titulo: str, icone: str = "📚"):
    """Configuração padrão de todas as páginas"""
    st.set_page_config(
        page_title=f"LADOS 2.0 - {titulo}",
        page_icon=icone,
        layout="wide",
        initial_sidebar_state="expanded"
    )
    
    # CSS para melhorar a aparência
    st.markdown("""
        <style>
        /* Cabeçalho */
        .main-header {
            background: linear-gradient(135deg, #1e3c72 0%, #2a5298 100%);
            padding: 1rem;
            border-radius: 10px;
            margin-bottom: 2rem;
            color: white;
            text-align: center;
        }
        .main-header h1 {
            margin: 0;
            font-size: 2rem;
        }
        .main-header p {
            margin: 0;
            opacity: 0.9;
        }
        
        /* Cards */
        .card {
            background: #f8f9fa;
            border-radius: 10px;
            padding: 1.5rem;
            margin: 1rem 0;
            border: 1px solid #e9ecef;
        }
        
        /* Botões */
        .stButton > button {
            background: linear-gradient(135deg, #1e3c72 0%, #2a5298 100%);
            color: white;
            border: none;
            border-radius: 5px;
            transition: all 0.3s ease;
        }
        .stButton > button:hover {
            transform: translateY(-2px);
            box-shadow: 0 4px 12px rgba(0,0,0,0.15);
        }
        </style>
    """, unsafe_allow_html=True)

def mostrar_cabecalho(titulo: str, subtitulo: str = ""):
    """Mostra o cabeçalho padronizado"""
    if subtitulo:
        html = f'<div class="main-header"><h1>{titulo}</h1><p>{subtitulo}</p></div>'
    else:
        html = f'<div class="main-header"><h1>{titulo}</h1></div>'
    st.markdown(html, unsafe_allow_html=True)

def alerta_sucesso(mensagem: str):
    """Alerta de sucesso"""
    st.success(f"✅ {mensagem}")

def alerta_erro(mensagem: str):
    """Alerta de erro"""
    st.error(f"❌ {mensagem}")

def alerta_info(mensagem: str):
    """Alerta informativo"""
    st.info(f"ℹ️ {mensagem}")
