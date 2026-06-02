import requests
import os
from dotenv import load_dotenv

load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

headers = {
    "apikey": SUPABASE_KEY,
    "Authorization": f"Bearer {SUPABASE_KEY}",
    "Content-Type": "application/json"
}

# 1. Deletar admin existente (se houver)
print("Deletando admin existente...")
url = f"{SUPABASE_URL}/rest/v1/usuarios?email=eq.admin@lados.com"
requests.delete(url, headers=headers)

# 2. Criar admin com senha correta
print("Criando novo admin...")
admin_data = {
    "email": "admin@lados.com",
    "senha_hash": "admin123",
    "nome": "Administrador",
    "perfil": "Admin",
    "ativo": True
}
r = requests.post(f"{SUPABASE_URL}/rest/v1/usuarios", headers=headers, json=admin_data)
print(f"Admin: {r.status_code}")

# 3. Criar professor1
print("Criando professor1...")
prof_data = {
    "email": "professor1@lados.com",
    "senha_hash": "professor123",
    "nome": "Professor 1",
    "perfil": "Professor",
    "ativo": True
}
r2 = requests.post(f"{SUPABASE_URL}/rest/v1/usuarios", headers=headers, json=prof_data)
print(f"Professor1: {r2.status_code}")

print("\n✅ Usuários recriados com sucesso!")
