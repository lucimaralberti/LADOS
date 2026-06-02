from services.auth_service import AuthService

class SupabaseService(AuthService):
    """Cliente SupabaseService compatível com o código existente"""
    
    def __init__(self):
        super().__init__(usar_supabase=True)
    
    # Método específico que o sistema está procurando
    def autenticar_usuario(self, email: str, senha: str):
        """Método de autenticação que o sistema espera"""
        return self.autenticar(email, senha)
