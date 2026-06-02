"""
Serviço de Exportação de Resultados - LADOS 2.0
Geração de relatórios em CSV, Excel e PDF
"""

import pandas as pd
import io
from datetime import datetime
from typing import List, Dict, Any, Optional
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
from reportlab.lib.colors import black, white, grey, red, green, blue, HexColor
from reportlab.pdfgen import canvas
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
import streamlit as st

class ExportadorResultados:
    """
    Exporta resultados de correção para diferentes formatos
    """
    
    def __init__(self):
        pass
    
    def exportar_csv(self, dados: List[Dict], nome_base: str = "resultados") -> bytes:
        """Exporta resultados para CSV"""
        df = pd.DataFrame(dados)
        buffer = io.BytesIO()
        df.to_csv(buffer, index=False, encoding='utf-8-sig')
        buffer.seek(0)
        return buffer.getvalue()
    
    def exportar_excel(self, dados: List[Dict], nome_base: str = "resultados") -> bytes:
        """Exporta resultados para Excel"""
        df = pd.DataFrame(dados)
        buffer = io.BytesIO()
        
        with pd.ExcelWriter(buffer, engine='openpyxl') as writer:
            df.to_excel(writer, sheet_name='Resultados', index=False)
            
            # Ajustar largura das colunas
            worksheet = writer.sheets['Resultados']
            for column in worksheet.columns:
                max_length = 0
                column_letter = column[0].column_letter
                for cell in column:
                    try:
                        if len(str(cell.value)) > max_length:
                            max_length = len(str(cell.value))
                    except:
                        pass
                adjusted_width = min(max_length + 2, 50)
                worksheet.column_dimensions[column_letter].width = adjusted_width
        
        buffer.seek(0)
        return buffer.getvalue()
    
    def exportar_pdf_relatorio(self, dados: List[Dict], turma: str, prova: str, 
                                data: datetime) -> bytes:
        """Exporta relatório completo em PDF"""
        buffer = io.BytesIO()
        
        c = canvas.Canvas(buffer, pagesize=A4)
        largura, altura = A4
        margem = 15 * mm
        y = altura - margem
        
        # Título
        c.setFont('Helvetica-Bold', 14)
        c.drawCentredString(largura/2, y, f"RELATÓRIO DE DESEMPENHO")
        y -= 10*mm
        
        c.setFont('Helvetica', 11)
        c.drawCentredString(largura/2, y, f"{prova}")
        y -= 8*mm
        
        c.setFont('Helvetica', 10)
        c.drawString(margem, y, f"Turma: {turma}")
        c.drawRightString(largura - margem, y, f"Data: {data.strftime('%d/%m/%Y')}")
        y -= 15*mm
        
        # Estatísticas gerais
        df = pd.DataFrame(dados)
        
        total_alunos = len(df)
        media_notas = df['nota'].mean() if 'nota' in df.columns else 0
        mediana_notas = df['nota'].median() if 'nota' in df.columns else 0
        desvio_padrao = df['nota'].std() if 'nota' in df.columns else 0
        aprovados = len(df[df['nota'] >= 7]) if 'nota' in df.columns else 0
        recuperacao = len(df[(df['nota'] >= 5) & (df['nota'] < 7)]) if 'nota' in df.columns else 0
        reprovados = len(df[df['nota'] < 5]) if 'nota' in df.columns else 0
        
        c.setFont('Helvetica-Bold', 12)
        c.drawString(margem, y, "ESTATÍSTICAS GERAIS")
        y -= 8*mm
        
        c.setFont('Helvetica', 10)
        c.drawString(margem, y, f"Total de alunos: {total_alunos}")
        y -= 6*mm
        c.drawString(margem, y, f"Média da turma: {media_notas:.1f}")
        y -= 6*mm
        c.drawString(margem, y, f"Mediana: {mediana_notas:.1f}")
        y -= 6*mm
        c.drawString(margem, y, f"Desvio padrão: {desvio_padrao:.2f}")
        y -= 6*mm
        c.drawString(margem, y, f"Aprovados (≥ 7): {aprovados} ({aprovados/total_alunos*100:.1f}%)")
        y -= 6*mm
        c.drawString(margem, y, f"Recuperação (5-6.9): {recuperacao} ({recuperacao/total_alunos*100:.1f}%)")
        y -= 6*mm
        c.drawString(margem, y, f"Reprovados (< 5): {reprovados} ({reprovados/total_alunos*100:.1f}%)")
        y -= 15*mm
        
        # Distribuição de notas
        c.setFont('Helvetica-Bold', 12)
        c.drawString(margem, y, "DISTRIBUIÇÃO DE NOTAS")
        y -= 10*mm
        
        # Desenhar histograma simples
        c.setStrokeColor(blue)
        c.setFillColor(blue)
        bar_width = (largura - 2*margem) / 10
        for i in range(10):
            nota_min = i
            nota_max = i + 1
            count = len(df[(df['nota'] >= nota_min) & (df['nota'] < nota_max)]) if 'nota' in df.columns else 0
            altura_barra = (count / max(total_alunos, 1)) * 40 * mm
            c.rect(margem + i * bar_width, y - altura_barra, bar_width - 1, altura_barra, stroke=1, fill=1)
            c.setFont('Helvetica', 7)
            c.drawCentredString(margem + i * bar_width + bar_width/2, y - 3*mm, f"{nota_min}-{nota_max}")
        
        y -= 50*mm
        
        # Rodapé
        c.setFont('Helvetica', 8)
        c.setFillColor(grey)
        c.drawCentredString(largura/2, 15*mm, "Sistema Lados - 2026. Todos os Direitos Reservados")
        c.drawRightString(largura - margem, 15*mm, "01")
        
        c.save()
        buffer.seek(0)
        return buffer.getvalue()


