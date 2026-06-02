from services.supabase_service import supabase_service
import json
from datetime import datetime

print("🔍 Testando registro manual...")

test_data = {
    "exam_id": f"TEST_MANUAL_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
    "nome": "Teste Manual de Registro",
    "disciplina": "Sistema",
    "ano": "Teste",
    "qtd_questoes": 5,
    "gabarito": json.dumps({"1": "A", "2": "B", "3": "C"}),
    "created_at": datetime.now().isoformat()
}

try:
    result = supabase_service.client.table("provas").insert(test_data).execute()
    print(f"   ✅ Registro manual bem-sucedido!")
    print(f"   ID: {result.data[0]['exam_id']}")
except Exception as e:
    print(f"   ❌ Erro no registro manual: {e}")
