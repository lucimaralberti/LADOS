import requests

# Credenciais diretas
SUPABASE_URL = "https://uzxkyllykvnehscaemfk.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InV6eGt5bGx5a3ZuZWhzY2FlbWZrIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NzkwMjc2NTksImV4cCI6MjA5NDYwMzY1OX0.bM-pSUL5PfbxFiclp4w_ocM5gV1c18c1v1H-AoV-iWk"

HEADERS = {
    "apikey": SUPABASE_KEY,
    "Authorization": f"Bearer {SUPABASE_KEY}",
    "Content-Type": "application/json"
}

print("📚 Criando usuários diretamente no Supabase...")
print(f"URL: {SUPABASE_URL}")

# Criar admin
admin_data = {
    "email": "admin@lados.com",
    "senha_hash": "admin123",
    "nome": "Administrador",
    "perfil": "Admin",
    "ativo": True
}

url = f"{SUPABASE_URL}/rest/v1/usuarios"
response = requests.post(url, headers=HEADERS, json=admin_data)

if response.status_code in [200, 201]:
    print("✅ Admin criado com sucesso!")
else:
    print(f"❌ Admin: {response.status_code} - {response.text[:200]}")

# Criar professor
prof_data = {
    "email": "professor1@lados.com",
    "senha_hash": "professor123",
    "nome": "Professor 1",
    "perfil": "Professor",
    "ativo": True
}

response2 = requests.post(url, headers=HEADERS, json=prof_data)

if response2.status_code in [200, 201]:
    print("✅ Professor criado com sucesso!")
else:
    print(f"❌ Professor: {response2.status_code} - {response2.text[:200]}")
