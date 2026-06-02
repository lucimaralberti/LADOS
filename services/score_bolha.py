# -*- coding: utf-8 -*-
"""score_bolha.py - Score probabilistico com binarizacao adaptativa"""

import cv2
import numpy as np
from typing import Tuple

# Tentar importar scikit-image para binarizacao adaptativa
try:
    from skimage.filters import threshold_local
    SKIMAGE_DISPONIVEL = True
except ImportError:
    SKIMAGE_DISPONIVEL = False

class ScoreBolha:
    """Calcula probabilidade de bolha preenchida"""

    @staticmethod
    def binarizar_roi(roi: np.ndarray) -> np.ndarray:
        """Binarizacao adaptativa (melhor para diferentes iluminacoes)"""
        if SKIMAGE_DISPONIVEL and roi.shape[0] > 10 and roi.shape[1] > 10:
            try:
                # Threshold adaptativo baseado na regiao
                thresh = threshold_local(roi, 15, method='gaussian')
                binario = (roi > thresh).astype(np.uint8) * 255
                return binario
            except:
                pass
        
        # Fallback: threshold simples
        _, binario = cv2.threshold(roi, 80, 255, cv2.THRESH_BINARY_INV)
        return binario

    @staticmethod
    def densidade_pixels(roi: np.ndarray) -> float:
        """Detecta pixels escuros (lapis, caneta, azul)"""
        if len(roi.shape) == 3:
            hsv = cv2.cvtColor(roi, cv2.COLOR_BGR2HSV)
            
            # Azul escuro (caneta)
            lower_blue = np.array([90, 50, 30])
            upper_blue = np.array([130, 255, 150])
            
            # Cinza escuro / preto (lapis grafite)
            lower_gray = np.array([0, 0, 30])
            upper_gray = np.array([180, 50, 100])
            
            # Preto intenso (caneta preta)
            lower_black = np.array([0, 0, 0])
            upper_black = np.array([180, 255, 60])
            
            mask_blue = cv2.inRange(hsv, lower_blue, upper_blue)
            mask_gray = cv2.inRange(hsv, lower_gray, upper_gray)
            mask_black = cv2.inRange(hsv, lower_black, upper_black)
            
            mask = cv2.bitwise_or(mask_blue, mask_gray)
            mask = cv2.bitwise_or(mask, mask_black)
            
            escuros = cv2.countNonZero(mask)
        else:
            # Binarizacao adaptativa
            binario = ScoreBolha.binarizar_roi(roi)
            escuros = cv2.countNonZero(binario)
        
        total = roi.shape[0] * roi.shape[1]
        return escuros / total if total > 0 else 0

    @staticmethod
    def detectar_x(roi: np.ndarray) -> float:
        """Detecta marcacao em forma de X"""
        if len(roi.shape) == 3:
            gray = cv2.cvtColor(roi, cv2.COLOR_BGR2GRAY)
        else:
            gray = roi
        
        # Binarizacao adaptativa
        binario = ScoreBolha.binarizar_roi(gray)
        
        # Detectar linhas
        edges = cv2.Canny(binario, 50, 150)
        lines = cv2.HoughLines(edges, 1, np.pi/180, 30)
        
        if lines is None:
            return 0.0
        
        angulos = []
        for rho, theta in lines[:, 0]:
            angulo = np.degrees(theta)
            angulos.append(angulo)
        
        # Verificar se ha duas linhas aproximadamente opostas (X)
        for a1 in angulos:
            for a2 in angulos:
                if abs(abs(a1 - a2) - 90) < 20:
                    return 0.8
        
        return 0.0

    @staticmethod
    def fechamento_borda(roi: np.ndarray) -> float:
        """Presenca de borda circular fechada"""
        if len(roi.shape) == 3:
            gray = cv2.cvtColor(roi, cv2.COLOR_BGR2GRAY)
        else:
            gray = roi
            
        edges = cv2.Canny(gray, 50, 150)
        contornos, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        if not contornos:
            return 0.0

        for c in contornos:
            area = cv2.contourArea(c)
            if area > 50:
                peri = cv2.arcLength(c, True)
                if peri > 0:
                    circularidade = 4 * np.pi * area / (peri * peri)
                    if circularidade > 0.7:
                        return min(1.0, area / 300)
        return 0.0

    @staticmethod
    def simetria_circular(roi: np.ndarray) -> float:
        """Simetria do circulo"""
        if len(roi.shape) == 3:
            gray = cv2.cvtColor(roi, cv2.COLOR_BGR2GRAY)
        else:
            gray = roi
            
        circles = cv2.HoughCircles(gray, cv2.HOUGH_GRADIENT, dp=1, minDist=20,
                                   param1=50, param2=30, minRadius=5, maxRadius=30)

        if circles is not None:
            return 0.9
        return 0.0

    @staticmethod
    def calcular_score(roi: np.ndarray, pesos=(0.4, 0.3, 0.2, 0.1)) -> float:
        """Score com suporte a X"""
        densidade = ScoreBolha.densidade_pixels(roi)
        fechamento = ScoreBolha.fechamento_borda(roi)
        simetria = ScoreBolha.simetria_circular(roi)
        tem_x = ScoreBolha.detectar_x(roi)
        
        score = (densidade * 0.4 + fechamento * 0.25 + simetria * 0.15 + tem_x * 0.2)
        return min(1.0, max(0.0, score))

    @staticmethod
    def classificar_por_score(score: float) -> str:
        if score >= 0.4:
            return "preenchida"
        elif score >= 0.25:
            return "ambigua"
        else:
            return "vazia"
