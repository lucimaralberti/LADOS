"""Repositório para Supabase - Conexão com banco de dados"""

from typing import List, Dict, Optional
from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).parent.parent))

from domain.modelos.item import Item
from domain.modelos.turma import Turma
from domain.modelos.diagnostico_turma import DiagnosticoTurma
from utils.logger import get_logger

logger = get_logger(__name__)

# Importar supabase apenas se disponível
try:
    from supabase import create_client, Client
    SUPABASE_AVAILABLE = True
except ImportError:
    SUPABASE_AVAILABLE = False
    logger.warning("Supabase não instalado. Use: pip install supabase")

class SupabaseRepository:
    """Repositório para Supabase - substitui JSON quando disponível"""
    
    def __init__(self, url: Optional[str] = None, key: Optional[str] = None):
        self.url = url or "https://seu-projeto.supabase.co"
        self.key = key or "sua-chave-anon"
        self.client: Optional[Client] = None
        
        if SUPABASE_AVAILABLE:
            try:
                self.client = create_client(self.url, self.key)
                logger.info("Conectado ao Supabase")
            except Exception as e:
                logger.error(f"Erro ao conectar ao Supabase: {e}")
    
    def is_available(self) -> bool:
        return self.client is not None
    
    # ===== MÉTODOS PARA ITENS =====
    def listar_itens(self, filtros: Optional[Dict] = None) -> List[Dict]:
        if not self.is_available():
            return []
        
        query = self.client.table("itens").select("*")
        if filtros:
            for key, value in filtros.items():
                query = query.eq(key, value)
        
        result = query.execute()
        return result.data
    
    def buscar_item_por_codigo(self, codigo: str) -> Optional[Dict]:
        if not self.is_available():
            return None
        
        result = self.client.table("itens").select("*").eq("codigo", codigo).execute()
        return result.data[0] if result.data else None
    
    # ===== MÉTODOS PARA TURMAS =====
    def listar_turmas_por_escola(self, escola_id: str) -> List[Dict]:
        if not self.is_available():
            return []
        
        result = self.client.table("turmas").select("*").eq("escola_id", escola_id).execute()
        return result.data
    
    def criar_turma(self, turma: Dict) -> Optional[Dict]:
        if not self.is_available():
            return None
        
        result = self.client.table("turmas").insert(turma).execute()
        return result.data[0] if result.data else None
    
    # ===== MÉTODOS PARA AVALIAÇÕES =====
    def registrar_avaliacao(self, avaliacao: Dict) -> Optional[Dict]:
        if not self.is_available():
            return None
        
        result = self.client.table("avaliacoes_turma").insert(avaliacao).execute()
        return result.data[0] if result.data else None
    
    def registrar_respostas_agregadas(self, respostas: List[Dict]) -> bool:
        if not self.is_available():
            return False
        
        try:
            self.client.table("respostas_agregadas").insert(respostas).execute()
            return True
        except Exception as e:
            logger.error(f"Erro ao registrar respostas: {e}")
            return False
    
    # ===== MÉTODOS PARA DIAGNÓSTICOS =====
    def salvar_diagnostico(self, diagnostico: Dict) -> Optional[Dict]:
        if not self.is_available():
            return None
        
        result = self.client.table("diagnosticos_turma").insert(diagnostico).execute()
        return result.data[0] if result.data else None
    
    def buscar_ultimo_diagnostico(self, turma_id: str) -> Optional[Dict]:
        if not self.is_available():
            return None
        
        result = self.client.table("diagnosticos_turma")\
            .select("*")\
            .eq("turma_id", turma_id)\
            .order("created_at", desc=True)\
            .limit(1)\
            .execute()
        
        return result.data[0] if result.data else None
    
    # ===== MÉTRICAS AGREGADAS =====
    def calcular_media_turma(self, turma_id: str) -> float:
        if not self.is_available():
            return 0.0
        
        result = self.client.rpc("calcular_media_turma", {"p_turma_id": turma_id}).execute()
        return result.data if result.data else 0.0
    
    def obter_descritores_criticos(self, turma_id: str, limite: float = 60.0) -> List[Dict]:
        if not self.is_available():
            return []
        
        result = self.client.rpc("obter_descritores_criticos", {
            "p_turma_id": turma_id,
            "p_limite": limite
        }).execute()
        return result.data if result.data else []
