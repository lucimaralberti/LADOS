"""correcao_visao_v3.py - Pipeline completo com todos os upgrades"""

from services.detector_folha import DetectorFolha
from services.detector_grid import DetectorGrid
from services.score_bolha import ScoreBolha
from services.calibrador_layout import calibrador
import cv2
import numpy as np
import base64
from typing import Dict, List, Optional
from PIL import Image
import io

class CorrecaoVisaoV3:
    """Versão 3 - Scanner inteligente de provas imperfeitas"""
    
    def __init__(self):
        self.detector_folha = DetectorFolha()
        self.detector_grid = DetectorGrid()
        self.score_bolha = ScoreBolha()
    
    def base64_to_image(self, base64_str: str) -> np.ndarray:
        if "," in base64_str:
            base64_str = base64_str.split(",")[1]
        image_data = base64.b64decode(base64_str)
        image = Image.open(io.BytesIO(image_data))
        return cv2.cvtColor(np.array(image), cv2.COLOR_RGB2BGR)
    
    def processar(self, imagem_base64: str, escola_id: str = None) -> Dict:
        """Pipeline completo com todos os upgrades"""
        try:
            imagem = self.base64_to_image(imagem_base64)
            
            # 1. Detecção híbrida de folha
            folha = DetectorFolha.detectar(imagem)
            if folha is None:
                return {"erro": "Não foi possível detectar a folha", "sucesso": False}
            
            # 2. Calibração por escola
            perfil = calibrador.obter_perfil(escola_id) if escola_id else None
            
            # 3. Detecção dinâmica de grade
            grade_info = DetectorGrid.calcular_celulas(folha)
            celulas = grade_info["celulas"]
            
            # 4. Leitura por score probabilístico
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
                
                score = ScoreBolha.calcular_score(roi)
                scores.append(score)
                
                if score >= 0.7:
                    alternativa = chr(65 + coluna)
                    respostas[questao] = alternativa
            
            # 5. Calcular confiança global
            confianca_global = sum(scores) / len(scores) if scores else 0
            
            if confianca_global >= 0.8:
                modo = "automático"
            elif confianca_global >= 0.6:
                modo = "semi_automatico"
            else:
                modo = "revisao_professor"
            
            return {
                "sucesso": True,
                "modo": modo,
                "respostas": respostas,
                "confianca": round(confianca_global, 2),
                "total_detectado": len(respostas),
                "grade_info": grade_info,
                "mensagem": f"Leitura {modo} com {confianca_global*100:.0f}% de confiança"
            }
        except Exception as e:
            return {"erro": str(e), "sucesso": False}
