"""
Gerador de Gabarito - LADOS 2.0
"""

from datetime import datetime
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
from reportlab.lib.colors import black, grey, green, red
from reportlab.pdfgen import canvas


class GeradorGabarito:
    """
    Gera PDF do gabarito com justificativas
    """
    
    def __init__(self):
        self.page_width, self.page_height = A4
        self.margin_left = 10 * mm
        self.margin_right = 10 * mm
        self.margin_top = 10 * mm
        self.margin_bottom = 15 * mm
    
    def gerar_pdf(self, escola: str, turma: str, ano: str, disciplina: str,
                  professor: str, questoes: List[Dict], qtd_questoes: int,
                  exam_id: str, output_path: str):
        
        c = canvas.Canvas(output_path, pagesize=A4)
        y = self.page_height - self.margin_top
        
        # Cabeçalho
        c.setFont('Helvetica-Bold', 14)
        c.drawCentredString(self.page_width/2, y, "GABARITO")
        y -= 8*mm
        
        c.setFont('Helvetica', 11)
        c.drawCentredString(self.page_width/2, y, f"{escola.upper()} - {turma}")
        y -= 8*mm
        
        c.drawString(self.margin_left, y, f"Professor(a): {professor}")
        c.drawRightString(self.page_width - self.margin_right, y, f"Data: {datetime.now().strftime('%d/%m/%Y')}")
        y -= 12*mm
        
        # Respostas corretas
        c.setFont('Helvetica-Bold', 11)
        c.drawString(self.margin_left, y, "RESPOSTAS CORRETAS:")
        y -= 6*mm
        
        c.setFont('Helvetica', 10)
        for i, q in enumerate(questoes, 1):
            gabarito = q.get('gabarito', '?')
            c.drawString(self.margin_left + 5*mm, y, f"{i}. {gabarito}")
            y -= 5*mm
        
        y -= 10*mm
        
        # Justificativas
        c.setFont('Helvetica-Bold', 11)
        c.drawString(self.margin_left, y, "JUSTIFICATIVAS:")
        y -= 6*mm
        
        c.setFont('Helvetica', 9)
        for i, q in enumerate(questoes, 1):
            if y < 40*mm:
                c.showPage()
                y = self.page_height - self.margin_top
            
            c.setFont('Helvetica-Bold', 10)
            c.drawString(self.margin_left, y, f"{i}. {q.get('enunciado', '')[:60]}...")
            y -= 5*mm
            
            c.setFont('Helvetica', 9)
            c.drawString(self.margin_left + 5*mm, y, f"Resposta correta: {q.get('gabarito', '?')}")
            y -= 5*mm
            c.drawString(self.margin_left + 5*mm, y, f"Justificativa: {q.get('justificativa_correta', '')}")
            y -= 8*mm
        
        c.save()
        print(f"✅ Gabarito gerado: {output_path}")
        return True
