import json
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

print("📚 Migrando usuários...")

# Usar utf-8-sig para ignorar BOM
with open("data/usuarios.json", "r", encoding="utf-8-sig") as f:
    usuarios = json.load(f)

print(f"Encontrados {len(usuarios)} usuários")

for u in usuarios:
    data = {
        "email": u.get("email"),
        "senha_hash": u.get("senha", u.get("senha_hash")),
        "nome": u.get("nome"),
        "perfil": u.get("perfil", "Professor"),
        "ativo": True
    }
    
    # Verificar se já existe
    url_check = f"{SUPABASE_URL}/rest/v1/usuarios?email=eq.{data['email']}"
    r_check = requests.get(url_check, headers=HEADERS)
    
    if r_check.status_code == 200 and r_check.json():
        print(f"⚠️ {data['email']} já existe")
    else:
        url = f"{SUPABASE_URL}/rest/v1/usuarios"
        response = requests.post(url, headers=HEADERS, json=data)
        if response.status_code in [200, 201]:
            print(f"✅ {data['email']} migrado")
        else:
            print(f"❌ {data['email']}: {response.status_code} - {response.text[:100]}")
