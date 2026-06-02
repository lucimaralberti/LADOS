"""
Leitura de QR Code para correção de provas
"""

import cv2
import numpy as np
from pyzbar.pyzbar import decode


def ler_qrcode(imagem):
    """
    Lê QR Code de uma imagem
    """
    try:
        # Converter para escada de cinza se necessário
        if len(imagem.shape) == 3:
            gray = cv2.cvtColor(imagem, cv2.COLOR_BGR2GRAY)
        else:
            gray = imagem
        
        # Detectar QR Code
        qr_codes = decode(gray)
        
        if qr_codes:
            qr_data = qr_codes[0].data.decode('utf-8')
            # Formato esperado: exam_id|turma|data
            partes = qr_data.split('|')
            if len(partes) >= 1:
                return {
                    "success": True,
                    "exam_id": partes[0],
                    "turma": partes[1] if len(partes) > 1 else "",
                    "data": partes[2] if len(partes) > 2 else "",
                    "raw_data": qr_data
                }
        
        return {"success": False, "error": "QR Code não encontrado"}
    
    except Exception as e:
        return {"success": False, "error": str(e)}
