import requests

SUPABASE_URL = "https://cxelepvrrkxmwwejniau.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImN4ZWxlcHZycmt4bXd3ZWpuaWF1Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3Nzg5MDc4MDUsImV4cCI6MjA5NDQ4MzgwNX0.qVnx3CEWuMdZyO-Nb_Y7xnencaIG5SH-rVgA-qmPLwM"

def testar_conexao():
    """Testa conexao com Supabase via endpoint de autenticacao"""
    try:
        # Usar endpoint de autenticacao (que funciona)
        url = f"{SUPABASE_URL}/auth/v1/health"
        headers = {
            "apikey": SUPABASE_KEY,
            "Authorization": f"Bearer {SUPABASE_KEY}"
        }
        response = requests.get(url, headers=headers, timeout=10)
        
        if response.status_code == 200:
            return {"sucesso": True, "dados": "Conexao OK"}
        else:
            return {"sucesso": False, "erro": f"HTTP {response.status_code}"}
    except Exception as e:
        return {"sucesso": False, "erro": str(e)}

def criar_tabela_sql(sql):
    """Executa SQL usando o endpoint de autenticacao"""
    try:
        # Nota: Para executar SQL, você precisa usar o SQL Editor manualmente
        return {"sucesso": False, "erro": "Execute o SQL manualmente no painel do Supabase"}
    except Exception as e:
        return {"sucesso": False, "erro": str(e)}

if __name__ == "__main__":
    print(testar_conexao())
