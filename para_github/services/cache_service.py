"""
Cache decorator - LADOS 2.0
"""

import functools
import time
from typing import Any, Callable

class Cache:
    """Cache simples em memória"""
    
    def __init__(self, ttl: int = 60):
        self.ttl = ttl
        self._cache = {}
    
    def get(self, key: str) -> Any:
        if key in self._cache:
            valor, expira = self._cache[key]
            if time.time() < expira:
                return valor
            del self._cache[key]
        return None
    
    def set(self, key: str, valor: Any):
        self._cache[key] = (valor, time.time() + self.ttl)
    
    def clear(self):
        self._cache.clear()

# Cache global
cache = Cache(ttl=60)

def cached(ttl: int = 60):
    """Decorator para cache"""
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            # Criar chave baseada nos argumentos
            key = f"{func.__name__}:{str(args)}:{str(kwargs)}"
            
            # Tentar obter do cache
            resultado = cache.get(key)
            if resultado is not None:
                return resultado
            
            # Executar função
            resultado = func(*args, **kwargs)
            
            # Salvar no cache
            cache.set(key, resultado)
            return resultado
        return wrapper
    return decorator
