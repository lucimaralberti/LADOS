import requests
import json
import time

SUPABASE_URL = "https://uzxkyllykvnehscaemfk.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InV6eGt5bGx5a3ZuZWhzY2FlbWZrIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NzkwMjc2NTksImV4cCI6MjA5NDYwMzY1OX0.bM-pSUL5PfbxFiclp4w_ocM5gV1c18c1v1H-AoV-iWk"

HEADERS = {
    "apikey": SUPABASE_KEY,
    "Authorization": f"Bearer {SUPABASE_KEY}",
    "Content-Type": "application/json"
}

print("📚 Migrando questões para o Supabase...")

with open("data/itens.json", "r", encoding="utf-8") as f:
    questoes = json.load(f)

print(f"Total de questões no JSON: {len(questoes)}")

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
        "dificuldade": q.get("dificuldade", 0.5)
    }
    
    url = f"{SUPABASE_URL}/rest/v1/questoes"
    response = requests.post(url, headers=HEADERS, json=data)
    
    if response.status_code in [200, 201]:
        enviadas += 1
        if (i + 1) % 100 == 0:
            print(f"Progresso: {i+1}/{len(questoes)}")
    else:
        erros += 1
        if erros <= 10:
            print(f"❌ {q.get('id')}: {response.status_code} - {response.text[:100]}")
    time.sleep(0.05)

print(f"\n✅ Concluído!")
print(f"   Enviadas: {enviadas}")
print(f"   Erros: {erros}")
