"""
Gerador de Gabarito Comentado
Cria um documento PDF com gabarito, alternativa correta, explicação e habilidade
"""

from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
from reportlab.pdfgen import canvas
from reportlab.lib.colors import black, white, blue
from datetime import datetime
from pathlib import Path

def gerar_gabarito_comentado(questoes, output_path=None):
    """
    Gera um PDF com gabarito comentado
    
    Args:
        questoes: Lista de dicionários com as questões
        output_path: Caminho para salvar (opcional)
    
    Returns:
        Dicionário com dados do gabarito ou caminho do arquivo
    """
    if output_path is None:
        output_dir = Path("output")
        output_dir.mkdir(parents=True, exist_ok=True)
        output_path = output_dir / f"gabarito_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
    
    c = canvas.Canvas(str(output_path), pagesize=A4)
    width, height = A4
    margin = 20 * mm
    y = height - margin
    line_height = 8 * mm
    
    # Cabeçalho
    c.setFont("Helvetica-Bold", 16)
    c.drawString(margin, y, "GABARITO COMENTADO")
    y -= line_height
    
    c.setFont("Helvetica", 10)
    c.drawString(margin, y, f"Data de geração: {datetime.now().strftime('%d/%m/%Y %H:%M')}")
    y -= line_height * 1.5
    
    # Para cada questão
    for i, q in enumerate(questoes, 1):
        # Verificar se precisa de nova página
        if y < 50 * mm:
            c.showPage()
            y = height - margin
        
        # Número da questão
        c.setFont("Helvetica-Bold", 12)
        c.drawString(margin, y, f"Questão {i:02d}")
        y -= line_height * 0.8
        
        # Enunciado (resumido)
        c.setFont("Helvetica", 9)
        enunciado = q.get("enunciado", "")[:200]
        if len(q.get("enunciado", "")) > 200:
            enunciado += "..."
        
        text_obj = c.beginText(margin, y)
        text_obj.setFont("Helvetica", 9)
        text_obj.setTextOrigin(margin, y)
        
        # Quebrar texto em múltiplas linhas
        words = enunciado.split()
        line = ""
        for word in words:
            test_line = line + " " + word if line else word
            if c.stringWidth(test_line, "Helvetica", 9) < (width - 2 * margin):
                line = test_line
            else:
                text_obj.textLine(line)
                y -= line_height * 0.8
                line = word
        if line:
            text_obj.textLine(line)
            y -= line_height * 0.8
        
        c.drawText(text_obj)
        y -= line_height * 0.5
        
        # Gabarito
        c.setFont("Helvetica-Bold", 10)
        c.setFillColor(blue)
        c.drawString(margin, y, f"✓ Alternativa correta: {q.get('gabarito', '?')}")
        c.setFillColor(black)
        y -= line_height
        
        # Habilidade
        c.setFont("Helvetica-Oblique", 9)
        habilidade = q.get("habilidade", "Não informada")
        c.drawString(margin, y, f"📌 Habilidade: {habilidade[:80]}")
        y -= line_height * 0.8
        
        # Explicação (simplificada)
        c.setFont("Helvetica", 8)
        explicacao = f"💡 Explicação: Esta questão avalia {habilidade[:60]}..."
        c.drawString(margin, y, explicacao[:100])
        y -= line_height * 1.5
        
        # Linha separadora
        c.setStrokeColor(black)
        c.line(margin, y, width - margin, y)
        y -= line_height * 0.5
    
    c.save()
    return str(output_path)

def gerar_gabarito_json(questoes):
    """Retorna o gabarito em formato JSON para uso no ZIP"""
    return [
        {
            "numero": i,
            "gabarito": q.get("gabarito"),
            "habilidade": q.get("habilidade", ""),
            "descritor": q.get("descritor", "")
        }
        for i, q in enumerate(questoes, 1)
    ]
