"""detector_grid.py - Detecção automática de grade (sem coordenadas fixas)"""

import cv2
import numpy as np
from typing import List, Tuple, Dict

class DetectorGrid:
    """Detecta grade de respostas automaticamente usando projeção e Hough"""
    
    @staticmethod
    def detectar_por_projecao(imagem: np.ndarray) -> Tuple[int, int, int, int]:
        """Detecta grade por análise de projeção (soma de pixels por eixo)"""
        gray = cv2.cvtColor(imagem, cv2.COLOR_BGR2GRAY)
        _, thresh = cv2.threshold(gray, 100, 255, cv2.THRESH_BINARY_INV)
        
        # Projeção vertical
        proj_y = np.sum(thresh, axis=1)
        proj_y_normalizado = proj_y / np.max(proj_y) if np.max(proj_y) > 0 else proj_y
        
        # Encontrar limites da grade (onde há concentração de pixels)
        limiar = 0.3
        y_inicio = 0
        y_fim = len(proj_y_normalizado) - 1
        
        for i, val in enumerate(proj_y_normalizado):
            if val > limiar:
                y_inicio = i
                break
        
        for i in range(len(proj_y_normalizado) - 1, -1, -1):
            if proj_y_normalizado[i] > limiar:
                y_fim = i
                break
        
        # Projeção horizontal
        regiao = thresh[y_inicio:y_fim, :]
        proj_x = np.sum(regiao, axis=0)
        proj_x_normalizado = proj_x / np.max(proj_x) if np.max(proj_x) > 0 else proj_x
        
        x_inicio = 0
        x_fim = len(proj_x_normalizado) - 1
        
        for i, val in enumerate(proj_x_normalizado):
            if val > limiar:
                x_inicio = i
                break
        
        for i in range(len(proj_x_normalizado) - 1, -1, -1):
            if proj_x_normalizado[i] > limiar:
                x_fim = i
                break
        
        return x_inicio, y_inicio, x_fim, y_fim
    
    @staticmethod
    def detectar_por_hough(imagem: np.ndarray) -> Tuple[List[int], List[int]]:
        """Detecta linhas da grade usando Hough Lines"""
        gray = cv2.cvtColor(imagem, cv2.COLOR_BGR2GRAY)
        edges = cv2.Canny(gray, 50, 150)
        
        lines = cv2.HoughLines(edges, 1, np.pi/180, 100)
        if lines is None:
            return [], []
        
        verticais = []
        horizontais = []
        
        for rho, theta in lines[:, 0]:
            if abs(np.cos(theta)) < 0.1:
                # Linha horizontal
                horizontais.append(rho)
            elif abs(np.sin(theta)) < 0.1:
                # Linha vertical
                verticais.append(rho)
        
        # Agrupar linhas próximas
        verticais = sorted(set([int(v) for v in verticais]))
        horizontais = sorted(set([int(h) for h in horizontais]))
        
        return verticais, horizontais
    
    @staticmethod
    def calcular_celulas(imagem: np.ndarray) -> Dict:
        """Calcula posições das células da grade automaticamente"""
        x1, y1, x2, y2 = DetectorGrid.detectar_por_projecao(imagem)
        
        regiao = imagem[y1:y2, x1:x2]
        alt_celula = (y2 - y1) // 20
        larg_celula = (x2 - x1) // 4
        
        celulas = {}
        for linha in range(20):
            for coluna in range(4):
                cx = x1 + coluna * larg_celula + larg_celula // 2
                cy = y1 + linha * alt_celula + alt_celula // 2
                celulas[(linha + 1, coluna)] = (cx, cy, larg_celula // 2)
        
        return {
            "celulas": celulas,
            "grade_bbox": (x1, y1, x2, y2),
            "altura_celula": alt_celula,
            "largura_celula": larg_celula
        }
