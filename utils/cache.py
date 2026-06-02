from typing import Dict, Any, Optional, Tuple
from datetime import datetime, timedelta
from pathlib import Path
from functools import wraps
import os

# Cache global (instância única)
_global_cache = None

def get_cache():
    """Obtém a instância global do cache (singleton)"""
    global _global_cache
    if _global_cache is None:
        _global_cache = MemoryCache()
    return _global_cache

class MemoryCache:
    """Cache em memória com TTL e invalidação por timestamp - SINGLETON"""
    
    def __init__(self, default_ttl: int = 300):
        self._cache: Dict[str, Tuple[Any, datetime, int]] = {}
        self.default_ttl = default_ttl
        self._timestamps: Dict[str, float] = {}
    
    def get(self, key: str, file_path: Optional[str] = None) -> Optional[Any]:
        if file_path and os.path.exists(file_path):
            current_mtime = os.path.getmtime(file_path)
            last_mtime = self._timestamps.get(key, 0)
            if current_mtime > last_mtime:
                self._cache.pop(key, None)
                self._timestamps.pop(key, None)
                return None
        
        if key in self._cache:
            data, timestamp, ttl = self._cache[key]
            if datetime.now() - timestamp < timedelta(seconds=ttl):
                return data
            else:
                del self._cache[key]
        return None
    
    def set(self, key: str, value: Any, ttl: int = None, file_path: Optional[str] = None):
        ttl = ttl or self.default_ttl
        self._cache[key] = (value, datetime.now(), ttl)
        if file_path and os.path.exists(file_path):
            self._timestamps[key] = os.path.getmtime(file_path)
    
    def clear(self, key: str = None):
        if key:
            self._cache.pop(key, None)
            self._timestamps.pop(key, None)
        else:
            self._cache.clear()
            self._timestamps.clear()

# Decorator usando cache global
def cached(ttl: int = 300, track_file: bool = False):
    """Decorator de cache usando instância global"""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            cache_instance = get_cache()
            key = f"{func.__name__}:{str(args)}:{str(kwargs)}"
            
            file_path = None
            if track_file and args:
                first_arg = args[0] if args else None
                if isinstance(first_arg, (str, Path)):
                    file_path = str(first_arg)
            
            result = cache_instance.get(key, file_path)
            if result is None:
                result = func(*args, **kwargs)
                cache_instance.set(key, result, ttl, file_path)
            return result
        return wrapper
    return decorator

# Instância global para uso direto
cache = get_cache()
