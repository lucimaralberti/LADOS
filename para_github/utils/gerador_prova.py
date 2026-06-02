"""
Gerador de Provas em PDF - LADOS 2.0
Padrão baseado no modelo fornecido
"""

from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm, cm
from reportlab.lib.colors import black, white, lightgrey
from reportlab.pdfgen import canvas
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib.fonts import addMapping
import os
from datetime import datetime

class GeradorProva:
    def __init__(self, output_path="output"):
        self.output_path = output_path
        os.makedirs(output_path, exist_ok=True)
        
        # Registrar fontes (usando fontes padrão do ReportLab)
        try:
            # Tentar registrar Arial
            pdfmetrics.registerFont(TTFont('Arial', 'arial.ttf'))
            self.font_normal = 'Arial'
        except:
            self.font_normal = 'Helvetica'
        
    def gerar_prova(self, dados_prova):
        """
        Gera PDF da prova no padrão solicitado
        
        dados_prova = {
            "nome_aluno": "",
            "professor": "Carlos Silva",
            "data": "29/04/2026",
            "ano": "3º Ano",
            "turma": "Manhã",
            "disciplinas": ["Língua Portuguesa", "Matemática"],
            "questoes": [
                {
                    "numero": 1,
                    "enunciado": "Qual ela deve escolher?",
                    "alternativas": ["10", "T", "■", "§"],
                    "gabarito": "A"
                },
                ...
            ]
        }
        """
        
        # Nome do arquivo
        nome_arquivo = f"prova_{dados_prova.get('ano', '')}_{dados_prova.get('turma', '')}_{datetime.now().strftime('%Y%m%d%H%M%S')}.pdf"
        caminho_pdf = os.path.join(self.output_path, nome_arquivo)
        
        # Criar PDF
        c = canvas.Canvas(caminho_pdf, pagesize=A4)
        width, height = A4
        margem_esq = 20 * mm
        margem_dir = width - 20 * mm
        margem_sup = height - 20 * mm
        y_position = margem_sup
        
        # ========== CONFIGURAÇÕES DE FONTE ==========
        c.setFont(self.font_normal, 11)
        
        # ========== CABEÇALHO ==========
        # Nome (com linha completa)
        c.drawString(margem_esq, y_position, "Nome:")
        # Linha para o nome (do final da palavra Nome até a margem direita)
        linha_inicio = margem_esq + 35
        c.line(linha_inicio, y_position - 3, margem_dir, y_position - 3)
        y_position -= 15
        
        # Professor(a)
        c.drawString(margem_esq, y_position, f"Professor(a): {dados_prova.get('professor', '')}")
        y_position -= 15
        
        # Data e Conceito/Nota
        c.drawString(margem_esq, y_position, f"Data: {dados_prova.get('data', datetime.now().strftime('%d/%m/%Y'))} /")
        c.drawString(margem_esq + 100, y_position, "Conceito/Nota:")
        y_position -= 20
        
        # Linha separadora
        c.line(margem_esq, y_position, margem_dir, y_position)
        y_position -= 15
        
        # ========== INSTRUÇÕES ==========
        c.setFont(self.font_normal, 10)
        c.drawString(margem_esq, y_position, "## INSTRUÇÕES:")
        y_position -= 15
        
        instrucoes = [
            "1) Leia cada questão com atenção.",
            "2) Marque apenas uma alternativa.",
            "3) Questões com duas alternativas marcadas serão consideradas erradas.",
            "4) Ao preencher a grade, pinte o círculo completamente.",
            "5) Sempre use caneta azul ou preta."
        ]
        
        for instr in instrucoes:
            c.drawString(margem_esq + 5, y_position, instr)
            y_position -= 12
        
        y_position -= 10
        
        # ========== GRADE DE RESPOSTAS ==========
        c.setFont(self.font_normal, 11)
        c.drawString(margem_esq, y_position, "## GRADE DE RESPOSTAS")
        y_position -= 20
        
        num_questoes = len(dados_prova.get('questoes', []))
        
        # Desenhar grade com base no número de questões
        grade_y = self._desenhar_grade_respostas(c, margem_esq, margem_dir, y_position, num_questoes)
        y_position = grade_y - 20
        
        # ========== QUESTÕES ==========
        for idx, questao in enumerate(dados_prova.get('questoes', []), 1):
            # Verificar se precisa de nova página
            if y_position < 50 * mm:
                c.showPage()
                y_position = margem_sup
                # Reconfigurar fonte na nova página
                c.setFont(self.font_normal, 11)
            
            # Número da questão
            c.setFont(self.font_normal, 11)
            c.drawString(margem_esq, y_position, f"{idx}) {questao['enunciado']}")
            y_position -= 15
            
            # Alternativas
            c.setFont(self.font_normal, 10)
            alternativas = questao.get('alternativas', [])
            for letra, texto in zip(['A', 'B', 'C', 'D'], alternativas):
                c.drawString(margem_esq + 10, y_position, f"{letra}) {texto}")
                y_position -= 12
            
            y_position -= 8  # Espaço entre questões
        
        # ========== RODAPÉ ==========
        c.setFont(self.font_normal, 8)
        rodape = "SISTEMA LADOS - 2026. Todos os Direitos Reservados."
        largura_texto = pdfmetrics.stringWidth(rodape, self.font_normal, 8)
        c.drawString((width - largura_texto) / 2, 15 * mm, rodape)
        
        # Salvar PDF
        c.save()
        
        return caminho_pdf
    
    def _desenhar_grade_respostas(self, canvas_obj, x, x_fim, y, num_questoes):
        """Desenha a grade de respostas com círculos"""
        import math
        
        # Determinar layout da grade
        colunas = min(num_questoes, 10)  # Máximo 10 colunas por linha
        linhas = math.ceil(num_questoes / colunas)
        
        # Configurações da grade
        largura_disponivel = x_fim - x
        espacamento = largura_disponivel / (colunas + 1)
        raio = 4
        y_atual = y
        
        for linha in range(linhas):
            y_atual -= 15
            for col in range(colunas):
                questao_num = linha * colunas + col + 1
                if questao_num > num_questoes:
                    break
                
                x_pos = x + (col + 1) * espacamento
                
                # Número da questão
                canvas_obj.setFont(self.font_normal, 8)
                canvas_obj.drawString(x_pos - 3, y_atual + 8, str(questao_num))
                
                # Círculos das alternativas
                canvas_obj.setFont(self.font_normal, 7)
                for i, letra in enumerate(['A', 'B', 'C', 'D']):
                    x_circulo = x_pos + i * 12
                    # Desenhar círculo
                    canvas_obj.circle(x_circulo, y_atual - 2, raio, stroke=1, fill=0)
                    # Letra dentro do círculo
                    canvas_obj.drawString(x_circulo - 3, y_atual - 6, letra)
        
        return y_atual - 10


