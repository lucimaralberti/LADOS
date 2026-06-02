"""vision/omr_reader.py - Leitor de grade de respostas OMR"""

import cv2
import numpy as np
from typing import Dict, List, Tuple

class OMRReader:
    """Leitor de grade de respostas (bolhas)"""
    
    def detectar_circulos(self, imagem: np.ndarray) -> Dict[int, str]:
        """Detecta círculos preenchidos e retorna respostas"""
        
        gray = cv2.cvtColor(imagem, cv2.COLOR_BGR2GRAY)
        
        # Binarização adaptativa
        _, thresh = cv2.threshold(gray, 100, 255, cv2.THRESH_BINARY_INV)
        
        # Encontrar contornos
        contornos, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        # Filtrar por tamanho e circularidade
        circulos = []
        for c in contornos:
            area = cv2.contourArea(c)
            if area < 50 or area > 500:
                continue
            
            peri = cv2.arcLength(c, True)
            if peri == 0:
                continue
            
            circularidade = 4 * np.pi * area / (peri * peri)
            if circularidade > 0.7:
                # Calcular centro
                M = cv2.moments(c)
                if M["m00"] != 0:
                    cx = int(M["m10"] / M["m00"])
                    cy = int(M["m01"] / M["m00"])
                    circulos.append((cx, cy))
        
        # Mapear posições → questões
        respostas = {}
        # TODO: Implementar mapeamento real baseado em grade conhecida
        
        return respostas
    
    def calcular_score_roi(self, roi: np.ndarray) -> float:
        """Calcula score de preenchimento de uma região"""
        _, thresh = cv2.threshold(roi, 100, 255, cv2.THRESH_BINARY)
        pretos = cv2.countNonZero(thresh)
        total = roi.shape[0] * roi.shape[1]
        return pretos / total if total > 0 else 0
