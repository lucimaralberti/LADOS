from services.supabase_service import supabase_service
import json
from datetime import datetime

print("🔍 Testando inserção manual no Supabase...")
print("")

# Dados de teste
test_data = {
    "exam_id": "TESTE_MANUAL_002",
    "nome": "Teste de Inserção",
    "disciplina": "Matemática",
    "ano": "5º Ano",
    "qtd_questoes": 10,
    "gabarito": json.dumps({"1": "A", "2": "B", "3": "C"}),
    "created_at": datetime.now().isoformat()
}

print("📤 Enviando dados:")
print(f"   Exam ID: {test_data['exam_id']}")
print(f"   Nome: {test_data['nome']}")
print(f"   Disciplina: {test_data['disciplina']}")
print("")

try:
    result = supabase_service.client.table("provas").insert(test_data).execute()
    print("✅ Inserção bem-sucedida!")
    print(f"   ID: {result.data[0]['exam_id']}")
    print(f"   Nome: {result.data[0]['nome']}")
except Exception as e:
    print(f"❌ Erro: {e}")
