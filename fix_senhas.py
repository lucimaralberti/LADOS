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

print("=== ATUALIZANDO SENHAS NO SUPABASE ===")

# Atualizar admin
admin_data = {"senha_hash": "admin123"}
url = f"{SUPABASE_URL}/rest/v1/usuarios?email=eq.admin@lados.com"
r = requests.patch(url, headers=headers, json=admin_data)
print(f"Admin (admin@lados.com): {r.status_code}")

# Verificar se o professor1 existe e atualizar
prof_data = {"senha_hash": "professor123"}
url = f"{SUPABASE_URL}/rest/v1/usuarios?email=eq.professor1@lados.com"
r2 = requests.patch(url, headers=headers, json=prof_data)
print(f"Professor1 (professor1@lados.com): {r2.status_code}")

# Verificar também o professor (sem o 1)
prof_data2 = {"senha_hash": "professor123"}
url = f"{SUPABASE_URL}/rest/v1/usuarios?email=eq.professor@lados.com"
r3 = requests.patch(url, headers=headers, json=prof_data2)
print(f"Professor (professor@lados.com): {r3.status_code}")

print("\n✅ Senhas atualizadas!")
