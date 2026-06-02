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

print("📚 Migrando questões para o Supabase...")

with open("data/itens.json", "r", encoding="utf-8") as f:
    questoes = json.load(f)

print(f"Total de questões encontradas: {len(questoes)}")

enviadas = 0
erros = 0

for i, q in enumerate(questoes):
    data = {
        "codigo": q.get("id"),
        "enunciado": q.get("enunciado"),
        "alternativas": q.get("alternativas", []),
        "gabarito": q.get("gabarito"),
        "disciplina": q.get("disciplina"),
        "ano": q.get("ano"),
        "descritor_id": None,
        "dificuldade": q.get("dificuldade", 0.5),
        "created_at": "now()"
    }
    
    url = f"{SUPABASE_URL}/rest/v1/questoes"
    response = requests.post(url, headers=HEADERS, json=data)
    
    if response.status_code in [200, 201]:
        enviadas += 1
        if (i + 1) % 100 == 0:
            print(f"Progresso: {i+1}/{len(questoes)}")
    else:
        erros += 1
        if erros <= 5:
            print(f"❌ Erro na questão {q.get('id')}: {response.status_code}")

print(f"\n✅ Concluído!")
print(f"   Questões enviadas: {enviadas}")
print(f"   Erros: {erros}")
