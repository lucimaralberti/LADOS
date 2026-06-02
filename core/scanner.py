"""core/scanner.py - Orquestrador de correção"""

import cv2
import numpy as np
from pathlib import Path
import sys

# Adicionar caminho para imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from vision.qr_reader import QRReader
from vision.omr_reader import OMRReader
from services.detector_folha import DetectorFolha
from services.detector_grid import DetectorGrid
from services.score_bolha import ScoreBolha


class Corrector:
    """Orquestrador completo da correção de provas"""
    
    def __init__(self):
        self.qr_reader = QRReader()
        self.omr_reader = OMRReader()
        self.detector_folha = DetectorFolha()
        self.detector_grid = DetectorGrid()
        self.score_bolha = ScoreBolha()
    
    def corrigir(self, imagem_base64: str) -> dict:
        """Pipeline completo de correção"""
        try:
            # Converter base64 para imagem
            import base64
            import io
            from PIL import Image
            
            if "," in imagem_base64:
                imagem_base64 = imagem_base64.split(",")[1]
            image_data = base64.b64decode(imagem_base64)
            imagem_pil = Image.open(io.BytesIO(image_data))
            imagem = cv2.cvtColor(np.array(imagem_pil), cv2.COLOR_RGB2BGR)
            
            # Detectar folha
            folha = DetectorFolha.detectar(imagem)
            if folha is None:
                return {"sucesso": False, "erro": "Não foi possível detectar a folha"}
            
            # Ler QR Code
            qr_data = self.qr_reader.ler(folha)
            if not qr_data:
                return {"sucesso": False, "erro": "QR Code não encontrado ou não legível"}
            
            gabarito = qr_data.get("gabarito", [])
            
            # Detectar grade
            grade_info = DetectorGrid.calcular_celulas(folha)
            celulas = grade_info["celulas"]
            
            # Ler respostas
            gray = cv2.cvtColor(folha, cv2.COLOR_BGR2GRAY)
            respostas = {}
            scores = []
            
            for (questao, coluna), (cx, cy, raio) in celulas.items():
                x1 = max(0, cx - raio)
                y1 = max(0, cy - raio)
                x2 = min(folha.shape[1], cx + raio)
                y2 = min(folha.shape[0], cy + raio)
                
                roi = gray[y1:y2, x1:x2]
                if roi.size == 0:
                    continue
                
                score = self.score_bolha.calcular_score(roi)
                scores.append(score)
                
                if score >= 0.7:
                    alternativa = chr(65 + coluna)
                    respostas[questao] = alternativa
            
            # Calcular acertos
            total = len(gabarito)
            acertos = 0
            for i, gab in enumerate(gabarito, 1):
                if respostas.get(str(i)) == gab:
                    acertos += 1
            
            percentual = (acertos / total) * 100 if total > 0 else 0
            
            return {
                "sucesso": True,
                "gabarito": gabarito,
                "respostas": respostas,
                "total": total,
                "acertos": acertos,
                "percentual": percentual,
                "confianca": sum(scores) / len(scores) if scores else 0
            }
            
        except Exception as e:
            return {"sucesso": False, "erro": str(e)}
