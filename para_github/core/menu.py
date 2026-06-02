"""
Menu Principal do LADOS 2.0
Integra navbar e sidebar
"""

import streamlit as st
from core.navbar import render_navbar
from core.sidebar import render_sidebar


def renderizar_menu(usuario: dict):
    """
    Renderiza o menu completo (navbar + sidebar)
    """
    # Renderizar navbar (horizontal)
    render_navbar(usuario)
    
    # Renderizar sidebar (colapsável)
    render_sidebar(usuario)
