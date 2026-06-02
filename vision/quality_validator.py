"""vision/quality_validator.py - Validação de qualidade da imagem antes da correção"""

import cv2
import numpy as np
from typing import Dict, Tuple, Optional

class QualityValidator:
    """Valida se a imagem tem qualidade suficiente para correção"""
    
    @staticmethod
    def validar_brilho(imagem: np.ndarray) -> Tuple[bool, float, str]:
        """Verifica se o brilho da imagem está adequado"""
        if len(imagem.shape) == 3:
            gray = cv2.cvtColor(imagem, cv2.COLOR_BGR2GRAY)
        else:
            gray = imagem
        
        brilho_medio = gray.mean()
        
        if brilho_medio < 80:
            return False, brilho_medio, "Imagem muito escura"
        elif brilho_medio > 200:
            return False, brilho_medio, "Imagem muito clara (excesso de luz)"
        else:
            return True, brilho_medio, "Brilho adequado"
    
    @staticmethod
    def validar_nitidez(imagem: np.ndarray) -> Tuple[bool, float, str]:
        """Verifica se a imagem está nítida (não borrada)"""
        if len(imagem.shape) == 3:
            gray = cv2.cvtColor(imagem, cv2.COLOR_BGR2GRAY)
        else:
            gray = imagem
        
        # Usar operador Laplaciano para detectar borrão
        laplacian = cv2.Laplacian(gray, cv2.CV_64F)
        variancia = laplacian.var()
        
        # Quanto maior a variância, mais nítida a imagem
        if variancia < 50:
            return False, variancia, "Imagem borrada (fora de foco)"
        elif variancia < 100:
            return True, variancia, "Nitidez regular (pode funcionar)"
        else:
            return True, variancia, "Imagem nítida"
    
    @staticmethod
    def validar_tamanho(imagem: np.ndarray) -> Tuple[bool, int, int, str]:
        """Verifica se a imagem tem resolução mínima"""
        altura, largura = imagem.shape[:2]
        resolucao = altura * largura
        
        if resolucao < 300000:  # ~ 500x600 pixels
            return False, altura, largura, f"Imagem muito pequena ({largura}x{altura})"
        else:
            return True, altura, largura, f"Resolução adequada ({largura}x{altura})"
    
    @staticmethod
    def validar_contraste(imagem: np.ndarray) -> Tuple[bool, float, str]:
        """Verifica o contraste da imagem"""
        if len(imagem.shape) == 3:
            gray = cv2.cvtColor(imagem, cv2.COLOR_BGR2GRAY)
        else:
            gray = imagem
        
        contraste = gray.std()
        
        if contraste < 30:
            return False, contraste, "Contraste muito baixo"
        elif contraste < 40:
            return True, contraste, "Contraste regular"
        else:
            return True, contraste, "Bom contraste"
    
    @staticmethod
    def validar_imagem(imagem: np.ndarray) -> Dict:
        """Valida todos os aspectos da imagem"""
        
        resultados = {
            "valida": True,
            "motivos": [],
            "detalhes": {}
        }
        
        # 1. Brilho
        brilho_ok, brilho_valor, brilho_msg = QualityValidator.validar_brilho(imagem)
        resultados["detalhes"]["brilho"] = {"valor": brilho_valor, "msg": brilho_msg}
        if not brilho_ok:
            resultados["valida"] = False
            resultados["motivos"].append(brilho_msg)
        
        # 2. Nitidez
        nitidez_ok, nitidez_valor, nitidez_msg = QualityValidator.validar_nitidez(imagem)
        resultados["detalhes"]["nitidez"] = {"valor": nitidez_valor, "msg": nitidez_msg}
        if not nitidez_ok:
            resultados["valida"] = False
            resultados["motivos"].append(nitidez_msg)
        
        # 3. Tamanho
        tamanho_ok, altura, largura, tamanho_msg = QualityValidator.validar_tamanho(imagem)
        resultados["detalhes"]["tamanho"] = {"altura": altura, "largura": largura, "msg": tamanho_msg}
        if not tamanho_ok:
            resultados["valida"] = False
            resultados["motivos"].append(tamanho_msg)
        
        # 4. Contraste
        contraste_ok, contraste_valor, contraste_msg = QualityValidator.validar_contraste(imagem)
        resultados["detalhes"]["contraste"] = {"valor": contraste_valor, "msg": contraste_msg}
        if not contraste_ok:
            resultados["valida"] = False
            resultados["motivos"].append(contraste_msg)
        
        return resultados
