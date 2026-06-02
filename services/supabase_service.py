from services.auth_service import AuthService

class SupabaseService(AuthService):
    """
    Serviço compatível com o código existente.
    Herda todas as funções de AuthService e adiciona o método específico
    que o sistema está procurando.
    """
    def __init__(self):
        # Inicializa a classe pai (AuthService) com suporte ao Supabase
        super().__init__(usar_supabase=True)

    # Este é o método que faltava e que o seu sistema tenta chamar
    def autenticar_usuario(self, email: str, senha: str):
        """
        Método de autenticação específico que seu código espera.
        Ele simplesmente chama o método 'autenticar' da classe pai.
        """
        return self.autenticar(email, senha)
