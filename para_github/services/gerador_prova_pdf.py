"""
Gerador de PDF da Prova - LADOS 2.0
VERSÃO FINAL - Com quadrados pretos nos cantos
"""

import os
import uuid
import zipfile
import qrcode
import unicodedata

from io import BytesIO
from datetime import datetime
from typing import List, Dict, Optional, Tuple

from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
from reportlab.lib.colors import black, white, grey
from reportlab.pdfgen import canvas
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib.utils import ImageReader


try:
    pdfmetrics.registerFont(TTFont("Arial", "arial.ttf"))
except:
    pass


class GeradorProva:

    def __init__(self):

        self.page_width, self.page_height = A4

        self.margin_left = 12 * mm
        self.margin_right = 12 * mm
        self.margin_top = 15 * mm
        self.margin_bottom = 15 * mm

        self.content_width = (
            self.page_width
            - self.margin_left
            - self.margin_right
        )

        self.num_questoes_fixo = 10

    # =========================================================
    # DESENHOS
    # =========================================================

    def _desenhar_quadrado_preto(self, c, x, y, tamanho=10 * mm):
        """Desenha um quadrado preto sólido de 10x10mm"""
        c.setFillColor(black)
        c.setStrokeColor(black)
        c.rect(x - tamanho/2, y - tamanho/2, tamanho, tamanho, fill=1, stroke=1)

    def _desenhar_circulo(self, c, x, y, diametro=10 * mm):
        raio = diametro / 2
        c.setStrokeColor(black)
        c.setLineWidth(1.3)
        c.circle(x, y, raio, stroke=1, fill=0)

    # =========================================================
    # TEXTO
    # =========================================================

    def _quebrar_texto(self, texto, largura_maxima, fonte="Helvetica", tamanho=10):

        if not texto:
            return []

        palavras = texto.split()
        linhas = []
        linha = ""

        for palavra in palavras:
            teste = f"{linha} {palavra}".strip()
            largura = pdfmetrics.stringWidth(teste, fonte, tamanho)

            if largura <= largura_maxima:
                linha = teste
            else:
                if linha:
                    linhas.append(linha)
                linha = palavra

        if linha:
            linhas.append(linha)

        return linhas

    # =========================================================
    # ID
    # =========================================================

    def gerar_exam_id(self, turma):

        data_str = datetime.now().strftime("%Y%m%d")
        sufixo = str(uuid.uuid4())[:6].upper()

        turma_clean = ''.join(
            c for c in unicodedata.normalize('NFKD', turma)
            if not unicodedata.combining(c)
        )

        turma_clean = turma_clean.replace(" ", "").replace("º", "").upper()[:6]

        return f"PROV_{turma_clean}_{data_str}_{sufixo}"

    # =========================================================
    # QR CODE
    # =========================================================

    def gerar_qrcode(self, exam_id):

        qr = qrcode.QRCode(version=2, box_size=4, border=2)
        qr.add_data(exam_id)
        qr.make(fit=True)

        img = qr.make_image(fill_color="black", back_color="white")
        buffer = BytesIO()
        img.save(buffer, format="PNG")
        buffer.seek(0)

        return ImageReader(buffer)

    # =========================================================
    # CAPA
    # =========================================================

    def gerar_pdf_prova(
        self,
        escola,
        turma,
        ano,
        disciplinas,
        professor,
        questoes,
        qtd_questoes,
        data_prova=None
    ):

        buffer = BytesIO()
        c = canvas.Canvas(buffer, pagesize=A4)

        exam_id = self.gerar_exam_id(turma)
        qr_image = self.gerar_qrcode(exam_id)

        y = self.page_height - self.margin_top

        # LINHA 01 - Nome da Escola (centralizado)
        c.setFont("Helvetica-Bold", 11)
        escola = escola.strip().upper() if escola else "ESCOLA FANTASIA"
        c.drawCentredString(self.page_width / 2, y, escola)
        y -= 8 * mm

        # LINHA 02 - Título (centralizado)
        c.setFont("Helvetica", 11)
        disciplina = disciplinas[0] if disciplinas else "Matemática"
        titulo = f"Prova de {disciplina} - {ano} - {turma}"
        c.drawCentredString(self.page_width / 2, y, titulo)
        y -= 8 * mm

        # LINHA 03 - Nome
        c.setFont("Helvetica", 10)
        linha_nome = "Nome: "
        largura_nome = c.stringWidth(linha_nome, "Helvetica", 10)
        c.drawString(self.margin_left, y, linha_nome)
        c.setStrokeColor(black)
        c.setLineWidth(0.5)
        c.line(
            self.margin_left + largura_nome + 2 * mm,
            y - 1,
            self.page_width - self.margin_right,
            y - 0
        )
        c.setLineWidth(1)
        y -= 8 * mm

        # LINHA 04 - Professor, Data, Conceito
        if data_prova:
            data_txt = data_prova.strftime("%d/%m/%Y")
        else:
            data_txt = "____/____/______"

        # Calcular largura dos textos
        largura_prof = c.stringWidth(f"Professor(a): {professor}", "Helvetica", 10)
        largura_data = c.stringWidth(f"Data: {data_txt}", "Helvetica", 10)

        # Calcular posições
        centro_pagina = self.page_width / 2
        pos_data = centro_pagina - (largura_data / 2)

        # Desenhar
        c.drawString(self.margin_left, y, f"Professor(a): {professor}")
        c.drawString(pos_data, y, f"Data: {data_txt}")
        c.drawRightString(self.page_width - self.margin_right, y, "Conceito/Nota: ___________")

        y -= 10 * mm

        # INSTRUÇÕES
        c.setFont("Helvetica-Bold", 10)
        c.drawString(self.margin_left, y, "INSTRUÇÕES:")
        y -= 6 * mm

        instrucoes = [
            "1. Leia cada questão com atenção.",
            "2. Marque apenas uma alternativa por questão.",
            "3. Preencha o círculo completamente.",
            "4. Use caneta azul ou preta.",
            "5. Não rasure. Rasuras anulam a questão.",
            "6. Boa prova!"
        ]

        c.setFont("Helvetica", 9)
        for instrucao in instrucoes:
            c.drawString(self.margin_left + 5 * mm, y, instrucao)
            y -= 5 * mm

        y -= 20 * mm

        # GRADE
        grade_x = self.margin_left + 8 * mm
        grade_y = y

        diametro = 9 * mm
        espaco_h = 4 * mm
        espaco_v = 8 * mm

        largura_celula = diametro + espaco_h
        altura_celula = diametro + espaco_v

        grade_largura = largura_celula * 10
        grade_altura = altura_celula * 4

        qr_tamanho = 28 * mm

        # QR Code
        qr_x = grade_x + grade_largura + 20 * mm
        qr_y = grade_y - grade_altura + 16 * mm

        # QUADRADOS PRETOS SUPERIORES
        self._desenhar_quadrado_preto(c, self.margin_left + 5 * mm, grade_y + 5 * mm)
        self._desenhar_quadrado_preto(c, self.page_width - self.margin_right - 5 * mm, grade_y + 5 * mm)

        # TÍTULO GRADE
        centro_grade = grade_x + grade_largura / 2
        c.setFont("Helvetica-Bold", 10)
        c.drawCentredString(centro_grade, grade_y + 5 * mm, "GRADE DE RESPOSTAS")

        # NÚMEROS
        inicio_x = grade_x
        inicio_y = grade_y - 5 * mm
        c.setFont("Helvetica", 9)

        for i in range(1, 11):
            x_centro = inicio_x + (i - 0.5) * largura_celula
            c.drawCentredString(x_centro, inicio_y, str(i).zfill(2))

        # ALTERNATIVAS
        letras = ["A", "B", "C", "D"]
        y_linha = inicio_y - altura_celula

        for letra in letras:
            c.setFont("Helvetica-Bold", 10)
            c.drawString(grade_x - 7 * mm, y_linha + diametro / 2, letra)

            for col in range(10):
                x_centro = inicio_x + (col + 0.5) * largura_celula
                y_centro = y_linha + diametro / 2
                self._desenhar_circulo(c, x_centro, y_centro, diametro)

            y_linha -= altura_celula

        # QUADRADOS PRETOS INFERIORES
        self._desenhar_quadrado_preto(c, self.margin_left + 5 * mm, y_linha + altura_celula - 15 * mm)
        self._desenhar_quadrado_preto(c, self.page_width - self.margin_right - 5 * mm, y_linha + altura_celula - 15 * mm)

        # QR CODE
        c.setFillColor(white)
        c.rect(qr_x - 2 * mm, qr_y - 2 * mm, qr_tamanho + 4 * mm, qr_tamanho + 4 * mm, fill=1, stroke=0)
        c.drawImage(qr_image, qr_x, qr_y, width=qr_tamanho, height=qr_tamanho)
        c.setFillColor(black)

        # RASCUNHO
        y_rascunho = y_linha + altura_celula - 35 * mm

        c.setFont("Helvetica-Bold", 10)
        c.drawString(self.margin_left, y_rascunho, "ANOTAÇÕES")
        y_rascunho -= 5 * mm
        y_rascunho -= 5 * mm

        altura_rascunho = max(y_rascunho - self.margin_bottom - 10 * mm, 40 * mm)

        c.rect(
            self.margin_left,
            y_rascunho - altura_rascunho,
            self.content_width,
            altura_rascunho,
            stroke=1,
            fill=0
        )

        # Linhas internas do rascunho
        c.setStrokeColor(grey)
        num_linhas = int(altura_rascunho / (8 * mm))

        for i in range(num_linhas):
            linha_y = y_rascunho - ((i + 1) * 8 * mm)
            if linha_y > (y_rascunho - altura_rascunho + 5 * mm):
                c.line(
                    self.margin_left + 5 * mm,
                    linha_y,
                    self.page_width - self.margin_right - 5 * mm,
                    linha_y
                )

        c.setStrokeColor(black)

        # RODAPÉ
        c.setFont("Helvetica", 8)
        c.setFillColor(grey)

        c.drawCentredString(
            self.page_width / 2,
            self.margin_bottom - 3 * mm,
            "Sistema Lados - 2026. Todos os Direitos Reservados."
        )

        c.drawRightString(
            self.page_width - self.margin_right,
            self.margin_bottom - 3 * mm,
            "01"
        )

        c.setFillColor(black)

        c.showPage()
        c.save()

        buffer.seek(0)

        return buffer, exam_id

    # =========================================================
    # QUESTÕES
    # =========================================================

    def gerar_pdf_questoes(self, questoes, exam_id=""):

        buffer = BytesIO()
        c = canvas.Canvas(buffer, pagesize=A4)

        pagina = 2
        y = self.page_height - self.margin_top

        for idx, q in enumerate(questoes, 1):

            if y < 50 * mm:
                self._rodape_com_id(c, pagina, exam_id)
                c.showPage()
                pagina += 1
                y = self.page_height - self.margin_top

            enunciado = q.get("enunciado", "")
            texto = self._quebrar_texto(f"{idx}) {enunciado}", self.content_width, "Helvetica-Bold", 11)

            c.setFont("Helvetica-Bold", 11)

            for linha in texto:
                c.drawString(self.margin_left, y, linha)
                y -= 5 * mm

            y -= 2 * mm

            alternativas = q.get("alternativas", [])
            c.setFont("Helvetica", 10)

            for alt in alternativas:
                letra = alt.get("letra", "")
                texto_alt = alt.get("texto", "")
                linhas = self._quebrar_texto(texto_alt, self.content_width - 15 * mm, "Helvetica", 10)

                for i, linha in enumerate(linhas):
                    prefixo = f"{letra}) " if i == 0 else "   "
                    c.drawString(self.margin_left + 5 * mm, y, prefixo + linha)
                    y -= 5 * mm

            y -= 8 * mm

        self._rodape_com_id(c, pagina, exam_id)
        c.showPage()
        c.save()

        buffer.seek(0)

        return buffer

    # =========================================================
    # RODAPÉ COM ID
    # =========================================================

    def _rodape_com_id(self, c, pagina, exam_id):

        c.setFont("Helvetica", 8)
        c.setFillColor(grey)

        c.drawCentredString(
            self.page_width / 2,
            self.margin_bottom - 3 * mm,
            f"Sistema Lados - 2026. Todos os Direitos Reservados.  ID: {exam_id}"
        )

        c.drawRightString(
            self.page_width - self.margin_right,
            self.margin_bottom - 3 * mm,
            str(pagina).zfill(2)
        )

        c.setFillColor(black)

    # =========================================================
    # GABARITO
    # =========================================================

    def gerar_pdf_gabarito(self, questoes, titulo):

        buffer = BytesIO()
        c = canvas.Canvas(buffer, pagesize=A4)

        y = self.page_height - self.margin_top

        c.setFont("Helvetica-Bold", 14)
        c.drawCentredString(self.page_width / 2, y, f"GABARITO COMENTADO - {titulo}")
        y -= 15 * mm

        for q in questoes:

            if y < 50 * mm:
                c.showPage()
                y = self.page_height - self.margin_top

            numero = q.get("numero", 0)
            gabarito = q.get("gabarito", "A")
            comentario = q.get("comentario", "Comentário não disponível.")

            c.setFont("Helvetica-Bold", 11)
            c.drawString(self.margin_left, y, f"Questão {numero}")
            y -= 5 * mm

            c.setFont("Helvetica", 10)
            c.drawString(self.margin_left, y, f"Gabarito: {gabarito}")
            y -= 5 * mm

            linhas = self._quebrar_texto(comentario, self.content_width, "Helvetica", 9)

            c.setFont("Helvetica", 9)

            for linha in linhas:
                c.drawString(self.margin_left + 3 * mm, y, linha)
                y -= 4 * mm

            y -= 6 * mm

            c.line(self.margin_left, y, self.page_width - self.margin_right, y)
            y -= 8 * mm

        c.showPage()
        c.save()

        buffer.seek(0)

        return buffer

    # =========================================================
    # ZIP
    # =========================================================

    def gerar_zip_prova(
        self,
        escola,
        turma,
        ano,
        disciplinas,
        professor,
        questoes,
        qtd_questoes,
        data_prova=None
    ):

        zip_buffer = BytesIO()

        for idx, q in enumerate(questoes[:qtd_questoes], 1):
            q["numero"] = idx

        pdf_prova, exam_id = self.gerar_pdf_prova(
            escola, turma, ano, disciplinas, professor,
            questoes, qtd_questoes, data_prova
        )

        pdf_questoes = self.gerar_pdf_questoes(questoes[:qtd_questoes], exam_id)

        titulo = f"{disciplinas[0]}_{turma}" if disciplinas else turma

        pdf_gabarito = self.gerar_pdf_gabarito(questoes[:qtd_questoes], titulo)

        nome_base = f"{titulo}_{datetime.now().strftime('%Y%m%d_%H%M')}"

        with zipfile.ZipFile(zip_buffer, "w", zipfile.ZIP_DEFLATED) as zip_file:
            zip_file.writestr(f"{nome_base}_PROVA.pdf", pdf_prova.getvalue())
            zip_file.writestr(f"{nome_base}_QUESTOES.pdf", pdf_questoes.getvalue())
            zip_file.writestr(f"{nome_base}_GABARITO.pdf", pdf_gabarito.getvalue())

        zip_buffer.seek(0)

        return zip_buffer, nome_base


gerador_prova = GeradorProva()
