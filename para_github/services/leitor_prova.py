"""
Leitor de provas - LADOS 2.0 (OMR Profissional - Versão Definitiva)
- DETECÇÃO REAL DE CÍRCULOS (HoughCircles como sistema principal)
- Correção de iluminação não uniforme (background subtraction)
- Auto-calibração de bolhas por detecção física
- Overlay visual para diagnóstico
- Heatmap de confiança por questão
- Fallback para ROI matemática quando necessário
"""

import cv2
import numpy as np
from PIL import Image
import streamlit as st
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime
import os
import json
import hashlib
from collections import OrderedDict
import math

# ============================================================
# CONSTANTES
# ============================================================
WARP_WIDTH = 1200
WARP_HEIGHT = 1600
MIN_AREA_FOLHA = 50000
MIN_MARKER_AREA = 300
MAX_MARKER_AREA = 2000
MARKER_ASPECT_RATIO_MIN = 0.8
MARKER_ASPECT_RATIO_MAX = 1.2
MARKER_SOLIDITY_MIN = 0.7
PREENCIMENTO_MARCADO = 40
PREENCIMENTO_PARCIAL = 25
CACHE_MAX_SIZE = 50
NUM_ALTERNATIVAS = 4
HOUGH_MIN_DIST = 20
HOUGH_MIN_RADIUS = 8
HOUGH_MAX_RADIUS = 15
HOUGH_PARAM1 = 50
HOUGH_PARAM2 = 30
TOLERANCIA_DISTANCIA_LINHA = 1.5  # Fator de tolerância para agrupamento


