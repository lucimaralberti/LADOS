import requests
import os
from dotenv import load_dotenv

load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

headers = {
    "apikey": SUPABASE_KEY,
    "Authorization": f"Bearer {SUPABASE_KEY}"
}

print("=== TESTE DE AUTENTICAÇÃO ===")

# Testar admin
email = "admin@lados.com"
senha = "admin123"

url = f"{SUPABASE_URL}/rest/v1/usuarios?email=eq.{email}&select=*"
response = requests.get(url, headers=headers)

print(f"Status: {response.status_code}")

if response.status_code == 200 and response.json():
    usuario = response.json()[0]
    print(f"Usuário encontrado: {usuario.get('email')}")
    print(f"Senha hash: {usuario.get('senha_hash')}")
    print(f"Senha informada: {senha}")
    print(f"Correspondem? {usuario.get('senha_hash') == senha}")
    
    if usuario.get('senha_hash') == senha:
        print("✅ LOGIN VÁLIDO!")
    else:
        print("❌ SENHA INCORRETA NO SUPABASE")
else:
    print("❌ Usuário não encontrado")
