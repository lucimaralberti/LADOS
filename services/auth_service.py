from typing import Optional, Dict
import json
from pathlib import Path
import os
from dotenv import load_dotenv

class AuthService:
    """Serviço unificado de autenticação"""
    
    def __init__(self, usar_supabase: bool = True):
        self.usar_supabase = usar_supabase
        self.supabase = None
        if usar_supabase:
            self._init_supabase()
    
    def _init_supabase(self):
        """Inicializa cliente Supabase"""
        try:
            from supabase import create_client
            
            load_dotenv()
            supabase_url = os.environ.get('SUPABASE_URL')
            supabase_key = os.environ.get('SUPABASE_KEY')
            
            if supabase_url and supabase_key:
                self.supabase = create_client(supabase_url, supabase_key)
                print("✅ Conectado ao Supabase!")
            else:
                print("⚠️ Supabase não configurado. Usando fallback JSON.")
                self.usar_supabase = False
        except Exception as e:
            print(f"⚠️ Erro ao conectar Supabase: {e}")
            self.usar_supabase = False
    
    # MÉTODO PRINCIPAL QUE O SISTEMA ESPERA
    def autenticar_usuario(self, email: str, senha: str) -> Optional[Dict]:
        """Método principal de autenticação - compatível com o sistema existente"""
        return self.autenticar(email, senha)
    
    def autenticar(self, email: str, senha: str) -> Optional[Dict]:
        """Autentica usando Supabase ou JSON"""
        if self.usar_supabase and self.supabase:
            return self._autenticar_supabase(email, senha)
        else:
            return self._autenticar_json(email, senha)
    
    def _autenticar_supabase(self, email: str, senha: str) -> Optional[Dict]:
        """Autenticação via Supabase"""
        try:
            # Tenta autenticar via Supabase Auth
            response = self.supabase.auth.sign_in_with_password({
                "email": email,
                "password": senha
            })
            
            if response.user:
                return {
                    'id': response.user.id,
                    'email': response.user.email,
                    'nome': response.user.user_metadata.get('nome', email),
                    'role': response.user.user_metadata.get('role', 'professor')
                }
            return None
        except Exception as e:
            # Fallback: tenta autenticar direto na tabela
            return self._autenticar_tabela_direta(email, senha)
    
    def _autenticar_tabela_direta(self, email: str, senha: str) -> Optional[Dict]:
        """Fallback: autentica diretamente na tabela usuarios"""
        try:
            response = self.supabase.table("usuarios").select("*").eq("email", email).execute()
            if response.data:
                usuario = response.data[0]
                if usuario.get('senha') == senha:
                    return {
                        'id': usuario.get('id'),
                        'email': usuario.get('email'),
                        'nome': usuario.get('nome'),
                        'role': usuario.get('role', 'professor')
                    }
            return None
        except:
            return None
    
    def _autenticar_json(self, email: str, senha: str) -> Optional[Dict]:
        """Autenticação via JSON (fallback)"""
        usuarios_path = Path("data/usuarios.json")
        
        if not usuarios_path.exists():
            self._criar_usuarios_padrao()
        
        try:
            with open(usuarios_path, 'r', encoding='utf-8') as f:
                usuarios = json.load(f)
        except:
            return None
        
        for usuario in usuarios:
            if usuario.get('email') == email and usuario.get('senha') == senha:
                return usuario
        
        return None
    
    def _criar_usuarios_padrao(self):
        """Cria arquivo de usuários padrão"""
        Path("data").mkdir(exist_ok=True)
        
        usuarios_padrao = [
            {"id": "1", "nome": "Administrador", "email": "admin@lados.com", "senha": "admin123", "role": "admin"},
            {"id": "2", "nome": "Professor Demo", "email": "professor@lados.com", "senha": "professor123", "role": "professor"}
        ]
        
        with open("data/usuarios.json", 'w', encoding='utf-8') as f:
            json.dump(usuarios_padrao, f, indent=2, ensure_ascii=False)
        
        print("✅ Usuários padrão criados em data/usuarios.json")
