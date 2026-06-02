"""
Gerador de Prova OMR - Layout com Marcas nas posições corretas
"""

import hashlib
import json
import qrcode
from datetime import datetime
from pathlib import Path
from typing import Dict, Any

from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
from reportlab.pdfgen import canvas
from reportlab.platypus import Image, Paragraph
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_JUSTIFY


class GeradorProvaOMR:
    def _get_texto_alternativa(self, alt):
        """Extrai o texto de uma alternativa, seja dict ou string"""
        if isinstance(alt, dict):
            return alt.get("texto", str(alt))
        return str(alt)


    def __init__(self, output_dir="output"):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)

        self.font = "Helvetica"
        self.bold = "Helvetica-Bold"

    # =========================
    # QR CODE
    # =========================
    def gerar_qr(self, payload):
        path = self.output_dir / f"qr_{datetime.now().strftime('%H%M%S%f')}.png"
        img = qrcode.make(json.dumps(payload))
        img.save(path)
        return path

    # =========================
    # RODAPÉ
    # =========================
    def rodape(self, c, W, margem_inf, pagina):
        c.setFont("Helvetica-Bold", 7)
        c.drawCentredString(
            W / 2,
            margem_inf - 5 * mm,
            "SISTEMA LADOS - 2026. Todos os Direitos Reservados"
        )

        if pagina > 1:
            c.setFont("Helvetica", 7)
            c.drawRightString(
                W - 15 * mm,
                margem_inf - 5 * mm,
                f"{pagina:02d}"
            )

    # =========================
    # GRADE OMR
    # =========================
    def desenhar_grade(self, c, margem_esq, margem_dir, y):

        num_q = 20
        largura = margem_dir - margem_esq

        dx = largura / (num_q + 1)
        dy = 8 * mm

        topo = y
        altura = dy * 5

        c.rect(margem_esq, topo - altura, largura, altura)

        for j in range(1, 5):
            c.line(margem_esq, topo - j * dy, margem_dir, topo - j * dy)

        for i in range(1, num_q + 1):
            x = margem_esq + i * dx
            c.line(x, topo, x, topo - altura)

        c.setFont(self.bold, 8)
        for i in range(num_q):
            x = margem_esq + (i + 1.5) * dx
            c.drawCentredString(x, topo - dy / 2, f"{i+1:02d}")

        for j, letra in enumerate(["A", "B", "C", "D"]):
            y_c = topo - (j + 1.5) * dy

            c.setFont(self.bold, 10)
            c.drawCentredString(margem_esq + dx / 2, y_c - 3, letra)

            for i in range(num_q):
                x = margem_esq + (i + 1.5) * dx
                c.circle(x, y_c, dx * 0.35)

        return topo - altura

    # =========================
    # QUESTÕES (página 2+)
    # =========================
    def desenhar_questoes(self, c, questoes, W, H):

        margem_esq = 15 * mm
        margem_dir = W - 15 * mm
        margem_sup = H - 20 * mm
        margem_inf = 20 * mm

        largura = margem_dir - margem_esq
        y = margem_sup
        pagina = 2

        styles = getSampleStyleSheet()

        estilo_q = ParagraphStyle(
            "q",
            parent=styles["Normal"],
            fontName="Helvetica",
            fontSize=11,
            leading=14,
            alignment=TA_JUSTIFY,
        )

        estilo_alt = ParagraphStyle(
            "a",
            parent=styles["Normal"],
            fontName="Helvetica",
            fontSize=11,
            leading=14,
            alignment=TA_JUSTIFY,
        )

        for i, q in enumerate(questoes, start=1):

            if y < margem_inf + 40 * mm:
                self.rodape(c, W, margem_inf, pagina)
                c.showPage()
                pagina += 1
                y = margem_sup

            p = Paragraph(f"<b>{i})</b> {q['enunciado']}", estilo_q)
            w, h = p.wrap(largura, y)
            p.drawOn(c, margem_esq, y - h)
            y -= h

            y -= 3 * mm

            for letra in ["A", "B", "C", "D"]:
                alternativas = q.get("alternativas", {})
    
                if isinstance(alternativas, dict):
                    texto = alternativas.get(letra, "")
                elif isinstance(alternativas, list):
                    idx = ord(letra) - ord('A')
                    if idx < len(alternativas):
                        alt = alternativas[idx]
                        if isinstance(alt, dict):
                            texto = alt.get("texto", "")
                        else:
                            texto = str(alt)
                    else:
                        texto = ""
                else:
                    texto = ""
    
                p = Paragraph(f"<b>{letra})</b> {texto}", estilo_alt)
                w, h = p.wrap(largura, y)
                p.drawOn(c, margem_esq, y - h)
                y -= h

            y -= 6 * mm

        self.rodape(c, W, margem_inf, pagina)

    # =========================
    # PDF
    # =========================
    def gerar_pdf(self, dados: Dict[str, Any]):

        prova_id = hashlib.md5(
            json.dumps(dados.get("questoes", []), sort_keys=True).encode()
        ).hexdigest()[:10]

        path = self.output_dir / f"prova_{prova_id}.pdf"

        c = canvas.Canvas(str(path), pagesize=A4)
        W, H = A4

        margem_esq = 15 * mm
        margem_dir = W - 15 * mm
        margem_sup = H - 15 * mm
        margem_inf = 20 * mm

        largura = margem_dir - margem_esq
        y = margem_sup

        # =====================================================
        # LINHA 1: Nome da Escola
        # =====================================================
        c.setFont(self.bold, 11)
        nome_escola = dados.get("nome_escola", "")

        if nome_escola:
            c.drawCentredString(W/2, y, nome_escola)
        y -= 6 * mm

        # =====================================================
        # LINHA 2: Subtítulo
        # =====================================================
        c.setFont(self.font, 11)
        c.drawCentredString(
            W/2,
            y,
            f"{dados.get('disciplina')} - {dados.get('ano')} - {dados.get('turma')}"
        )
        y -= 10 * mm

        # =====================================================
        # LINHA 3: Nome
        # =====================================================
        c.setFont(self.bold, 11)
        c.drawString(margem_esq, y, "Nome:")
        c.line(margem_esq + 35, y - 2, margem_dir, y - 2)
        y -= 8 * mm

        # =====================================================
        # LINHA 4: Professor, Data, Conceito
        # =====================================================
        col = largura / 3
        campos = ["Professor(a):", "Data:", "Conceito/Nota:"]

        for i, t in enumerate(campos):
            x = margem_esq + i * col
            c.drawString(x, y, t)
            w = c.stringWidth(t, self.bold, 11)
            c.line(x + w + 5, y - 2, x + col - 5, y - 2)

        y -= 8 * mm

        # =====================================================
        # LINHA 5: [BRANCO] - apenas espaço
        # =====================================================
        y -= 2 * mm

        # =====================================================
        # LINHA 6: MARCAS SUPERIORES (esquerda e direita)
        # =====================================================
        marca = 5 * mm
        c.rect(margem_esq, y - marca/2, marca, marca, fill=1, stroke=0)
        c.rect(margem_dir - marca, y - marca/2, marca, marca, fill=1, stroke=0)
        y -= 6 * mm

        # =====================================================
        # LINHA 7: [BRANCO]
        # =====================================================
        y -= 2 * mm

        # =====================================================
        # LINHA 8: INSTRUÇÕES (título)
        # =====================================================
        altura = 35 * mm
        col_esq = largura * 0.75

        c.rect(margem_esq, y - altura, largura, altura)
        c.line(margem_esq + col_esq, y, margem_esq + col_esq, y - altura)

        y_inst = y - 6 * mm

        c.setFont(self.bold, 11)
        c.drawString(margem_esq + 5, y_inst, "INSTRUÇÕES:")
        y_inst -= 6 * mm

        # =====================================================
        # LINHAS 9-13: 5 instruções + QR Code
        # =====================================================
        c.setFont(self.font, 10)

        instrucoes = [
            "1) Leia cada questão com atenção.",
            "2) Marque apenas uma alternativa.",
            "3) Questões com duas alternativas marcadas serão consideradas erradas.",
            "4) Ao preencher a grade, pinte o círculo completamente.",
            "5) Sempre use caneta azul ou preta."
        ]

        for linha in instrucoes:
            c.drawString(margem_esq + 8, y_inst, linha)
            y_inst -= 5 * mm

        # QR CODE
        gabarito = [q.get("gabarito") for q in dados.get("questoes", [])]
        qr_path = self.gerar_qr({"id": prova_id, "gabarito": gabarito})

        qr_size = 30 * mm
        cx = margem_esq + col_esq + (largura - col_esq) / 2
        cy = y - altura / 2

        Image(str(qr_path), qr_size, qr_size).drawOn(c, cx - qr_size/2, cy - qr_size/2)

        y -= altura

        # =====================================================
        # LINHA 14: [BRANCO]
        # =====================================================
        y -= 4 * mm

        # =====================================================
        # LINHA 15: GRADE DE RESPOSTAS (título)
        # =====================================================
        c.setFont(self.bold, 11)
        c.drawCentredString(W/2, y, "GRADE DE RESPOSTAS")
        y -= 5 * mm

        # =====================================================
        # LINHAS 16-20: Grade (5 linhas)
        # =====================================================
        y = self.desenhar_grade(c, margem_esq, margem_dir, y)

        # =====================================================
        # LINHA 21: [BRANCO]
        # =====================================================
        y -= 4 * mm

        # =====================================================
        # LINHA 22: MARCAS INFERIORES (esquerda e direita)
        # =====================================================
        c.rect(margem_esq, y - marca/2, marca, marca, fill=1, stroke=0)
        c.rect(margem_dir - marca, y - marca/2, marca, marca, fill=1, stroke=0)
        y -= 6 * mm

        # =====================================================
        # LINHA 23: [BRANCO]
        # =====================================================
        y -= 2 * mm

        # =====================================================
        # LINHA 24: Habilidades / Descritores
        # =====================================================
        c.setFont(self.bold, 9)
        c.drawString(margem_esq, y, "Habilidades / Descritores:")
        y -= 8 * mm

        # =====================================================
        # LINHA 25: RASCUNHO
        # =====================================================
        topo_quadro = y

        c.rect(
            margem_esq,
            margem_inf + 10 * mm,
            largura,
            topo_quadro - (margem_inf + 10 * mm)
        )

        c.setFont(self.bold, 9)
        c.drawString(margem_esq + 5, topo_quadro - 5 * mm, "RASCUNHO")

        # RODAPÉ
        self.rodape(c, W, margem_inf, 1)

        # PÁGINA 2+ (questões)
        c.showPage()
        self.desenhar_questoes(c, dados.get("questoes", []), W, H)

        # SALVAR METADADOS
        gabarito_path = self.output_dir / f"prova_{prova_id}_metadata.json"
        gabarito_data = {
            "prova_id": prova_id,
            "gabarito": gabarito,
            "total_questoes": len(gabarito),
            "disciplina": dados.get("disciplina"),
            "ano": dados.get("ano"),
            "turma": dados.get("turma"),
            "data_criacao": datetime.now().isoformat()
        }
        with open(gabarito_path, "w", encoding="utf-8") as f:
            json.dump(gabarito_data, f, indent=2, ensure_ascii=False)

        c.save()

        return path


def gerar_prova(dados: Dict[str, Any]):
    return GeradorProvaOMR().gerar_pdf(dados)