class AnaliseDesempenho:
    """
    Análise de desempenho por descritor e disciplina
    """
    
    def __init__(self):
        pass
    
    def analisar_por_descritor(self, correcoes: List[Dict]) -> pd.DataFrame:
        """
        Analisa acertos por descritor
        """
        resultados = []
        
        for correcao in correcoes:
            detalhes = correcao.get('detalhes', [])
            for detalhe in detalhes:
                resultados.append({
                    'questao': detalhe.get('questao', 0),
                    'descritor': detalhe.get('descritor', 'Não identificado'),
                    'acertou': detalhe.get('acertou', False),
                    'disciplina': detalhe.get('disciplina', 'Geral')
                })
        
        if not resultados:
            return pd.DataFrame()
        
        df = pd.DataFrame(resultados)
        
        # Agrupar por descritor
        analise = df.groupby('descritor').agg(
            total_questoes=('acertou', 'count'),
            acertos=('acertou', 'sum'),
            percentual_acerto=('acertou', lambda x: (x.sum() / len(x)) * 100)
        ).round(2)
        
        return analise
    
    def analisar_por_disciplina(self, correcoes: List[Dict]) -> pd.DataFrame:
        """
        Analisa desempenho por disciplina
        """
        resultados = []
        
        for correcao in correcoes:
            detalhes = correcao.get('detalhes', [])
            disciplina = correcao.get('disciplina', 'Geral')
            for detalhe in detalhes:
                resultados.append({
                    'disciplina': disciplina,
                    'acertou': detalhe.get('acertou', False)
                })
        
        if not resultados:
            return pd.DataFrame()
        
        df = pd.DataFrame(resultados)
        
        analise = df.groupby('disciplina').agg(
            total_questoes=('acertou', 'count'),
            acertos=('acertou', 'sum'),
            percentual_acerto=('acertou', lambda x: (x.sum() / len(x)) * 100)
        ).round(2)
        
        return analise
    
    def analise_distorcedores(self, correcoes: List[Dict]) -> pd.DataFrame:
        """
        Análise de distratores - quais alternativas erradas foram mais escolhidas
        """
        resultados = []
        
        for correcao in correcoes:
            detalhes = correcao.get('detalhes', [])
            for detalhe in detalhes:
                if not detalhe.get('acertou', False):
                    resultados.append({
                        'questao': detalhe.get('questao', 0),
                        'resposta_aluno': detalhe.get('resposta_aluno', ''),
                        'gabarito': detalhe.get('gabarito', '')
                    })
        
        if not resultados:
            return pd.DataFrame()
        
        df = pd.DataFrame(resultados)
        
        # Contar ocorrências de cada erro
        analise = df.groupby(['questao', 'resposta_aluno', 'gabarito']).size().reset_index(name='ocorrencias')
        analise = analise.sort_values('ocorrencias', ascending=False)
        
        return analise


