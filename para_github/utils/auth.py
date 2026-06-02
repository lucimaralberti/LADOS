"""
Compatibilidade - Redireciona para core/auth.py
Mantido para não quebrar código existente
"""

from core.auth import *

# Mensagem de depreciação (opcional, não afeta funcionamento)
import warnings
warnings.warn("utils/auth.py está depreciado. Use core/auth.py", DeprecationWarning, stacklevel=2)
