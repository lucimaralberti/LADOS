import requests
import json

# Credenciais diretas (evita problema de load_dotenv)
SUPABASE_URL = "https://uzxkyllykvnehscaemfk.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InV6eGt5bGx5a3ZuZWhzY2FlbWZrIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NzkwMjc2NTksImV4cCI6MjA5NDYwMzY1OX0.bM-pSUL5PfbxFiclp4w_ocM5gV1c18c1v1H-AoV-iWk"

HEADERS = {
    "apikey": SUPABASE_KEY,
    "Authorization": f"Bearer {SUPABASE_KEY}"
}

print("=" * 50)
print("ANALISANDO SUPABASE - LADOS 2.0")
print("=" * 50)

tabelas = ["usuarios", "turmas", "questoes", "avaliacoes", "resultados", "logs_exportacao", "termos_aceite"]

for tabela in tabelas:
    url = f"{SUPABASE_URL}/rest/v1/{tabela}?select=*&limit=1"
    response = requests.get(url, headers=HEADERS)
    
    if response.status_code == 200:
        dados = response.json()
        print(f"\n✅ {tabela}: {len(dados)} registros (amostra)")
        
        # Buscar total real
        url_count = f"{SUPABASE_URL}/rest/v1/{tabela}?select=count"
        count_response = requests.get(url_count, headers=HEADERS)
        if count_response.status_code == 200:
            print(f"   Total: {len(count_response.json()) if count_response.json() else 0}")
    else:
        print(f"\n❌ {tabela}: Erro {response.status_code}")

print("\n" + "=" * 50)
print("ANÁLISE CONCLUÍDA!")
print("=" * 50)
