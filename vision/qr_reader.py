"""vision/qr_reader.py - Leitor de QR Code com fallback"""

import cv2
import numpy as np
from typing import Optional

class QRReader:
    """Leitor de QR Code com fallback: OpenCV → pyzbar"""
    
    def __init__(self):
        self.pyzbar_disponivel = False
        
        # Tentar importar pyzbar (fallback)
        try:
            from pyzbar.pyzbar import decode
            self.pyzbar_decode = decode
            self.pyzbar_disponivel = True
        except ImportError:
            pass
    
    def ler(self, imagem) -> Optional[str]:
        """Tenta ler QR Code com OpenCV primeiro, depois pyzbar"""
        
        # Método 1: OpenCV QRDetector (nativo, rápido)
        try:
            detector = cv2.QRCodeDetector()
            dados, _, _ = detector.detectAndDecode(imagem)
            if dados:
                return dados
        except:
            pass
        
        # Método 2: pyzbar (fallback para QR difíceis)
        if self.pyzbar_disponivel:
            try:
                from PIL import Image
                if isinstance(imagem, np.ndarray):
                    imagem_pil = Image.fromarray(cv2.cvtColor(imagem, cv2.COLOR_BGR2RGB))
                else:
                    imagem_pil = imagem
                
                qrcodes = self.pyzbar_decode(imagem_pil)
                if qrcodes:
                    return qrcodes[0].data.decode('utf-8')
            except:
                pass
        
        return None
