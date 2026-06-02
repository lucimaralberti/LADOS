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

print("📚 Verificando questões já migradas...")

# Buscar códigos já existentes no Supabase
url_check = f"{SUPABASE_URL}/rest/v1/questoes?select=codigo&limit=1000"
response = requests.get(url_check, headers=HEADERS)

existentes = set()
if response.status_code == 200:
    for q in response.json():
        if q.get("codigo"):
            existentes.add(q.get("codigo"))
    print(f"✅ Questões já migradas: {len(existentes)}")
else:
    print(f"❌ Erro ao buscar: {response.status_code}")

# Carregar JSON
with open("data/itens.json", "r", encoding="utf-8") as f:
    questoes = json.load(f)

print(f"Total no JSON: {len(questoes)}")

# Filtrar as que faltam
faltantes = [q for q in questoes if q.get("id") not in existentes]
print(f"📚 Questões a migrar: {len(faltantes)}")

if len(faltantes) == 0:
    print("✅ Todas as questões já foram migradas!")
    exit()

enviadas = 0
erros = 0

for i, q in enumerate(faltantes):
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
    try:
        response = requests.post(url, headers=HEADERS, json=data, timeout=30)
        if response.status_code in [200, 201]:
            enviadas += 1
            if (i + 1) % 50 == 0:
                print(f"Progresso: {i+1}/{len(faltantes)}")
        else:
            erros += 1
            if erros <= 10:
                print(f"❌ {q.get('id')}: {response.status_code}")
    except Exception as e:
        erros += 1
        print(f"❌ {q.get('id')}: Erro de conexão")
    time.sleep(0.1)  # Pausa para não sobrecarregar

print(f"\n✅ Concluído!")
print(f"   Enviadas nesta sessão: {enviadas}")
print(f"   Erros: {erros}")
print(f"   Total no Supabase: {len(existentes) + enviadas}")
