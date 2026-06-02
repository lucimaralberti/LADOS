from pathlib import Path
from typing import Dict, Any
import json
import os
from utils.cache import cache
from utils.logger import get_logger

logger = get_logger(__name__)

class DadosService:
    def __init__(self, data_dir=None):
        from config import settings
        self.data_dir = data_dir or settings.data_dir
        self._carregar_todos()
    
    def _carregar_json(self, filename: str) -> Dict:
        caminho = self.data_dir / filename
        cache_key = f"json:{filename}"
        
        dados = cache.get(cache_key, str(caminho))
        if dados is not None:
            return dados
        
        if caminho.exists():
            try:
                with open(caminho, "r", encoding="utf-8") as f:
                    dados = json.load(f)
                cache.set(cache_key, dados, file_path=str(caminho))
                logger.debug(f"Carregado: {filename}")
                return dados
            except Exception as e:
                logger.error(f"Erro ao carregar {filename}: {e}")
        
        cache.set(cache_key, {}, ttl=60)
        return {}
    
    def _carregar_todos(self):
        logger.info("Carregando todos os dados...")
        self.pesos_bloom = self._carregar_json("pesos_bloom.json")
        self.mapeamento_erros = self._carregar_json("mapeamento_erros.json")
        self.pre_requisitos = self._carregar_json("pre_requisitos.json")
        self.tipos_erros = self._carregar_json("tipos_erros.json")
        self.saeb = self._carregar_json("saeb.json")
        self.cnca = self._carregar_json("cnca.json")
        self.escalas = {
            "2EF": self._carregar_json("escala_2ano.json"),
            "5EF": self._carregar_json("escala_5ano.json"),
            "9EF": self._carregar_json("escala_9ano.json")
        }
        
        total_erros = len(self.mapeamento_erros) if isinstance(self.mapeamento_erros, list) else 0
        logger.info(f"Dados carregados: Bloom={bool(self.pesos_bloom)}, Erros={total_erros}, PreReqs={len(self.pre_requisitos)}")
    
    def get_nivel_saeb(self, ano: str, disciplina: str, percentual: float) -> Dict[str, Any]:
        """Classifica o nível SAEB baseado no percentual de acertos usando as escalas"""
        escala = self.escalas.get(ano, {})
        
        # Mapear disciplina para o nome no JSON
        disc_key = "lingua_portuguesa" if disciplina == "LP" else "matematica"
        niveis = escala.get("disciplinas", {}).get(disc_key, [])
        
        # Encontrar o nível correspondente
        for nivel in niveis:
            nivel_num = nivel.get("nivel", 0)
            if nivel_num <= percentual / 10:
                return {
                    "nivel": nivel.get("nomenclatura", "Indeterminado"),
                    "descricao": nivel.get("descricao", ""),
                    "percentual": percentual
                }
        
        # Fallback baseado em percentual simples
        if percentual >= 90:
            return {"nivel": "Avançado", "descricao": "Desempenho excepcional", "percentual": percentual}
        elif percentual >= 70:
            return {"nivel": "Proficiente", "descricao": "Desempenho adequado", "percentual": percentual}
        elif percentual >= 50:
            return {"nivel": "Básico", "descricao": "Desempenho em desenvolvimento", "percentual": percentual}
        else:
            return {"nivel": "Abaixo do Básico", "descricao": "Desempenho insuficiente", "percentual": percentual}
    
    def get_pesos_bloom_ano(self, ano: str) -> Dict:
        """Retorna os pesos Bloom para um ano específico"""
        return self.pesos_bloom.get(ano, {})
    
    def get_erros_por_descritor(self, descritor: str) -> list:
        """Retorna lista de erros esperados para um descritor"""
        for item in self.mapeamento_erros:
            if isinstance(item, dict) and item.get("descritor") == descritor:
                return item.get("erros", [])
        return []
    
    def get_pre_requisitos(self, descritor: str) -> Dict:
        """Retorna pré-requisitos para um descritor"""
        return self.pre_requisitos.get(descritor, {})
    
    def get_trilha_recuperacao(self, descritor: str) -> list:
        """Retorna a trilha de recuperação para um descritor"""
        dados = self.get_pre_requisitos(descritor)
        return dados.get("trilha_recuperacao", [])
    
    def get_pre_requisitos_lista(self, descritor: str) -> list:
        """Retorna lista de pré-requisitos com pesos"""
        dados = self.get_pre_requisitos(descritor)
        return dados.get("pre_requisitos", [])
    
    def get_tipo_erro(self, codigo: str) -> Dict:
        """Retorna informações detalhadas de um tipo de erro"""
        for erro in self.tipos_erros:
            if isinstance(erro, dict) and erro.get("codigo") == codigo:
                return erro
        return {}
    
    def get_descricao_erro_por_ano(self, codigo: str, ano: str) -> str:
        """Retorna a descrição da progressão do erro para um ano específico"""
        erro = self.get_tipo_erro(codigo)
        progressao = erro.get("progressao", {})
        return progressao.get(ano, erro.get("descricao", ""))
    
    def get_intervencao_erro(self, codigo: str) -> str:
        """Retorna a intervenção sugerida para um tipo de erro"""
        erro = self.get_tipo_erro(codigo)
        return erro.get("intervencao", "")
    
    def get_pesos_saeb(self, ano: str, disciplina: str) -> Dict[str, float]:
        """Retorna os pesos SAEB por descritor"""
        dados_ano = self.saeb.get(ano, {})
        disc_key = "Língua Portuguesa" if disciplina == "LP" else "Matemática"
        dados_disc = dados_ano.get(disc_key, [])
        return {item["codigo"]: item.get("peso", 0.05) for item in dados_disc}
    
    def recarregar(self, filename: str = None):
        """Recarrega dados (força limpeza de cache)"""
        if filename:
            cache_key = f"json:{filename}"
            cache.clear(cache_key)
        else:
            self._carregar_todos()
        logger.info(f"Recarregado: {filename or 'todos os dados'}")

dados_service = DadosService()
