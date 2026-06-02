import requests
import os
from dotenv import load_dotenv

load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

HEADERS = {
    "apikey": SUPABASE_KEY,
    "Authorization": f"Bearer {SUPABASE_KEY}",
    "Content-Type": "application/json"
}

print("📚 Criando usuários diretamente no Supabase...")

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
    print(f"❌ Admin: {response.status_code} - {response.text[:100]}")

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
    print(f"❌ Professor: {response2.status_code} - {response2.text[:100]}")
