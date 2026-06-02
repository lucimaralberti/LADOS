import requests
import os
from dotenv import load_dotenv
import json

load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

headers = {
    "apikey": SUPABASE_KEY,
    "Authorization": f"Bearer {SUPABASE_KEY}"
}

url = f"{SUPABASE_URL}/rest/v1/usuarios?select=email,senha_hash"
response = requests.get(url, headers=headers)

print("=== USUÁRIOS E SENHAS ===")
print(f"Status: {response.status_code}")
print(f"Resposta bruta: {response.text[:200]}")

if response.status_code == 200:
    dados = response.json()
    print(f"Tipo do retorno: {type(dados)}")
    
    if isinstance(dados, list):
        for u in dados:
            print(f"{u.get('email')} -> {u.get('senha_hash')}")
    else:
        print(f"Conteúdo: {dados}")
else:
    print(f"Erro: {response.status_code}")
