from services.supabase_service import supabase_service
import json

# Carregar turmas
with open("para_supabase/turmas.json", "r", encoding="utf-8-sig") as f:
    turmas = json.load(f)

print("📤 Enviando turmas...")

for turma in turmas:
    # Filtrar apenas campos válidos
    dados = {k: v for k, v in turma.items() if k in ["nome", "ano", "turno"]}
    
    try:
        # Verificar se já existe
        existing = supabase_service.client.table("turmas").select("*").eq("nome", dados["nome"]).execute()
        if existing.data:
            print(f"   ⚠️ Turma {dados['nome']} já existe")
        else:
            supabase_service.client.table("turmas").insert(dados).execute()
            print(f"   ✅ Turma {dados['nome']} inserida")
    except Exception as e:
        print(f"   ❌ Erro: {e}")

print("✅ Envio concluído!")