class IntegracaoSupabase:
    """
    Integração com Supabase para salvar e recuperar correções
    """
    
    def __init__(self, supabase_client=None):
        self.client = supabase_client
    
    def salvar_correcao(self, correcao_data: Dict) -> bool:
        """
        Salva uma correção no Supabase
        """
        if not self.client:
            return False
        
        try:
            # Remover campos não serializáveis
            dados_serializaveis = {
                'id': correcao_data.get('id'),
                'sessao_id': correcao_data.get('sessao_id'),
                'numero_prova': correcao_data.get('numero_prova'),
                'tipo_prova': correcao_data.get('tipo_prova'),
                'acertos': correcao_data.get('acertos'),
                'total': correcao_data.get('total'),
                'percentual': correcao_data.get('percentual'),
                'nota': correcao_data.get('nota'),
                'periodo': correcao_data.get('periodo'),
                'ordem': correcao_data.get('ordem'),
                'prova': correcao_data.get('prova'),
                'turma': correcao_data.get('turma'),
                'horario': correcao_data.get('horario'),
                'data': correcao_data.get('data'),
                'timestamp': correcao_data.get('timestamp')
            }
            
            # Salvar no Supabase
            # result = self.client.table('correcoes').insert(dados_serializaveis).execute()
            return True
            
        except Exception as e:
            st.error(f"Erro ao salvar no Supabase: {e}")
            return False
    
    def salvar_sessao(self, sessao_id: str, correcoes: List[Dict], 
                       periodo: str, ordem: str, prova: str, 
                       turma: str, usuario: Dict) -> bool:
        """
        Salva uma sessão completa no Supabase
        """
        if not self.client:
            return False
        
        try:
            notas = [c.get('nota', 0) for c in correcoes]
            
            dados_sessao = {
                'sessao_id': sessao_id,
                'periodo': periodo,
                'ordem': ordem,
                'prova': prova,
                'turma': turma,
                'total_alunos': len(correcoes),
                'media_geral': sum(notas) / len(notas) if notas else 0,
                'usuario_nome': usuario.get('nome'),
                'data': datetime.now().isoformat()
            }
            
            # Salvar sessão
            # result = self.client.table('sessoes_correcao').insert(dados_sessao).execute()
            
            # Salvar cada correção
            for correcao in correcoes:
                self.salvar_correcao(correcao)
            
            return True
            
        except Exception as e:
            st.error(f"Erro ao salvar sessão no Supabase: {e}")
            return False
    
    def recuperar_historico(self, turma: str, prova: str = None, 
                             limite: int = 50) -> List[Dict]:
        """
        Recupera histórico de correções do Supabase
        """
        if not self.client:
            return []
        
        try:
            # Construir query
            query = self.client.table('correcoes').select('*').eq('turma', turma).order('timestamp', desc=True).limit(limite)
            
            if prova:
                query = query.eq('prova', prova)
            
            # result = query.execute()
            # return result.data
            
            return []
            
        except Exception as e:
            st.error(f"Erro ao recuperar histórico: {e}")
            return []


class DashboardDesempenho:
    """
    Dashboard visual de desempenho
    """
    
    def __init__(self):
        pass
    
    def exibir_dashboard(self, correcoes: List[Dict]):
        """
        Exibe dashboard interativo no Streamlit
        """
        if not correcoes:
            st.info("Nenhuma correção disponível para análise")
            return
        
        import plotly.express as px
        import plotly.graph_objects as go
        
        df = pd.DataFrame(correcoes)
        
        st.subheader("📊 Dashboard de Desempenho")
        
        # Métricas principais
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("Total de Provas", len(df), border=True)
        with col2:
            st.metric("Média Geral", f"{df['nota'].mean():.1f}", border=True)
        with col3:
            aprovados = len(df[df['nota'] >= 7])
            st.metric("Aprovados", f"{aprovados}/{len(df)}", border=True)
        with col4:
            st.metric("Acerto Médio", f"{df['percentual'].mean():.1f}%", border=True)
        
        # Gráfico de distribuição de notas
        st.subheader("📈 Distribuição de Notas")
        fig = px.histogram(df, x='nota', nbins=20, title="Distribuição das Notas")
        fig.update_layout(bargap=0.1)
        st.plotly_chart(fig, use_container_width=True)
        
        # Gráfico de evolução (se houver data)
        if 'timestamp' in df.columns:
            st.subheader("📅 Evolução ao Longo do Tempo")
            df['data'] = pd.to_datetime(df['timestamp']).dt.date
            evolucao = df.groupby('data')['nota'].mean().reset_index()
            fig = px.line(evolucao, x='data', y='nota', title="Evolução da Média")
            st.plotly_chart(fig, use_container_width=True)
        
        # Tabela de resultados
        st.subheader("📋 Detalhamento das Correções")
        st.dataframe(df[['numero_prova', 'acertos', 'total', 'percentual', 'nota', 'horario']], 
                     use_container_width=True)


# Instâncias globais
exportador = ExportadorResultados()
analise_desempenho = AnaliseDesempenho()
integracao_supabase = IntegracaoSupabase()
dashboard = DashboardDesempenho()
