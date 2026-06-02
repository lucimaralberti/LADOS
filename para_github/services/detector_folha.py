"""detector_folha.py - Detecção robusta de folha (Hough + Contours + Fallback)"""

import cv2
import numpy as np
from typing import Optional, Tuple, List

class DetectorFolha:
    """Detector de folha híbrido - funciona mesmo com sombras e fundo confuso"""
    
    @staticmethod
    def detectar_contornos(imagem: np.ndarray) -> Optional[np.ndarray]:
        """Método 1: Detecção por contornos (rápido)"""
        gray = cv2.cvtColor(imagem, cv2.COLOR_BGR2GRAY)
        blur = cv2.GaussianBlur(gray, (5, 5), 0)
        edges = cv2.Canny(blur, 50, 150)
        
        contornos, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        contornos = sorted(contornos, key=cv2.contourArea, reverse=True)
        
        for c in contornos[:5]:
            peri = cv2.arcLength(c, True)
            approx = cv2.approxPolyDP(c, 0.02 * peri, True)
            if len(approx) == 4:
                return DetectorFolha._corrigir_perspectiva(imagem, approx)
        return None
    
    @staticmethod
    def detectar_hough(imagem: np.ndarray) -> Optional[np.ndarray]:
        """Método 2: Detecção por linhas Hough (fallback para folhas com sombra)"""
        gray = cv2.cvtColor(imagem, cv2.COLOR_BGR2GRAY)
        edges = cv2.Canny(gray, 50, 150)
        
        lines = cv2.HoughLines(edges, 1, np.pi/180, 150)
        if lines is None:
            return None
        
        # Encontrar interseções das linhas principais
        verticais = []
        horizontais = []
        
        for rho, theta in lines[:, 0]:
            if abs(np.cos(theta)) < 0.1:  # Linha quase horizontal
                horizontais.append((rho, theta))
            elif abs(np.sin(theta)) < 0.1:  # Linha quase vertical
                verticais.append((rho, theta))
        
        if len(verticais) < 2 or len(horizontais) < 2:
            return None
        
        # Encontrar os cantos
        rho_h1, theta_h1 = min(horizontais, key=lambda x: x[0])
        rho_h2, theta_h2 = max(horizontais, key=lambda x: x[0])
        rho_v1, theta_v1 = min(verticais, key=lambda x: x[0])
        rho_v2, theta_v2 = max(verticais, key=lambda x: x[0])
        
        cantos = DetectorFolha._calcular_interseccoes(
            rho_v1, theta_v1, rho_h1, theta_h1,
            rho_v2, theta_v2, rho_h2, theta_h2
        )
        
        if cantos:
            return DetectorFolha._corrigir_perspectiva(imagem, np.array(cantos, dtype=np.float32))
        return None
    
    @staticmethod
    def detectar_convex_hull(imagem: np.ndarray) -> Optional[np.ndarray]:
        """Método 3: Detecção por convex hull (último fallback)"""
        gray = cv2.cvtColor(imagem, cv2.COLOR_BGR2GRAY)
        blur = cv2.GaussianBlur(gray, (5, 5), 0)
        _, thresh = cv2.threshold(blur, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
        
        contornos, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        if not contornos:
            return None
        
        maior = max(contornos, key=cv2.contourArea)
        hull = cv2.convexHull(maior)
        peri = cv2.arcLength(hull, True)
        approx = cv2.approxPolyDP(hull, 0.02 * peri, True)
        
        if len(approx) >= 4:
            return DetectorFolha._corrigir_perspectiva(imagem, approx[:4])
        return None
    
    @staticmethod
    def detectar(imagem: np.ndarray) -> Optional[np.ndarray]:
        """Pipeline completo com fallbacks"""
        # Tentar métodos em ordem
        resultado = DetectorFolha.detectar_contornos(imagem)
        if resultado is not None:
            return resultado
        
        resultado = DetectorFolha.detectar_hough(imagem)
        if resultado is not None:
            return resultado
        
        return DetectorFolha.detectar_convex_hull(imagem)
    
    @staticmethod
    def _corrigir_perspectiva(imagem: np.ndarray, pontos) -> np.ndarray:
        pts = pontos.reshape(4, 2).astype(np.float32)
        pts = DetectorFolha._ordenar_pontos(pts)
        (tl, tr, br, bl) = pts
        
        largura = int(max(np.linalg.norm(br - bl), np.linalg.norm(tr - tl)))
        altura = int(max(np.linalg.norm(tr - br), np.linalg.norm(tl - bl)))
        
        destino = np.array([[0, 0], [largura - 1, 0], [largura - 1, altura - 1], [0, altura - 1]], dtype=np.float32)
        matriz = cv2.getPerspectiveTransform(pts, destino)
        return cv2.warpPerspective(imagem, matriz, (largura, altura))
    
    @staticmethod
    def _ordenar_pontos(pts: np.ndarray) -> np.ndarray:
        soma = pts.sum(axis=1)
        diff = np.diff(pts, axis=1)
        return np.array([pts[np.argmin(soma)], pts[np.argmin(diff)], pts[np.argmax(soma)], pts[np.argmax(diff)]])
    
    @staticmethod
    def _calcular_interseccoes(rho1, theta1, rho2, theta2, rho3, theta3, rho4, theta4) -> List:
        A = np.array([[np.cos(theta1), np.sin(theta1)], [np.cos(theta2), np.sin(theta2)]])
        B = np.array([rho1, rho2])
        try:
            ponto1 = np.linalg.solve(A, B)
        except:
            ponto1 = None
        
        A = np.array([[np.cos(theta3), np.sin(theta3)], [np.cos(theta4), np.sin(theta4)]])
        B = np.array([rho3, rho4])
        try:
            ponto2 = np.linalg.solve(A, B)
        except:
            ponto2 = None
        
        if ponto1 is not None and ponto2 is not None:
            return [ponto1, ponto2, ponto1, ponto2]
        return []
