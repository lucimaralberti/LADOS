import uuid
import json
from datetime import datetime
from services.supabase_service import supabase_service

print("1. Verificando conexão com Supabase...")
if supabase_service.client:
    print("   ✅ Conectado!")
else:
    print("   ❌ NÃO CONECTADO!")
    exit()

print("")
print("2. Tentando inserir uma prova de teste...")

# Dados de teste
test_data = {
    "exam_id": f"TEST_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
    "nome": "Prova de Teste",
    "disciplina": "Matemática",
    "ano": "5º Ano",
    "qtd_questoes": 10,
    "gabarito": json.dumps({"1": "A", "2": "B", "3": "C"}),
    "created_at": datetime.now().isoformat()
}

try:
    result = supabase_service.client.table("provas").insert(test_data).execute()
    print(f"   ✅ Prova de teste inserida!")
    print(f"   ID: {result.data[0]['id']}")
    print(f"   Exam ID: {result.data[0]['exam_id']}")
    
    print("")
    print("3. Verificando se a prova apareceu...")
    result = supabase_service.client.table("provas").select("*").execute()
    print(f"   Total de provas: {len(result.data)}")
    
except Exception as e:
    print(f"   ❌ Erro: {e}")
