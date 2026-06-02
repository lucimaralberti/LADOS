import requests
import os

# Credenciais diretas (já que o .env não está carregando)
SUPABASE_URL = "https://cxelepvrrkxmwwejniau.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImN4ZWxlcHZycmt4bXd3ZWpuaWF1Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3Nzg5MDc4MDUsImV4cCI6MjA5NDQ4MzgwNX0.qVnx3CEWuMdZyO-Nb_Y7xnencaIG5SH-rVgA-qmPLwM"

print("🔍 Testando conexão com Supabase...")
print(f"URL: {SUPABASE_URL}")

try:
    url = f"{SUPABASE_URL}/rest/v1/"
    headers = {
        "apikey": SUPABASE_KEY,
        "Authorization": f"Bearer {SUPABASE_KEY}"
    }
    response = requests.get(url, headers=headers, timeout=10)
    print(f"Status: {response.status_code}")
    
    if response.status_code == 200:
        print("✅ Conexão funcionando! Tabelas existem.")
    elif response.status_code == 401:
        print("❌ Chave API inválida")
    elif response.status_code == 404:
        print("⚠️ Tabelas não existem, mas a conexão está OK!")
        print("   Execute o script SQL no Supabase para criar as tabelas.")
    else:
        print(f"⚠️ Resposta inesperada: {response.status_code}")
except Exception as e:
    print(f"❌ Erro: {e}")
