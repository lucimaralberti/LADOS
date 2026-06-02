"""Cache robusto para LADOS 2.0"""

import hashlib
import asyncio
from typing import Dict, Optional, Any
from datetime import datetime, timedelta
from utils.logger import get_logger
from config import settings

logger = get_logger(__name__)

class CacheRobusto:
    def __init__(self):
        self._mem_cache: Dict[str, tuple] = {}
        self._lock = asyncio.Lock()
        self._redis = None
        
        if settings.redis_url:
            try:
                import redis.asyncio as redis
                self._redis = redis.from_url(settings.redis_url)
                logger.info("Cache Redis conectado")
            except Exception as e:
                logger.warning(f"Redis não disponível: {e}")
    
    def _hash_imagem(self, imagem_bytes: bytes) -> str:
        return hashlib.sha256(imagem_bytes).hexdigest()
    
    async def get(self, imagem_bytes: bytes) -> Optional[Any]:
        cache_key = self._hash_imagem(imagem_bytes)
        
        async with self._lock:
            if self._redis:
                try:
                    cached = await self._redis.get(cache_key)
                    if cached:
                        import pickle
                        return pickle.loads(cached)
                except Exception as e:
                    logger.warning(f"Erro no Redis: {e}")
            
            if cache_key in self._mem_cache:
                resultado, timestamp = self._mem_cache[cache_key]
                if datetime.now() - timestamp < timedelta(seconds=settings.cache_ttl):
                    return resultado
        return None
    
    async def set(self, imagem_bytes: bytes, resultado: Any):
        cache_key = self._hash_imagem(imagem_bytes)
        
        async with self._lock:
            if self._redis:
                try:
                    import pickle
                    await self._redis.setex(cache_key, settings.cache_ttl, pickle.dumps(resultado))
                except Exception as e:
                    logger.warning(f"Erro ao salvar no Redis: {e}")
            
            if len(self._mem_cache) >= settings.cache_max_size:
                oldest = min(self._mem_cache.keys(), key=lambda k: self._mem_cache[k][1])
                del self._mem_cache[oldest]
            
            self._mem_cache[cache_key] = (resultado, datetime.now())

cache_robusto = CacheRobusto()
