import requests
import os
from dotenv import load_dotenv

load_dotenv()

class SupabaseService:
    def __init__(self):
        self.supabase_url = os.getenv("SUPABASE_URL")
        self.supabase_key = os.getenv("SUPABASE_KEY")
        self.client = self._get_client()
    
    def _get_client(self):
        """Verifica se as credenciais estão configuradas"""
        if self.supabase_url and self.supabase_key:
            return True
        return None
    
    def autenticar_usuario(self, email: str, senha: str):
        """Autentica usuário no Supabase"""
        if not self.client:
            return None
        
        headers = {
            "apikey": self.supabase_key,
            "Authorization": f"Bearer {self.supabase_key}"
        }
        
        url = f"{self.supabase_url}/rest/v1/usuarios?email=eq.{email}&select=*"
        
        try:
            response = requests.get(url, headers=headers)
            if response.status_code == 200 and response.json():
                usuario = response.json()[0]
                if usuario.get("senha_hash") == senha:
                    return usuario
            return None
        except Exception as e:
            print(f"Erro na autenticação: {e}")
            return None

# Instância global para uso em outros módulos
supabase_service = SupabaseService()
