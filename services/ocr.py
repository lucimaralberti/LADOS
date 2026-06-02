"""
Serviço de OCR para Leitura de Provas
Processa imagens da grade de respostas e identifica marcações
"""

import base64
import cv2
import numpy as np


def processar_prova_completa(image_base64: str) -> dict:
    """
    Processa uma imagem de prova e extrai as respostas marcadas
    
    Args:
        image_base64: Imagem em base64 (com ou sem prefixo data:image)
    
    Returns:
        Dicionário com resultados da correção
    """
    try:
        # Remover prefixo se existir
        if ',' in image_base64:
            image_base64 = image_base64.split(',')[1]
        
        # Decodificar imagem
        img_bytes = base64.b64decode(image_base64)
        nparr = np.frombuffer(img_bytes, np.uint8)
        img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        
        if img is None:
            return {"success": False, "error": "Imagem inválida"}
        
        # Redimensionar para padrão
        img = cv2.resize(img, (1200, 1600))
        
        # Converter para escala de cinza
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        
        # Aumentar contraste
        clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
        gray = clahe.apply(gray)
        
        # Detectar círculos
        circles = cv2.HoughCircles(gray, cv2.HOUGH_GRADIENT, dp=1.2, minDist=20,
                                    param1=50, param2=30, minRadius=10, maxRadius=25)
        
        # Gabarito fixo (provisório - será substituído por busca no repositório)
        gabarito = ["A", "B", "C", "D", "A", "B", "C", "D", "A", "B", 
                    "C", "D", "A", "B", "C", "D", "A", "B", "C", "D"]
        total = 20
        respostas = ['X'] * total
        
        if circles is not None:
            circles = np.round(circles[0, :]).astype("int")
            preenchidos = []
            
            for x, y, r in circles:
                mask = np.zeros(gray.shape, np.uint8)
                cv2.circle(mask, (x, y), r, 255, -1)
                if cv2.mean(gray, mask=mask)[0] < 120:
                    preenchidos.append((x, y, r))
            
            if preenchidos:
                preenchidos.sort(key=lambda c: (c[1], c[0]))
                y_vals = [c[1] for c in preenchidos]
                y_min, y_max = min(y_vals), max(y_vals)
                linhas = [[], [], [], []]
                
                for c in preenchidos:
                    if y_max - y_min > 0:
                        linha_idx = min(3, int((c[1] - y_min) / ((y_max - y_min) / 4)))
                        linhas[linha_idx].append(c)
                
                alternativas = ['A', 'B', 'C', 'D']
                for linha_idx, linha in enumerate(linhas):
                    if linha:
                        linha.sort(key=lambda c: c[0])
                        x_vals = [c[0] for c in linha]
                        x_min, x_max = min(x_vals), max(x_vals)
                        for c in linha:
                            if x_max - x_min > 0:
                                col = min(total - 1, int((c[0] - x_min) / ((x_max - x_min) / total)))
                                respostas[col] = alternativas[linha_idx]
        
        # Calcular resultados
        acertos = sum(1 for r, g in zip(respostas, gabarito) if r == g)
        percentual = round((acertos / total * 100), 1)
        
        # Determinar conceito
        if percentual >= 90:
            conceito = "MB"
        elif percentual >= 70:
            conceito = "B"
        elif percentual >= 50:
            conceito = "S"
        else:
            conceito = "I"
        
        return {
            "success": True,
            "score": acertos,
            "total": total,
            "percentage": percentual,
            "concept": conceito,
            "respostas_detectadas": respostas,
            "gabarito": gabarito
        }
        
    except Exception as e:
        return {"success": False, "error": str(e)}
