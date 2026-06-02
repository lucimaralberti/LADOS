"""
services/calibrador_layout.py
Sistema de calibração automática de layout - Aprende offsets de qualquer impressão
"""

import cv2
import numpy as np
from typing import Dict, Tuple, Optional, List
from dataclasses import dataclass
import json
from pathlib import Path
from utils.logger import get_logger

logger = get_logger(__name__)

@dataclass
class LayoutProfile:
    """Perfil de layout calibrado para uma escola/turma"""
    escala_x: float = 1.0
    escala_y: float = 1.0
    offset_x: int = 0
    offset_y: int = 0
    rotacao: float = 0.0
    grade_x_inicio: int = 400
    grade_y_inicio: int = 2200
    bolha_raio: int = 15
    bolha_espacamento_x: int = 45
    bolha_espacamento_y: int = 60
    confianca: float = 0.0
    data_calibracao: str = ""

class CalibradorLayout:
    """Calibra automaticamente o layout baseado em uma imagem de referência"""
    
    def __init__(self):
        self.perfil_padrao = LayoutProfile()
        self.cache_perfis: Dict[str, LayoutProfile] = {}
        self._carregar_perfis()
    
    def _carregar_perfis(self):
        """Carrega perfis salvos anteriormente"""
        arquivo = Path("data/layout_profiles.json")
        if arquivo.exists():
            try:
                with open(arquivo, "r", encoding="utf-8") as f:
                    dados = json.load(f)
                for key, value in dados.items():
                    perfil = LayoutProfile(**value)
                    self.cache_perfis[key] = perfil
                logger.info(f"Carregados {len(self.cache_perfis)} perfis de layout")
            except Exception as e:
                logger.error(f"Erro ao carregar perfis: {e}")
    
    def _salvar_perfis(self):
        """Salva perfis calibrados"""
        arquivo = Path("data/layout_profiles.json")
        try:
            arquivo.parent.mkdir(parents=True, exist_ok=True)
            dados = {k: v.__dict__ for k, v in self.cache_perfis.items()}
            with open(arquivo, "w", encoding="utf-8") as f:
                json.dump(dados, f, indent=2, ensure_ascii=False)
            logger.info(f"Salvos {len(self.cache_perfis)} perfis")
        except Exception as e:
            logger.error(f"Erro ao salvar perfis: {e}")
    
    def detectar_marcadores(self, imagem: np.ndarray, debug: bool = False) -> List[Tuple[int, int]]:
        """Detecta os 4 marcadores fiduciais com busca adaptativa"""
        gray = cv2.cvtColor(imagem, cv2.COLOR_BGR2GRAY)
        
        # Múltiplos thresholds para diferentes condições de iluminação
        thresholds = [50, 80, 100, 120]
        melhores_marcadores = []
        melhor_qualidade = 0
        
        for thresh_val in thresholds:
            _, thresh = cv2.threshold(gray, thresh_val, 255, cv2.THRESH_BINARY_INV)
            contornos, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            
            marcadores = []
            for c in contornos:
                area = cv2.contourArea(c)
                # Tolerância ampliada para diferentes resoluções
                if 800 < area < 8000:
                    x, y, w, h = cv2.boundingRect(c)
                    aspect_ratio = w / float(h)
                    if 0.7 < aspect_ratio < 1.3:
                        centro = (x + w//2, y + h//2)
                        marcadores.append(centro)
            
            # Verificar se encontrou 4 marcadores nos cantos
            if len(marcadores) >= 4:
                qualidade = len(marcadores)
                if qualidade > melhor_qualidade:
                    melhor_qualidade = qualidade
                    melhores_marcadores = marcadores[:4]
        
        return melhores_marcadores
    
    def calcular_offset_escala(self, imagem: np.ndarray, perfil_base: LayoutProfile = None) -> LayoutProfile:
        """Calcula offsets e escala real baseado na imagem"""
        if perfil_base is None:
            perfil_base = self.perfil_padrao
        
        marcadores = self.detectar_marcadores(imagem)
        
        if len(marcadores) < 4:
            logger.warning(f"Apenas {len(marcadores)} marcadores detectados")
            perfil_base.confianca = len(marcadores) / 4
            return perfil_base
        
        # Ordenar marcadores (tL, tR, bL, bR)
        marcadores.sort(key=lambda m: (m[1], m[0]))
        
        if len(marcadores) >= 4:
            tL, tR, bL, bR = marcadores[0], marcadores[1], marcadores[2], marcadores[3]
            
            # Calcular escala real
            largura_esperada = perfil_base.grade_x_inicio + (20 * perfil_base.bolha_espacamento_x)
            altura_esperada = perfil_base.grade_y_inicio + (20 * perfil_base.bolha_espacamento_y)
            
            largura_real = abs(tR[0] - tL[0])
            altura_real = abs(bL[1] - tL[1])
            
            perfil_base.escala_x = largura_real / largura_esperada if largura_esperada > 0 else 1.0
            perfil_base.escala_y = altura_real / altura_esperada if altura_esperada > 0 else 1.0
            
            # Calcular offset (deslocamento do primeiro marcador)
            perfil_base.offset_x = tL[0] - perfil_base.grade_x_inicio
            perfil_base.offset_y = tL[1] - perfil_base.grade_y_inicio
            
            # Ajustar parâmetros com escala
            perfil_base.grade_x_inicio = int(perfil_base.grade_x_inicio * perfil_base.escala_x)
            perfil_base.grade_y_inicio = int(perfil_base.grade_y_inicio * perfil_base.escala_y)
            perfil_base.bolha_raio = int(perfil_base.bolha_raio * min(perfil_base.escala_x, perfil_base.escala_y))
            perfil_base.bolha_espacamento_x = int(perfil_base.bolha_espacamento_x * perfil_base.escala_x)
            perfil_base.bolha_espacamento_y = int(perfil_base.bolha_espacamento_y * perfil_base.escala_y)
            
            perfil_base.confianca = 1.0
            from datetime import datetime
            perfil_base.data_calibracao = datetime.now().isoformat()
            
            logger.info(f"Layout calibrado: escala=({perfil_base.escala_x:.2f}, {perfil_base.escala_y:.2f}), "
                       f"offset=({perfil_base.offset_x}, {perfil_base.offset_y})")
        
        return perfil_base
    
    def calibrar_para_escola(self, escola_id: str, imagem_base64: str) -> LayoutProfile:
        """Calibra o layout para uma escola específica"""
        from services.correcao_visao import CorrecaoVisaoService
        visao = CorrecaoVisaoService()
        
        imagem = visao.base64_to_image(imagem_base64)
        perfil = self.calcular_offset_escala(imagem)
        
        self.cache_perfis[escola_id] = perfil
        self._salvar_perfis()
        
        return perfil
    
    def obter_perfil(self, escola_id: str) -> LayoutProfile:
        """Obtém perfil calibrado para uma escola (ou retorna padrão)"""
        if escola_id in self.cache_perfis:
            return self.cache_perfis[escola_id]
        return self.perfil_padrao
    
    def aplicar_perfil(self, grade: np.ndarray, perfil: LayoutProfile) -> np.ndarray:
        """Aplica correções de escala e offset à grade"""
        if perfil.escala_x != 1.0 or perfil.escala_y != 1.0:
            nova_largura = int(grade.shape[1] * perfil.escala_x)
            nova_altura = int(grade.shape[0] * perfil.escala_y)
            grade = cv2.resize(grade, (nova_largura, nova_altura))
        
        return grade

# Instância global
calibrador = CalibradorLayout()
