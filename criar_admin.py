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

print("=== CRIANDO USUÁRIO ADMIN ===")

# Verificar se admin já existe
url = f"{SUPABASE_URL}/rest/v1/usuarios?email=eq.admin@lados.com"
r = requests.get(url, headers=headers)

if r.status_code == 200 and r.json():
    print("Admin já existe! Atualizando senha...")
    # Atualizar senha
    url_patch = f"{SUPABASE_URL}/rest/v1/usuarios?email=eq.admin@lados.com"
    data = {"senha": "admin123"}
    r2 = requests.patch(url_patch, headers=headers, json=data)
    print(f"Admin atualizado: {r2.status_code}")
else:
    print("Admin não existe. Criando...")
    # Criar admin
    data = {
        "email": "admin@lados.com",
        "senha": "admin123",
        "nome": "Administrador",
        "perfil": "Admin"
    }
    r2 = requests.post(f"{SUPABASE_URL}/rest/v1/usuarios", headers=headers, json=data)
    print(f"Admin criado: {r2.status_code}")

print("\n=== VERIFICANDO USUÁRIOS ===")
url = f"{SUPABASE_URL}/rest/v1/usuarios?select=email,senha"
r = requests.get(url, headers=headers)
if r.status_code == 200:
    for u in r.json():
        print(f"{u['email']} - senha: {u['senha']}")
else:
    print(f"Erro: {r.status_code}")
