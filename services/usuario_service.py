"""
Serviços de usuário - Integração com Supabase
"""

from services.supabase_service import supabase_service

class UsuarioService:
    
    @staticmethod
    def buscar_por_email(email: str):
        """Busca usuário por email"""
        try:
            resultado = supabase_service.client.table("usuarios").select("*").eq("email", email).execute()
            return resultado.data[0] if resultado.data else None
        except:
            return None
    
    @staticmethod
    def buscar_por_id(usuario_id: str):
        """Busca usuário por ID"""
        try:
            resultado = supabase_service.client.table("usuarios").select("*").eq("id", usuario_id).execute()
            return resultado.data[0] if resultado.data else None
        except:
            return None
    
    @staticmethod
    def listar_por_perfil(perfil: str):
        """Lista usuários por perfil"""
        try:
            resultado = supabase_service.client.table("usuarios").select("*").eq("perfil", perfil).execute()
            return resultado.data
        except:
            return []
    
    @staticmethod
    def atualizar_ultimo_acesso(usuario_id: str):
        """Atualiza timestamp de último acesso"""
        try:
            supabase_service.client.table("usuarios").update({"updated_at": "now()"}).eq("id", usuario_id).execute()
        except:
            pass
