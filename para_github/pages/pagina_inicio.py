import streamlit as st
import json
from pathlib import Path
from datetime import datetime
from core.auth import get_current_user

def show():
    usuario = get_current_user()
    
    # Função segura para carregar JSON
    def carregar_json(caminho):
        try:
            if not Path(caminho).exists():
                return []
            with open(caminho, "r", encoding="utf-8-sig") as f:
                conteudo = f.read().strip()
                if not conteudo:
                    return []
                return json.loads(conteudo)
        except Exception as e:
            return []
    
    # Carregar dados
    turmas = carregar_json("data/turmas.json")
    resultados = carregar_json("data/resultados.json")
    
    total_turmas = len(turmas)
    provas_aplicadas = len(resultados)
    
    # Calcular média geral
    notas = []
    for r in resultados:
        if isinstance(r, dict):
            if "percentual_acerto" in r:
                notas.append(r["percentual_acerto"])
            elif "nota" in r:
                notas.append(r["nota"])
    media_geral = round(sum(notas) / len(notas), 1) if notas else 68.5
    
    saldo_restante = 20
    
    # ============================================
    # CSS GLOBAL - Espaçamento igual em todas as direções (16px)
    # ============================================
    st.markdown("""
    <style>
        /* Espaçamento horizontal entre colunas */
        [data-testid="stHorizontalBlock"] {
            gap: 16px !important;
        }
        
        /* Espaçamento vertical entre linhas */
        .row-spacing {
            margin-bottom: 16px !important;
        }
        
        /* Estilo dos cards */
        .card {
            border-radius: 20px;
            padding: 1.2rem 1rem;
            text-align: center;
            box-shadow: 0 2px 8px rgba(0,0,0,0.06);
            transition: transform 0.2s, box-shadow 0.2s;
            height: 100%;
            display: flex;
            flex-direction: column;
            justify-content: center;
        }
        .card:hover {
            transform: translateY(-3px);
            box-shadow: 0 6px 16px rgba(0,0,0,0.1);
        }
        .card-value {
            font-size: 2.5rem;
            font-weight: 800;
            margin: 0.25rem 0;
            line-height: 1.2;
        }
        .card-value-large {
            font-size: 3rem;
            font-weight: 800;
            margin: 0.25rem 0;
            line-height: 1.2;
        }
        .card-label {
            font-size: 0.7rem;
            font-weight: 700;
            text-transform: uppercase;
            letter-spacing: 1px;
            margin-bottom: 0.5rem;
        }
        .card-desc {
            font-size: 0.7rem;
            opacity: 0.85;
            margin-top: 0.25rem;
        }
        .card-desc-dark {
            font-size: 0.7rem;
            color: #555;
            margin-top: 0.25rem;
        }
        .card-desc-dark strong {
            display: block;
            font-size: 0.8rem;
            margin-bottom: 0.25rem;
        }
        .card-footer {
            font-size: 0.65rem;
            margin-top: 0.75rem;
            padding-top: 0.5rem;
            border-top: 1px solid rgba(0,0,0,0.08);
            font-weight: 500;
        }
        @media (max-width: 768px) {
            [data-testid="stHorizontalBlock"] {
                gap: 12px !important;
            }
        }
    </style>
    """, unsafe_allow_html=True)
    
    # Título
    st.title("📊 Início")
    st.caption(f"{datetime.now().strftime('%d/%m/%Y %H:%M')}")
    
    # ============================================
    # LINHA 1 - TRÊS PRIMEIROS CARDS
    # ============================================
    
    col1, col2, col3 = st.columns(3, gap="small")
    
    with col1:
        st.markdown(f'''
        <div class="card" style="background: #2B4C7E; color: white;">
            <div class="card-label">SUAS TURMAS</div>
            <div class="card-value-large">{total_turmas:02d}</div>
            <div class="card-desc">Turmas que estou avaliando</div>
        </div>
        ''', unsafe_allow_html=True)
    
    with col2:
        st.markdown(f'''
        <div class="card" style="background: #3A609E; color: white;">
            <div class="card-label">PROVAS APLICADAS</div>
            <div class="card-value-large">{provas_aplicadas:02d}</div>
            <div class="card-desc">Volume de trabalho executado</div>
        </div>
        ''', unsafe_allow_html=True)
    
    with col3:
        st.markdown(f'''
        <div class="card" style="background: #00A8B5; color: white;">
            <div class="card-label">SALDO RESTANTE</div>
            <div class="card-value-large">{saldo_restante}</div>
            <div class="card-desc">Capacidade operacional disponível</div>
        </div>
        ''', unsafe_allow_html=True)
    
    # ============================================
    # ESPAÇAMENTO VERTICAL (16px - mesmo valor do gap)
    # ============================================
    st.markdown('<div class="row-spacing"></div>', unsafe_allow_html=True)
    
    # ============================================
    # LINHA 2 - TRÊS ÚLTIMOS CARDS
    # ============================================
    
    col4, col5, col6 = st.columns(3, gap="small")
    
    media_int = int(media_geral)
    
    with col4:
        st.markdown(f'''
        <div class="card" style="background: white; border: 1px solid #e8e8e8;">
            <div class="card-label" style="color: #666;">MÉDIA GERAL</div>
            <div class="card-value-large" style="color: #F5A623;">{media_int}%</div>
            <div class="card-desc-dark">Atenção: está logo abaixo da meta de 70%</div>
        </div>
        ''', unsafe_allow_html=True)
    
    with col5:
        st.markdown(f'''
        <div class="card" style="background: white; border: 1px solid #e8e8e8;">
            <div class="card-label" style="color: #666;">PIOR DESCRITOR</div>
            <div class="card-value" style="color: #E05656;">32%</div>
            <div class="card-desc-dark">
                <strong>EF01LP04</strong>
                Distinguir letras do alfabeto de outros sinais
            </div>
            <div class="card-footer" style="color: #E05656;">🔴 Crítico: Exige plano de intervenção</div>
        </div>
        ''', unsafe_allow_html=True)
    
    with col6:
        st.markdown(f'''
        <div class="card" style="background: white; border: 1px solid #e8e8e8;">
            <div class="card-label" style="color: #666;">MELHOR DESCRITOR</div>
            <div class="card-value" style="color: #2E8B57;">88%</div>
            <div class="card-desc-dark">
                <strong>EF01LP04</strong>
                Distinguir letras do alfabeto de outros sinais
            </div>
            <div class="card-footer" style="color: #2E8B57;">✅ Adequado: Habilidade consolidada</div>
        </div>
        ''', unsafe_allow_html=True)
    
    # Linha divisória
    st.markdown("---")
    
    # Ações rápidas
    st.subheader("🚀 Acesso Rápido")
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("📝 Gerar Prova", use_container_width=True):
            st.query_params["page"] = "questoes"
            st.rerun()
    
    with col2:
        if st.button("🔍 Corrigir Prova", use_container_width=True):
            st.query_params["page"] = "correcao"
            st.rerun()
    
    with col3:
        if st.button("📊 Ver Relatórios", use_container_width=True):
            st.query_params["page"] = "relatorios"
            st.rerun()

if __name__ == "__main__":
    show()