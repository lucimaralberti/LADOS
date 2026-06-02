"""correcao_visao_v3.py - Pipeline completo com upgrades"""

from services.detector_folha import DetectorFolha
from services.detector_grid import DetectorGrid
from services.score_bolha import ScoreBolha
from services.calibrador_layout import calibrador
from vision.qr_reader import QRReader
import cv2
import numpy as np
import base64
from typing import Dict, List, Optional
from PIL import Image
import io
import json

class CorrecaoVisaoV3:

    def __init__(self):
        self.detector_folha = DetectorFolha()
        self.detector_grid = DetectorGrid()
        self.score_bolha = ScoreBolha()
        self.qr_reader = QRReader()

    def base64_to_image(self, base64_str: str) -> np.ndarray:
        if "," in base64_str:
            base64_str = base64_str.split(",")[1]
        image_data = base64.b64decode(base64_str)
        image = Image.open(io.BytesIO(image_data))
        return cv2.cvtColor(np.array(image), cv2.COLOR_RGB2BGR)

    def processar(self, imagem_base64: str, escola_id: str = None) -> Dict:
        try:
            imagem = self.base64_to_image(imagem_base64)

            folha = DetectorFolha.detectar(imagem)
            if folha is None:
                return {"erro": "NÃ£o foi possÃ­vel detectar a folha", "sucesso": False}

            # Usar o novo QRReader com fallback
            qr_data = self.qr_reader.ler(folha)
            
            if not qr_data:
                return {"erro": "QR Code nÃ£o encontrado ou nÃ£o legÃ­vel", "sucesso": False}
            
            # Tentar extrair gabarito
            try:
                qr_json = json.loads(qr_data)
                gabarito = qr_json.get("gabarito", [])
            except:
                # Tentar formato alternativo
                if "GABARITO:" in qr_data:
                    partes = qr_data.split("|")
                    for parte in partes:
                        if parte.startswith("GABARITO:"):
                            gabarito = parte.replace("GABARITO:", "").split(",")
                            break
                else:
                    gabarito = []
            
            if not gabarito:
                return {"erro": "Gabarito nÃ£o encontrado no QR Code", "sucesso": False}

            perfil = calibrador.obter_perfil(escola_id) if escola_id else None

            grade_info = DetectorGrid.calcular_celulas(folha)
            celulas = grade_info["celulas"]

            respostas = {}
            scores = []

            gray = cv2.cvtColor(folha, cv2.COLOR_BGR2GRAY)

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

                if score >= 0.4:
                    alternativa = chr(65 + coluna)
                    respostas[questao] = alternativa

            return {
                "sucesso": True,
                "gabarito": gabarito,
                "respostas": respostas,
                "total_questoes": len(gabarito),
                "confianca": sum(scores) / len(scores) if scores else 0
            }
        except Exception as e:
            return {"erro": str(e), "sucesso": False}
