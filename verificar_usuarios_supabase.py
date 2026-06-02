import requests

SUPABASE_URL = "https://uzxkyllykvnehscaemfk.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InV6eGt5bGx5a3ZuZWhzY2FlbWZrIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NzkwMjc2NTksImV4cCI6MjA5NDYwMzY1OX0.bM-pSUL5PfbxFiclp4w_ocM5gV1c18c1v1H-AoV-iWk"

HEADERS = {
    "apikey": SUPABASE_KEY,
    "Authorization": f"Bearer {SUPABASE_KEY}"
}

url = f"{SUPABASE_URL}/rest/v1/usuarios?select=email,perfil,nome"
response = requests.get(url, headers=HEADERS)

if response.status_code == 200:
    usuarios = response.json()
    print(f"📚 Total de usuários no Supabase: {len(usuarios)}")
    for u in usuarios:
        print(f"   - {u['email']} | {u['perfil']} | {u['nome']}")
else:
    print(f"❌ Erro: {response.status_code}")
