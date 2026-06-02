"""Métricas e observabilidade para o LADOS 2.0"""

from prometheus_client import Counter, Histogram, Gauge, generate_latest
from functools import wraps
import time
from utils.logger import get_logger

logger = get_logger(__name__)

provas_processadas = Counter('lados_provas_processadas_total', 'Total de provas processadas')
provas_sucesso = Counter('lados_provas_sucesso_total', 'Provas processadas com sucesso')
provas_erro = Counter('lados_provas_erro_total', 'Provas com erro de leitura')
tempo_processamento = Histogram('lados_tempo_processamento_segundos', 'Tempo de processamento por prova')
confianca_media = Gauge('lados_confianca_media', 'Confiança média das leituras')
cache_hits = Counter('lados_cache_hits_total', 'Acertos no cache')
cache_misses = Counter('lados_cache_misses_total', 'Erros no cache')

def monitorar(func):
    @wraps(func)
    async def wrapper(*args, **kwargs):
        start = time.time()
        provas_processadas.inc()
        try:
            result = await func(*args, **kwargs)
            tempo_processamento.observe(time.time() - start)
            if result.get("sucesso"):
                provas_sucesso.inc()
                confianca_media.set(result.get("confianca", 0))
            else:
                provas_erro.inc()
            return result
        except Exception as e:
            provas_erro.inc()
            logger.error(f"Erro em {func.__name__}: {e}")
            raise
    return wrapper

def get_metrics():
    return generate_latest()
