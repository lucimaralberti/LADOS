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

url = f"{SUPABASE_URL}/rest/v1/usuarios?select=email,senha_hash"
response = requests.get(url, headers=headers)

print("=== USUÁRIOS E SENHAS ===")
for u in response.json():
    print(u["email"], "->", u["senha_hash"])
