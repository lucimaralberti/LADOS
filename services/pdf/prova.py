"""
Gerador de PDF da Prova - LADOS 2.0
"""

import os
import uuid
import hashlib
import qrcode
from io import BytesIO
import base64
from datetime import datetime
from typing import List, Dict
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
from reportlab.lib.colors import black, white, grey, HexColor
from reportlab.pdfgen import canvas
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib.utils import ImageReader

try:
    pdfmetrics.registerFont(TTFont('Arial', 'arial.ttf'))
except:
    pass


class GeradorProva:
    """
    Gera PDF da prova
    """
    
    def __init__(self):
        self.page_width, self.page_height = A4
        self.margin_left = 10 * mm
        self.margin_right = 10 * mm
        self.margin_top = 10 * mm
        self.margin_bottom = 15 * mm
        self.content_width = self.page_width - self.margin_left - self.margin_right
    
    def gerar_exam_id(self, turma: str) -> str:
        data_str = datetime.now().strftime("%Y%m%d")
        random_sufix = str(uuid.uuid4())[:6].upper()
        turma_clean = turma.replace(" ", "").upper()[:6]
        return f"PROV_{turma_clean}_{data_str}_{random_sufix}"
    
    def gerar_qrcode(self, exam_id: str, turma: str, data: str) -> ImageReader:
        qr_data = f"{exam_id}|{turma}|{data}"
        qr = qrcode.QRCode(version=1, box_size=4, border=1)
        qr.add_data(qr_data)
        qr.make(fit=True)
        img = qr.make_image(fill_color="black", back_color="white")
        buffered = BytesIO()
        img.save(buffered, format="PNG")
        buffered.seek(0)
        return ImageReader(buffered)
    
    def gerar_pdf(self, escola: str, turma: str, ano: str, disciplina: str, 
                  professor: str, questoes: List[Dict], qtd_questoes: int, 
                  output_path: str, eh_simulado: bool = False):
        
        exam_id = self.gerar_exam_id(turma)
        data_atual = datetime.now().strftime("%d/%m/%Y")
        qr_image = self.gerar_qrcode(exam_id, turma, data_atual)
        
        c = canvas.Canvas(output_path, pagesize=A4)
        
        if eh_simulado:
            titulo = f"SIMULADO - {ano} - {turma}"
        else:
            titulo = f"PROVA DE {disciplina.upper()} - {ano} - {turma}"
        
        y = self.page_height - self.margin_top
        
        # Cabeçalho
        c.setFont('Helvetica-Bold', 14)
        c.drawCentredString(self.page_width/2, y, escola.upper())
        y -= 8*mm
        
        c.setFont('Helvetica', 12)
        c.drawCentredString(self.page_width/2, y, titulo)
        y -= 12*mm
        
        # Nome
        c.setFont('Helvetica', 11)
        c.drawString(self.margin_left, y, "Nome: _________________________________")
        y -= 8*mm
        
        # Professor e data
        c.drawString(self.margin_left, y, f"Professor(a): {professor}")
        c.drawRightString(self.page_width - self.margin_right, y, f"Data: {data_atual}")
        y -= 12*mm
        
        # Instruções
        c.setFont('Helvetica-Bold', 10)
        c.drawString(self.margin_left, y, "INSTRUÇÕES:")
        y -= 5*mm
        c.setFont('Helvetica', 9)
        instrucoes = [
            "1. Leia cada questão com atenção.",
            "2. Marque apenas uma alternativa.",
            "3. Preencha o círculo completamente.",
            "4. Use caneta azul ou preta."
        ]
        for instr in instrucoes:
            c.drawString(self.margin_left + 5*mm, y, instr)
            y -= 5*mm
        
        y -= 5*mm
        
        # QR Code
        qr_size = 25*mm
        c.drawImage(qr_image, self.page_width - self.margin_right - qr_size, y - qr_size, 
                   width=qr_size, height=qr_size)
        
        # Grade de respostas
        y -= 30*mm
        c.setFont('Helvetica-Bold', 11)
        c.drawCentredString(self.page_width/2, y, "GRADE DE RESPOSTAS")
        y -= 8*mm
        
        # Desenhar grade simplificada
        col_width = (self.content_width - 15*mm) / qtd_questoes
        row_height = 8*mm
        
        # Cabeçalho
        x = self.margin_left
        c.rect(x, y - row_height, 15*mm, row_height)
        c.drawCentredString(x + 7.5*mm, y - row_height/2 - 2*mm, "Q")
        x += 15*mm
        for i in range(1, qtd_questoes + 1):
            c.rect(x, y - row_height, col_width, row_height)
            c.drawCentredString(x + col_width/2, y - row_height/2 - 2*mm, str(i))
            x += col_width
        y -= row_height
        
        for letra in ['A', 'B', 'C', 'D']:
            x = self.margin_left
            c.rect(x, y - row_height, 15*mm, row_height)
            c.drawCentredString(x + 7.5*mm, y - row_height/2 - 2*mm, letra)
            x += 15*mm
            for i in range(1, qtd_questoes + 1):
                c.rect(x, y - row_height, col_width, row_height)
                c.circle(x + col_width/2, y - row_height/2, 3*mm, stroke=1, fill=0)
                x += col_width
            y -= row_height
        
        # Pular para próxima página
        c.showPage()
        y = self.page_height - self.margin_top
        
        # Questões
        for idx, q in enumerate(questoes, 1):
            if y < 40*mm:
                c.showPage()
                y = self.page_height - self.margin_top
            
            c.setFont('Helvetica-Bold', 11)
            c.drawString(self.margin_left, y, f"{idx}) {q.get('enunciado', '')}")
            y -= 6*mm
            
            c.setFont('Helvetica', 10)
            for alt in q.get('alternativas', []):
                if isinstance(alt, tuple):
                    letra, texto = alt
                else:
                    letra = alt.get('letra', '')
                    texto = alt.get('texto', '')
                c.drawString(self.margin_left + 5*mm, y, f"{letra}) {texto}")
                y -= 5*mm
            y -= 5*mm
        
        # Rodapé
        c.setFont('Helvetica', 8)
        c.setFillColor(grey)
        c.drawCentredString(self.page_width/2, self.margin_bottom - 5*mm, 
                           f"SISTEMA LADOS - 2026 | ID: {exam_id}")
        
        c.save()
        print(f"✅ Prova gerada: {output_path}")
        return True
