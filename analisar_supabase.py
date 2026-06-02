import requests
import json
from dotenv import load_dotenv
import os

load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

HEADERS = {
    "apikey": SUPABASE_KEY,
    "Authorization": f"Bearer {SUPABASE_KEY}",
    "Content-Type": "application/json"
}

print("=" * 60)
print("   ANALISANDO SUPABASE - LADOS 2.0")
print("=" * 60)

# ============================================
# 1. LISTAR TODAS AS TABELAS
# ============================================
print("\n📋 1. TABELAS EXISTENTES:")
print("-" * 40)

url = f"{SUPABASE_URL}/rest/v1/"
try:
    response = requests.get(url, headers=HEADERS)
    print(f"Status: {response.status_code}")
except:
    pass

# Tentar listar tabelas via SQL
sql = "SELECT table_name FROM information_schema.tables WHERE table_schema = 'public' ORDER BY table_name;"
url_sql = f"{SUPABASE_URL}/rest/v1/rpc/exec_sql"
try:
    response = requests.post(url_sql, headers=HEADERS, json={"query": sql})
    if response.status_code == 200:
        tabelas = response.json()
        for t in tabelas:
            print(f"   📁 {t.get('table_name')}")
except:
    print("   ⚠️ Não foi possível listar tabelas via SQL")

# ============================================
# 2. ANALISAR CADA TABELA
# ============================================
print("\n📊 2. ANÁLISE POR TABELA:")
print("-" * 40)

tabelas_para_analisar = ["usuarios", "turmas", "questoes", "avaliacoes", "resultados", "logs_exportacao", "termos_aceite"]

resultados = {}

for tabela in tabelas_para_analisar:
    url = f"{SUPABASE_URL}/rest/v1/{tabela}?select=*"
    response = requests.get(url, headers=HEADERS)
    
    if response.status_code == 200:
        dados = response.json()
        resultados[tabela] = {
            "total": len(dados),
            "dados": dados
        }
        print(f"\n   📁 {tabela}: {len(dados)} registros")
        
        # Mostrar amostra
        if len(dados) > 0:
            print(f"      📄 Exemplo: {list(dados[0].keys())[:5]}")
    else:
        resultados[tabela] = {"total": 0, "erro": response.status_code}
        print(f"\n   📁 {tabela}: Erro {response.status_code}")

# ============================================
# 3. VERIFICAR DUPLICIDADES
# ============================================
print("\n\n🔍 3. VERIFICANDO DUPLICIDADES:")
print("-" * 40)

# Verificar emails duplicados em usuarios
if "usuarios" in resultados and resultados["usuarios"]["total"] > 0:
    emails = [u.get("email") for u in resultados["usuarios"]["dados"]]
    emails_unicos = set(emails)
    if len(emails) != len(emails_unicos):
        print(f"   ⚠️ USUARIOS: {len(emails) - len(emails_unicos)} emails duplicados!")
        from collections import Counter
        duplicados = [email for email, count in Counter(emails).items() if count > 1]
        print(f"      Duplicados: {duplicados}")
    else:
        print(f"   ✅ USUARIOS: Sem duplicidades")

# Verificar codigos duplicados em questoes
if "questoes" in resultados and resultados["questoes"]["total"] > 0:
    codigos = [q.get("codigo") for q in resultados["questoes"]["dados"] if q.get("codigo")]
    codigos_unicos = set(codigos)
    if len(codigos) != len(codigos_unicos):
        print(f"   ⚠️ QUESTOES: {len(codigos) - len(codigos_unicos)} códigos duplicados!")
    else:
        print(f"   ✅ QUESTOES: Sem duplicidades")

# ============================================
# 4. RESUMO FINAL
# ============================================
print("\n\n📈 4. RESUMO FINAL:")
print("-" * 40)

for tabela, info in resultados.items():
    if info["total"] > 0:
        print(f"   ✅ {tabela}: {info['total']} registros")
    else:
        print(f"   ⚪ {tabela}: vazio ou erro")

print("\n" + "=" * 60)
print("   ANÁLISE CONCLUÍDA!")
print("=" * 60)

# Salvar relatório
relatorio = {
    "data_analise": str(__import__('datetime').datetime.now()),
    "resultados": {k: v for k, v in resultados.items() if "dados" not in v or isinstance(v["dados"], list)},
    "total_usuarios": resultados.get("usuarios", {}).get("total", 0),
    "total_questoes": resultados.get("questoes", {}).get("total", 0),
    "total_turmas": resultados.get("turmas", {}).get("total", 0)
}

with open("analise_supabase.json", "w", encoding="utf-8") as f:
    json.dump(relatorio, f, indent=2, ensure_ascii=False)

print("\n📄 Relatório salvo em: analise_supabase.json")