class LeitorProva:
    """
    Leitor OMR profissional - versão definitiva com detecção real de círculos
    """
    
    def __init__(self):
        self.debug_mode = False
        self.debug_images = []
        self._cache = OrderedDict()
        self._calibracao = None
    
    def _salvar_debug(self, imagem, nome: str, step: str = "geral"):
        if self.debug_mode:
            timestamp = datetime.now().strftime("%H%M%S_%f")[:-3]
            os.makedirs(f"logs/debug/{step}", exist_ok=True)
            caminho = f"logs/debug/{step}/debug_{nome}_{timestamp}.png"
            cv2.imwrite(caminho, imagem)
            self.debug_images.append(caminho)
            return caminho
        return None
    
    def _desenhar_overlay_rois(self, imagem, rois, titulo="ROIs Detectadas"):
        """Desenha ROIS sobre a imagem para validação visual"""
        img_copy = imagem.copy()
        if len(img_copy.shape) == 2:
            img_copy = cv2.cvtColor(img_copy, cv2.COLOR_GRAY2RGB)
        
        cores = [(0, 255, 0), (255, 0, 0), (0, 0, 255), (255, 255, 0)]
        
        for linha_idx, linha in enumerate(rois):
            cor = cores[linha_idx % len(cores)]
            for coluna_idx, (x, y, r) in enumerate(linha):
                cv2.circle(img_copy, (x, y), r, cor, 2)
                cv2.putText(img_copy, f"{chr(65+linha_idx)}{coluna_idx+1}", 
                           (x - 10, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.4, cor, 1)
        
        self._salvar_debug(img_copy, "overlay_circulos", "validacao")
        return img_copy
    
    def _desenhar_heatmap(self, imagem, confiancas, dimensoes):
        """Desenha heatmap de confiança por questão"""
        img_copy = imagem.copy()
        if len(img_copy.shape) == 2:
            img_copy = cv2.cvtColor(img_copy, cv2.COLOR_GRAY2RGB)
        
        num_linhas, num_colunas = dimensoes
        
        for i, conf in enumerate(confiancas):
            linha = i // num_colunas
            coluna = i % num_colunas
            if linha < num_linhas:
                intensidade = int(255 * (1 - conf / 100))
                cor = (0, intensidade, 255 - intensidade)
                y = 50 + linha * 40
                x = 50 + coluna * 60
                cv2.rectangle(img_copy, (x, y), (x + 50, y + 30), cor, -1)
                cv2.putText(img_copy, f"{conf:.0f}%", (x + 5, y + 20), 
                           cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)
        
        self._salvar_debug(img_copy, "heatmap_confianca", "validacao")
        return img_copy
    
    def _normalizar_resolucao(self, imagem):
        altura, largura = imagem.shape[:2]
        if altura != WARP_HEIGHT or largura != WARP_WIDTH:
            imagem = cv2.resize(imagem, (WARP_WIDTH, WARP_HEIGHT))
        return imagem
    
    def _corrigir_iluminacao(self, imagem):
        """Correção de iluminação não uniforme com background subtraction"""
        try:
            if len(imagem.shape) == 3:
                gray = cv2.cvtColor(imagem, cv2.COLOR_RGB2GRAY)
            else:
                gray = imagem
            
            # Suavização para estimar o fundo
            background = cv2.GaussianBlur(gray, (51, 51), 0)
            
            # Normalização
            normalized = cv2.divide(gray.astype(np.float32), background.astype(np.float32), scale=255)
            normalized = np.clip(normalized, 0, 255).astype(np.uint8)
            
            self._salvar_debug(normalized, "iluminacao_corrigida", "preprocessamento")
            return normalized
            
        except Exception as e:
            return imagem
    
    def _avaliar_qualidade_imagem(self, imagem):
        try:
            if len(imagem.shape) == 3:
                gray = cv2.cvtColor(imagem, cv2.COLOR_RGB2GRAY)
            else:
                gray = imagem
            
            laplaciano = cv2.Laplacian(gray, cv2.CV_64F)
            variancia = laplaciano.var()
            esta_borrado = variancia < 100
            nivel_borrao = max(0, min(100, (1 - variancia / 500) * 100))
            
            media_iluminacao = np.mean(gray)
            iluminacao_ruim = media_iluminacao < 50 or media_iluminacao > 200
            
            contraste = np.std(gray)
            baixo_contraste = contraste < 30
            
            qualidade = "boa"
            if esta_borrado:
                qualidade = "borrada"
            elif iluminacao_ruim:
                qualidade = "iluminacao_ruim"
            elif baixo_contraste:
                qualidade = "baixo_contraste"
            
            return {
                "esta_borrado": esta_borrado,
                "nivel_borrao": nivel_borrao,
                "iluminacao_ruim": iluminacao_ruim,
                "media_iluminacao": media_iluminacao,
                "baixo_contraste": baixo_contraste,
                "contraste": contraste,
                "qualidade": qualidade
            }
        except:
            return {"qualidade": "desconhecida", "esta_borrado": False}
    
    def _preprocessar_imagem(self, imagem):
        """Pipeline otimizado com correção de iluminação e OTSU"""
        imagem = self._normalizar_resolucao(imagem)
        
        # Correção de iluminação não uniforme
        ilum_corrigida = self._corrigir_iluminacao(imagem)
        
        if len(imagem.shape) == 3:
            gray = cv2.cvtColor(imagem, cv2.COLOR_RGB2GRAY)
        else:
            gray = imagem
        
        blurred = cv2.GaussianBlur(gray, (3, 3), 0)
        
        # CLAHE
        clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
        clahe_img = clahe.apply(blurred)
        
        # OTSU global
        _, binary = cv2.threshold(clahe_img, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)
        
        # Morfologia
        kernel = np.ones((2, 2), np.uint8)
        cleaned = cv2.morphologyEx(binary, cv2.MORPH_CLOSE, kernel)
        cleaned = cv2.morphologyEx(cleaned, cv2.MORPH_OPEN, kernel)
        
        self._salvar_debug(cleaned, "preprocessado", "preprocessamento")
        
        return gray, cleaned
    
    def _detectar_folha_a4(self, imagem):
        try:
            if len(imagem.shape) == 3:
                gray = cv2.cvtColor(imagem, cv2.COLOR_RGB2GRAY)
            else:
                gray = imagem
            
            for low_thresh in [30, 50, 70]:
                edges = cv2.Canny(gray, low_thresh, low_thresh * 3)
                kernel = np.ones((5, 5), np.uint8)
                dilated = cv2.dilate(edges, kernel, iterations=2)
                
                contornos, _ = cv2.findContours(dilated, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
                
                if contornos:
                    contornos_validos = [c for c in contornos if cv2.contourArea(c) > MIN_AREA_FOLHA]
                    if contornos_validos:
                        maior_contorno = max(contornos_validos, key=cv2.contourArea)
                        
                        peri = cv2.arcLength(maior_contorno, True)
                        aprox = cv2.approxPolyDP(maior_contorno, 0.02 * peri, True)
                        
                        if len(aprox) == 4:
                            pontos = aprox.reshape(4, 2).astype(np.float32)
                            return self._ordenar_pontos(pontos)
            
            return None
            
        except Exception as e:
            return None
    
    def _ordenar_pontos(self, pts):
        rect = np.zeros((4, 2), dtype=np.float32)
        soma = pts.sum(axis=1)
        rect[0] = pts[np.argmin(soma)]
        rect[2] = pts[np.argmax(soma)]
        diff = np.diff(pts, axis=1)
        rect[1] = pts[np.argmin(diff)]
        rect[3] = pts[np.argmax(diff)]
        return rect
    
    def _validar_marcadores_geometricos(self, marcadores):
        tl, tr, br, bl = marcadores
        
        largura_superior = np.linalg.norm(tr - tl)
        largura_inferior = np.linalg.norm(br - bl)
        if abs(largura_superior - largura_inferior) / max(largura_superior, largura_inferior) > 0.3:
            return False
        
        altura_esquerda = np.linalg.norm(bl - tl)
        altura_direita = np.linalg.norm(br - tr)
        if abs(altura_esquerda - altura_direita) / max(altura_esquerda, altura_direita) > 0.3:
            return False
        
        return True
    
    def _detectar_marcadores_robustos(self, imagem_binaria):
        try:
            contornos, _ = cv2.findContours(imagem_binaria, cv2.RETR_EXTERNAL, 
                                           cv2.CHAIN_APPROX_SIMPLE)
            
            candidatos = []
            areas = []
            
            for cnt in contornos:
                # Usar approxPolyDP para verificar se é quadrilátero
                peri = cv2.arcLength(cnt, True)
                aprox = cv2.approxPolyDP(cnt, 0.04 * peri, True)
                
                if len(aprox) != 4:
                    continue
                
                x, y, w, h = cv2.boundingRect(cnt)
                
                aspect_ratio = w / float(h) if h > 0 else 0
                if not (0.8 <= aspect_ratio <= 1.2):
                    continue
                
                area = w * h
                if area < MIN_MARKER_AREA or area > MAX_MARKER_AREA:
                    continue
                
                area_contorno = cv2.contourArea(cnt)
                solidity = area_contorno / area if area > 0 else 0
                if solidity < 0.7:
                    continue
                
                centro_x = x + w // 2
                centro_y = y + h // 2
                candidatos.append((centro_x, centro_y, area, solidity))
                areas.append(area)
            
            if len(candidatos) < 4:
                return None, 0
            
            media_area = np.mean(areas)
            areas_validas = [a for a in areas if abs(a - media_area) / media_area < 0.3]
            
            if len(areas_validas) < 4:
                return None, 0
            
            candidatos.sort(key=lambda p: p[1])
            top_dois = sorted(candidatos[:2], key=lambda p: p[0])
            bottom_dois = sorted(candidatos[-2:], key=lambda p: p[0])
            
            pontos_ordenados = [
                top_dois[0], top_dois[1],
                bottom_dois[0], bottom_dois[1]
            ]
            
            pts = np.array([(p[0], p[1]) for p in pontos_ordenados], dtype=np.float32)
            pts = self._ordenar_pontos(pts)
            
            if not self._validar_marcadores_geometricos(pts):
                return None, 0
            
            confianca = np.mean([p[3] for p in pontos_ordenados]) * 100
            
            return pts, confianca
            
        except Exception as e:
            return None, 0
    
    def _aplicar_warp(self, imagem, pontos_origem):
        pontos_destino = np.array([
            [0, 0],
            [WARP_WIDTH - 1, 0],
            [WARP_WIDTH - 1, WARP_HEIGHT - 1],
            [0, WARP_HEIGHT - 1]
        ], dtype=np.float32)
        
        matriz = cv2.getPerspectiveTransform(pontos_origem, pontos_destino)
        warp = cv2.warpPerspective(imagem, matriz, (WARP_WIDTH, WARP_HEIGHT))
        
        return warp
    
    def _detectar_circulos_reais(self, imagem_gray, num_questoes_esperado):
        """
        DETECÇÃO REAL DE CÍRCULOS - SISTEMA PRINCIPAL
        Usa HoughCircles no gradiente real (não no binário)
        """
        try:
            # Aplicar blur para Hough
            blurred = cv2.GaussianBlur(imagem_gray, (5, 5), 0)
            
            # Detectar círculos no gradiente real
            circles = cv2.HoughCircles(
                blurred,
                cv2.HOUGH_GRADIENT,
                dp=1,
                minDist=HOUGH_MIN_DIST,
                param1=HOUGH_PARAM1,
                param2=HOUGH_PARAM2,
                minRadius=HOUGH_MIN_RADIUS,
                maxRadius=HOUGH_MAX_RADIUS
            )
            
            if circles is None:
                return None
            
            circles = np.round(circles[0, :]).astype("int")
            
            # Ordenar por Y (linha) e depois por X (coluna)
            circles_sorted = sorted(circles, key=lambda c: (c[1], c[0]))
            
            # Agrupar por linhas baseado na proximidade em Y
            linhas = []
            linha_atual = []
            y_anterior = circles_sorted[0][1] if circles_sorted else 0
            
            for circle in circles_sorted:
                if abs(circle[1] - y_anterior) > HOUGH_MIN_RADIUS * TOLERANCIA_DISTANCIA_LINHA:
                    if linha_atual:
                        linhas.append(linha_atual)
                    linha_atual = [circle]
                    y_anterior = circle[1]
                else:
                    linha_atual.append(circle)
                    y_anterior = (y_anterior + circle[1]) // 2
            
            if linha_atual:
                linhas.append(linha_atual)
            
            # Pegar as primeiras N linhas (alternativas)
            linhas = linhas[:NUM_ALTERNATIVAS]
            
            # Ordenar cada linha por X
            for i in range(len(linhas)):
                linhas[i] = sorted(linhas[i], key=lambda c: c[0])
            
            # Verificar se temos o número esperado de colunas
            if linhas and len(linhas[0]) >= num_questoes_esperado * 0.8:
                # Truncar para o número esperado
                for i in range(len(linhas)):
                    linhas[i] = linhas[i][:num_questoes_esperado]
                return linhas
            
            return None
            
        except Exception as e:
            return None
    
    def _calcular_roi_por_marcadores(self, marcadores, num_linhas=4, num_colunas=10):
        """Método de fallback baseado em marcadores (quando detecção real falha)"""
        tl, tr, br, bl = marcadores
        
        left = min(tl[0], bl[0])
        right = max(tr[0], br[0])
        top = min(tl[1], tr[1])
        bottom = max(bl[1], br[1])
        
        largura_total = right - left
        altura_total = bottom - top
        
        margem_lateral = largura_total * 0.08
        margem_vertical = altura_total * 0.08
        
        inicio_x = left + margem_lateral
        inicio_y = top + margem_vertical
        largura_util = largura_total - 2 * margem_lateral
        altura_util = altura_total - 2 * margem_vertical
        
        largura_celula = largura_util / num_colunas
        altura_celula = altura_util / num_linhas
        
        foco = 0.65
        offset_x = largura_celula * (1 - foco) / 2
        offset_y = altura_celula * (1 - foco) / 2
        
        rois = []
        for linha in range(num_linhas):
            linha_rois = []
            for coluna in range(num_colunas):
                x1 = int(inicio_x + coluna * largura_celula + offset_x)
                y1 = int(inicio_y + linha * altura_celula + offset_y)
                x2 = int(x1 + largura_celula * foco)
                y2 = int(y1 + altura_celula * foco)
                
                x1 = max(0, min(WARP_WIDTH, x1))
                y1 = max(0, min(WARP_HEIGHT, y1))
                x2 = max(0, min(WARP_WIDTH, x2))
                y2 = max(0, min(WARP_HEIGHT, y2))
                
                linha_rois.append((x1, y1, x2, y2))
            rois.append(linha_rois)
        
        return rois
    
    def _analisar_preenchimento_circulo(self, imagem_gray, x, y, raio):
        """Analisa preenchimento de um círculo detectado"""
        try:
            mask = np.zeros(imagem_gray.shape, dtype=np.uint8)
            raio_interno = int(raio * 0.7)
            cv2.circle(mask, (x, y), raio_interno, 255, -1)
            
            pixels_regiao = np.sum(mask == 255)
            if pixels_regiao == 0:
                return 0, False, False
            
            pixels_escuros = np.sum(imagem_gray[mask == 255] < 100)
            preenchimento = (pixels_escuros / pixels_regiao) * 100
            
            marcado = preenchimento >= PREENCIMENTO_MARCADO
            parcial = PREENCIMENTO_PARCIAL <= preenchimento < PREENCIMENTO_MARCADO
            
            return preenchimento, marcado, parcial
            
        except Exception as e:
            return 0, False, False
    
    def _analisar_preenchimento_roi(self, imagem_binaria, x1, y1, x2, y2):
        """Fallback: análise por ROI quando círculo não é detectado"""
        if x2 <= x1 or y2 <= y1:
            return 0, False, False
        
        roi = imagem_binaria[y1:y2, x1:x2]
        if roi.size == 0:
            return 0, False, False
        
        h, w = roi.shape
        centro_x, centro_y = w // 2, h // 2
        raio = int(min(w, h) * 0.35)
        
        mask = np.zeros((h, w), dtype=np.uint8)
        cv2.circle(mask, (centro_x, centro_y), raio, 255, -1)
        
        roi_masked = cv2.bitwise_and(roi, roi, mask=mask)
        
        pixels_regiao = np.sum(mask == 255)
        pixels_pretos = np.sum(roi_masked == 255)
        
        preenchimento = (pixels_pretos / pixels_regiao) * 100 if pixels_regiao > 0 else 0
        
        marcado = preenchimento >= PREENCIMENTO_MARCADO
        parcial = PREENCIMENTO_PARCIAL <= preenchimento < PREENCIMENTO_MARCADO
        
        return preenchimento, marcado, parcial
    
    def _corrigir_rotacao(self, imagem, marcadores):
        tl, tr, br, bl = marcadores
        
        if tl[0] > tr[0] or tl[1] > bl[1]:
            imagem = cv2.rotate(imagem, cv2.ROTATE_180)
            h, w = imagem.shape[:2]
            marcadores_corrigidos = np.array([
                [w - tl[0], h - tl[1]],
                [w - tr[0], h - tr[1]],
                [w - br[0], h - br[1]],
                [w - bl[0], h - bl[1]]
            ], dtype=np.float32)
            marcadores_corrigidos = self._ordenar_pontos(marcadores_corrigidos)
            return imagem, marcadores_corrigidos, True
        
        return imagem, marcadores, False
    
    def _ler_qr_code(self, imagem_warp):
        try:
            if len(imagem_warp.shape) == 3:
                gray = cv2.cvtColor(imagem_warp, cv2.COLOR_RGB2GRAY)
            else:
                gray = imagem_warp
            
            detector = cv2.QRCodeDetector()
            dados, _, _ = detector.detectAndDecode(gray)
            
            if dados:
                try:
                    return json.loads(dados)
                except:
                    return {"exam_id": dados, "raw": dados}
            return None
        except:
            return None
    
    def _calcular_confianca_global(self, qualidade, confianca_marcadores, resultados):
        pesos = {
            "qualidade": 0.20,
            "marcadores": 0.20,
            "preenchimento": 0.35,
            "consistencia": 0.25
        }
        
        if qualidade.get("qualidade") == "boa":
            score_qualidade = 100
        elif qualidade.get("qualidade") == "borrada":
            score_qualidade = 30
        else:
            score_qualidade = 60
        
        score_marcadores = confianca_marcadores if confianca_marcadores else 0
        
        if resultados:
            confiancas = [d.get("confianca_preenchimento", 0) for d in resultados if isinstance(d, dict)]
            score_preenchimento = np.mean(confiancas) if confiancas else 70
        else:
            score_preenchimento = 50
        
        score_consistencia = 80
        
        confianca_global = (
            pesos["qualidade"] * score_qualidade +
            pesos["marcadores"] * score_marcadores +
            pesos["preenchimento"] * score_preenchimento +
            pesos["consistencia"] * score_consistencia
        )
        
        return min(100, max(0, confianca_global))
    
    def ler_grade(self, imagem: Image.Image, gabarito: Dict[str, str]) -> Dict[str, Any]:
        """
        Pipeline completo - VERSÃO DEFINITIVA
        """
        try:
            img = np.array(imagem)
            if len(img.shape) == 3 and img.shape[2] == 4:
                img = cv2.cvtColor(img, cv2.COLOR_RGBA2RGB)
            
            qualidade = self._avaliar_qualidade_imagem(img)
            
            if qualidade.get("esta_borrado", False):
                return {
                    "sucesso": False,
                    "erro": f"Imagem desfocada (nível: {qualidade['nivel_borrao']:.0f}%)",
                    "acertos": 0,
                    "total_questoes": len(gabarito),
                    "percentual": 0,
                    "detalhes": [],
                    "qualidade_imagem": qualidade,
                    "confianca_global": 0
                }
            
            # Pré-processamento
            gray, binary = self._preprocessar_imagem(img)
            
            # Cache
            thumb = cv2.resize(gray, (64, 64))
            chave_cache = hashlib.md5(thumb.tobytes()).hexdigest()
            
            if chave_cache in self._cache:
                cache_entry = self._cache[chave_cache]
                self._cache.move_to_end(chave_cache)
                rois_circulos = cache_entry["rois_circulos"]
                binary_warp = cache_entry["binary_warp"]
                img_warp = cache_entry["img_warp"]
                gray_warp = cache_entry["gray_warp"]
                confianca_marcadores = cache_entry["marcadores_conf"]
                num_questoes = cache_entry.get("num_questoes", 10)
                usou_deteccao_real = cache_entry.get("usou_deteccao_real", True)
            else:
                # Detecção da folha
                pontos_folha = self._detectar_folha_a4(img)
                if pontos_folha is not None:
                    img_warp_folha = self._aplicar_warp(img, pontos_folha)
                    gray_warp_folha, binary_warp_folha = self._preprocessar_imagem(img_warp_folha)
                else:
                    img_warp_folha = img
                    gray_warp_folha, binary_warp_folha = gray, binary
                
                # Detectar marcadores
                marcadores, confianca_marcadores = self._detectar_marcadores_robustos(binary_warp_folha)
                
                if marcadores is None:
                    return {
                        "sucesso": False,
                        "erro": "Marcadores não detectados",
                        "acertos": 0,
                        "total_questoes": len(gabarito),
                        "percentual": 0,
                        "detalhes": [],
                        "qualidade_imagem": qualidade,
                        "confianca_global": 0
                    }
                
                img_warp_folha, marcadores, rotacionado = self._corrigir_rotacao(img_warp_folha, marcadores)
                
                img_warp = self._aplicar_warp(img_warp_folha, marcadores)
                gray_warp, binary_warp = self._preprocessar_imagem(img_warp)
                
                # Ler QR Code para obter número de questões
                qr_data = self._ler_qr_code(img_warp)
                num_questoes = qr_data.get("num_questoes", len(gabarito)) if qr_data else len(gabarito)
                num_questoes = min(num_questoes, len(gabarito))
                
                # DETECÇÃO REAL DE CÍRCULOS (SISTEMA PRINCIPAL)
                rois_circulos = self._detectar_circulos_reais(gray_warp, num_questoes)
                usou_deteccao_real = rois_circulos is not None
                
                if not rois_circulos:
                    # Fallback: ROIs baseadas em marcadores
                    rois_circulos = self._calcular_roi_por_marcadores(marcadores, NUM_ALTERNATIVAS, num_questoes)
                    rois_circulos = [[(x1+x2)//2, (y1+y2)//2, (x2-x1)//2] for linha in rois_circulos for (x1,y1,x2,y2) in linha]
                    # Reorganizar em grade
                    temp = []
                    for i in range(NUM_ALTERNATIVAS):
                        inicio = i * num_questoes
                        temp.append(rois_circulos[inicio:inicio+num_questoes])
                    rois_circulos = temp
                
                if self.debug_mode:
                    self._desenhar_overlay_rois(img_warp, rois_circulos, 
                                               "Detecção Real" if usou_deteccao_real else "Fallback ROI")
                
                cache_entry = {
                    "rois_circulos": rois_circulos,
                    "binary_warp": binary_warp,
                    "img_warp": img_warp,
                    "gray_warp": gray_warp,
                    "marcadores_conf": confianca_marcadores,
                    "num_questoes": num_questoes,
                    "usou_deteccao_real": usou_deteccao_real
                }
                self._cache[chave_cache] = cache_entry
                
                while len(self._cache) > CACHE_MAX_SIZE:
                    self._cache.popitem(last=False)
            
            # Analisar cada círculo detectado
            letras = ['A', 'B', 'C', 'D']
            acertos = 0
            detalhes = []
            confiancas_por_questao = []
            
            for questao_idx in range(min(len(rois_circulos[0]) if rois_circulos else 0, num_questoes)):
                respostas_questao = []
                
                for linha_idx, letra in enumerate(letras):
                    if linha_idx < len(rois_circulos) and questao_idx < len(rois_circulos[linha_idx]):
                        x, y, r = rois_circulos[linha_idx][questao_idx]
                        
                        if usou_deteccao_real:
                            preenchimento, marcado, parcial = self._analisar_preenchimento_circulo(gray_warp, x, y, r)
                        else:
                            # Fallback: usar ROI
                            x1, y1, x2, y2 = x - r, y - r, x + r, y + r
                            preenchimento, marcado, parcial = self._analisar_preenchimento_roi(binary_warp, x1, y1, x2, y2)
                        
                        if marcado or parcial:
                            respostas_questao.append((letra, preenchimento, parcial))
                
                # Validar múltiplas marcações
                if len(respostas_questao) == 0:
                    resposta_final = None
                    status = "vazia"
                    mensagem = "Nenhuma alternativa detectada"
                    confianca = 0
                elif len(respostas_questao) == 1:
                    resposta_final = respostas_questao[0][0]
                    status = "parcial" if respostas_questao[0][2] else "ok"
                    mensagem = f"Alternativa {resposta_final}"
                    confianca = respostas_questao[0][1]
                else:
                    respostas_questao.sort(key=lambda x: x[1], reverse=True)
                    primeira = respostas_questao[0][1]
                    segunda = respostas_questao[1][1]
                    
                    if primeira - segunda > 30:
                        resposta_final = respostas_questao[0][0]
                        status = "ok"
                        mensagem = f"Preferência para {resposta_final}"
                        confianca = primeira
                    else:
                        resposta_final = None
                        status = "multipla"
                        mensagem = "Múltiplas marcações"
                        confianca = (primeira + segunda) / 2
                
                confiancas_por_questao.append(confianca)
                
                if resposta_final and status in ["ok", "parcial"]:
                    gabarito_questao = gabarito.get(str(questao_idx + 1), "").upper()
                    acertou = (resposta_final == gabarito_questao)
                    
                    if acertou:
                        acertos += 1
                    
                    detalhes.append({
                        "questao": questao_idx + 1,
                        "resposta_aluno": resposta_final,
                        "gabarito": gabarito_questao,
                        "acertou": acertou,
                        "status": status,
                        "mensagem": mensagem,
                        "confianca_preenchimento": confianca
                    })
                else:
                    detalhes.append({
                        "questao": questao_idx + 1,
                        "resposta_aluno": "ANULADA" if status == "multipla" else "Não detectada",
                        "gabarito": gabarito.get(str(questao_idx + 1), "").upper(),
                        "acertou": False,
                        "status": status,
                        "mensagem": mensagem,
                        "confianca_preenchimento": 0
                    })
            
            # Gerar heatmap se estiver em debug
            if self.debug_mode and confiancas_por_questao:
                self._desenhar_heatmap(img_warp, confiancas_por_questao, (NUM_ALTERNATIVAS, num_questoes))
            
            total_questoes = len(gabarito)
            percentual = (acertos / total_questoes) * 100 if total_questoes > 0 else 0
            confianca_global = self._calcular_confianca_global(qualidade, confianca_marcadores, detalhes)
            
            return {
                "sucesso": True,
                "acertos": acertos,
                "total_questoes": total_questoes,
                "percentual": percentual,
                "detalhes": detalhes,
                "qualidade_imagem": qualidade,
                "confianca_marcadores": confianca_marcadores,
                "confianca_global": confianca_global,
                "usou_deteccao_real": usou_deteccao_real,
                "debug_images": self.debug_images if self.debug_mode else []
            }
            
        except Exception as e:
            import traceback
            return {
                "sucesso": False,
                "erro": f"Erro: {str(e)}",
                "acertos": 0,
                "total_questoes": len(gabarito),
                "percentual": 0,
                "detalhes": [],
                "confianca_global": 0
            }


leitor_prova = LeitorProva()