# Exemplo de uso e teste
def gerar_prova_exemplo():
    """Gera uma prova de exemplo igual ao modelo"""
    questoes_exemplo = [
        {
            "numero": 1,
            "enunciado": "Qual ela deve escolher?",
            "alternativas": ["10", "T", "■", "§"],
            "gabarito": "A"
        },
        {
            "numero": 2,
            "enunciado": "O que ele vai usar?",
            "alternativas": ["Números", "Letras", "Desenhos", "Sinais"],
            "gabarito": "B"
        },
        {
            "numero": 3,
            "enunciado": "Qual é uma letra?",
            "alternativas": ["9", "R", "¥", "1"],
            "gabarito": "B"
        },
        {
            "numero": 4,
            "enunciado": "Qual par mostra a mesma letra?",
            "alternativas": ["A - a", "B - D", "C - S", "E - F"],
            "gabarito": "A"
        },
        {
            "numero": 5,
            "enunciado": "Qual letra vem depois de M?",
            "alternativas": ["L", "N", "O", "P"],
            "gabarito": "B"
        }
    ]
    
    dados = {
        "nome_aluno": "",
        "professor": "Carlos Silva",
        "data": "29/04/2026",
        "ano": "3º Ano",
        "turma": "Manhã",
        "disciplinas": ["Língua Portuguesa"],
        "questoes": questoes_exemplo[:5]
    }
    
    gerador = GeradorProva()
    caminho = gerador.gerar_prova(dados)
    print(f"✅ Prova gerada: {caminho}")
    return caminho


if __name__ == "__main__":
    gerar_prova_exemplo()
