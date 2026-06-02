from services.supabase_service import supabase_service

print("🔍 Buscando provas no Supabase...")
print("")

try:
    # Verificar estrutura da tabela
    print("📋 ESTRUTURA DA TABELA PROVAS:")
    print("-" * 40)
    
    # Buscar uma prova para ver os campos
    sample = supabase_service.client.table("provas").select("*").limit(1).execute()
    if sample.data:
        colunas = list(sample.data[0].keys())
        print(f"   Colunas: {', '.join(colunas)}")
    else:
        print("   Tabela vazia ou não existe")
    
    print("")
    
    # Contar total
    result = supabase_service.client.table("provas").select("*", count="exact").execute()
    total = getattr(result, 'count', len(result.data))
    
    print(f"📊 TOTAL DE PROVAS: {total}")
    print("")
    
    # Listar provas
    result = supabase_service.client.table("provas").select("*").order("created_at", desc=True).execute()
    
    if result.data:
        print("📋 LISTA DE PROVAS:")
        print("-" * 60)
        for i, prova in enumerate(result.data, 1):
            print(f"{i}. Exam ID: {prova.get('exam_id', 'N/A')}")
            print(f"   Nome: {prova.get('nome', 'N/A')}")
            print(f"   Disciplina: {prova.get('disciplina', 'N/A')}")
            print(f"   Ano: {prova.get('ano', 'N/A')}")
            print(f"   Questões: {prova.get('qtd_questoes', 'N/A')}")
            print(f"   Data: {prova.get('created_at', 'N/A')}")
            print("-" * 40)
    else:
        print("⚠️ Nenhuma prova encontrada no banco de dados.")
        print("   Gere uma prova primeiro na página 'Questões'.")
        
except Exception as e:
    print(f"❌ Erro ao buscar provas: {e}")
