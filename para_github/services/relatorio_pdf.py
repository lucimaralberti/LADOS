from pathlib import Path
from datetime import datetime
from typing import List, Dict
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm
from utils.logger import get_logger

logger = get_logger(__name__)

class GeradorRelatorioPDF:
    def __init__(self, output_dir: str = "relatorios"):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)
        self.styles = getSampleStyleSheet()
    
    def gerar_relatorio_turma_completo(self, turma_nome: str, diagnostico: Dict) -> str:
        """Gera relatório PDF completo com todas as análises integradas"""
        data_str = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = self.output_dir / f"relatorio_completo_{turma_nome}_{data_str}.pdf"
        
        doc = SimpleDocTemplate(str(filename), pagesize=A4)
        elementos = []
        
        # Título
        elementos.append(Paragraph(f"Relatório Pedagógico Completo", self.styles["Title"]))
        elementos.append(Paragraph(f"Turma: {turma_nome}", self.styles["Heading1"]))
        elementos.append(Spacer(1, 0.3 * cm))
        
        # Data e metadados
        elementos.append(Paragraph(f"Data de emissão: {datetime.now().strftime('%d/%m/%Y %H:%M')}", self.styles["Normal"]))
        elementos.append(Spacer(1, 0.5 * cm))
        
        # ===== RESULTADOS GERAIS =====
        elementos.append(Paragraph("1. Resultados Gerais", self.styles["Heading2"]))
        
        media = diagnostico.get("media_geral", 0)
        nivel = diagnostico.get("nivel", "Indeterminado")
        total_avaliacoes = diagnostico.get("total_avaliacoes", 0)
        
        tabela_geral = [
            ["Indicador", "Valor"],
            ["Média Geral de Acertos", f"{media:.1f}%"],
            ["Nível de Proficiência", nivel],
            ["Total de Avaliações", str(total_avaliacoes)]
        ]
        
        if diagnostico.get("descricao_nivel"):
            elementos.append(Paragraph(f"<i>{diagnostico['descricao_nivel']}</i>", self.styles["Normal"]))
            elementos.append(Spacer(1, 0.2 * cm))
        
        tabela = Table(tabela_geral, colWidths=[8*cm, 6*cm])
        tabela.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (1, 0), colors.grey),
            ("TEXTCOLOR", (0, 0), (1, 0), colors.whitesmoke),
            ("ALIGN", (0, 0), (1, 0), "CENTER"),
            ("GRID", (0, 0), (1, -1), 1, colors.black),
        ]))
        elementos.append(tabela)
        elementos.append(Spacer(1, 0.5 * cm))
        
        # ===== DESEMPENHO POR DESCRITOR =====
        elementos.append(Paragraph("2. Desempenho por Descritor", self.styles["Heading2"]))
        
        por_descriptor = diagnostico.get("por_descriptor", {})
        if por_descriptor:
            tabela_desc = [["Descritor", "Acertos", "Total", "%", "Nível"]]
            for desc, dados in list(por_descriptor.items())[:10]:
                if hasattr(dados, 'acertos'):
                    tabela_desc.append([
                        desc, str(dados.acertos), str(dados.total), 
                        f"{dados.percentual_acerto:.0f}%", dados.nivel
                    ])
                elif isinstance(dados, dict):
                    tabela_desc.append([
                        desc, str(dados.get("acertos", 0)), str(dados.get("total", 0)),
                        f"{dados.get('percentual_acerto', 0):.0f}%", dados.get("nivel", "")
                    ])
            
            tabela_descs = Table(tabela_desc, colWidths=[2.5*cm, 1.5*cm, 1.5*cm, 1.5*cm, 2.5*cm])
            tabela_descs.setStyle(TableStyle([
                ("BACKGROUND", (0, 0), (-1, 0), colors.grey),
                ("TEXTCOLOR", (0, 0), (-1, 0), colors.whitesmoke),
                ("ALIGN", (0, 0), (-1, 0), "CENTER"),
                ("GRID", (0, 0), (-1, -1), 0.5, colors.black),
                ("FONTSIZE", (0, 0), (-1, -1), 8),
            ]))
            elementos.append(tabela_descs)
        else:
            elementos.append(Paragraph("Nenhum dado de descritor disponível.", self.styles["Normal"]))
        
        elementos.append(Spacer(1, 0.5 * cm))
        
        # ===== PERFIL BLOOM =====
        perfil_bloom = diagnostico.get("perfil_bloom", {})
        if perfil_bloom:
            elementos.append(Paragraph("3. Perfil Cognitivo (Taxonomia de Bloom)", self.styles["Heading2"]))
            
            tabela_bloom = [["Nível", "Total", "Acertos", "%"]]
            for nivel, dados in perfil_bloom.items():
                if isinstance(dados, dict):
                    tabela_bloom.append([
                        nivel, str(dados.get("total", 0)), str(dados.get("acertos", 0)),
                        f"{dados.get('percentual', 0):.0f}%"
                    ])
            
            tabela_bloom_obj = Table(tabela_bloom, colWidths=[3*cm, 2*cm, 2*cm, 2*cm])
            tabela_bloom_obj.setStyle(TableStyle([
                ("BACKGROUND", (0, 0), (-1, 0), colors.grey),
                ("TEXTCOLOR", (0, 0), (-1, 0), colors.whitesmoke),
                ("ALIGN", (0, 0), (-1, 0), "CENTER"),
                ("GRID", (0, 0), (-1, -1), 0.5, colors.black),
            ]))
            elementos.append(tabela_bloom_obj)
            elementos.append(Spacer(1, 0.3 * cm))
        
        # ===== RECOMENDAÇÕES =====
        recomendacoes = diagnostico.get("recomendacoes", [])
        if recomendacoes:
            elementos.append(Paragraph("4. Recomendações Pedagógicas", self.styles["Heading2"]))
            for rec in recomendacoes[:4]:
                titulo = rec.get("titulo", rec.get("tipo_erro", "Recomendação"))
                elementos.append(Paragraph(f"<b>• {titulo}</b>", self.styles["Normal"]))
                if "acoes" in rec:
                    for acao in rec["acoes"][:2]:
                        elementos.append(Paragraph(f"   - {acao}", self.styles["Normal"]))
                elementos.append(Spacer(1, 0.1 * cm))
        
        # ===== TRILHA DE RECUPERAÇÃO =====
        trilha = diagnostico.get("trilha_recuperacao", [])
        if trilha:
            elementos.append(Paragraph("5. Trilha de Recuperação Sugerida", self.styles["Heading2"]))
            for i, etapa in enumerate(trilha[:5], 1):
                elementos.append(Paragraph(f"{i}. {etapa}", self.styles["Normal"]))
        
        doc.build(elementos)
        logger.info(f"Relatório completo gerado: {filename}")
        return str(filename)
