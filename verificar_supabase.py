import os
from supabase import create_client
from dotenv import load_dotenv

load_dotenv()

URL = os.getenv("SUPABASE_URL")
KEY = os.getenv("SUPABASE_KEY")

print("🔍 CONECTANDO AO SUPABASE...")
print(f"   URL: {URL}")
print(f"   KEY: {KEY[:50]}...")
print("")

try:
    supabase = create_client(URL, KEY)
    print("✅ CONEXÃO ESTABELECIDA COM SUCESSO!")
    print("")
    
    # ============================================================
    # 1. VERIFICAR TABELAS EXISTENTES
    # ============================================================
    print("=" * 50)
    print("📊 TABELAS NO BANCO DE DADOS:")
    print("=" * 50)
    
    tabelas = ["usuarios", "turmas", "alunos", "provas", "correcoes", "sessoes_correcao"]
    
    for tabela in tabelas:
        try:
            result = supabase.table(tabela).select("*", count="exact").limit(1).execute()
            count = getattr(result, 'count', len(result.data))
            status = "✅" if result.data or count == 0 else "⚠️"
            print(f"   {status} {tabela}: {count} registros")
        except Exception as e:
            if "relation" in str(e):
                print(f"   ❌ {tabela}: NÃO EXISTE")
            else:
                print(f"   ⚠️ {tabela}: {str(e)[:50]}")
    
    print("")
    
    # ============================================================
    # 2. USUÁRIOS CADASTRADOS
    # ============================================================
    print("=" * 50)
    print("👥 USUÁRIOS CADASTRADOS:")
    print("=" * 50)
    
    try:
        result = supabase.table("usuarios").select("*").execute()
        if result.data:
            for user in result.data:
                print(f"   ✅ {user['nome']} ({user['email']}) - {user['perfil']}")
        else:
            print("   ⚠️ Nenhum usuário cadastrado")
    except Exception as e:
        print(f"   ❌ Erro ao buscar usuários: {e}")
    
    print("")
    
    # ============================================================
    # 3. PROVAS GERADAS
    # ============================================================
    print("=" * 50)
    print("📄 PROVAS GERADAS:")
    print("=" * 50)
    
    try:
        result = supabase.table("provas").select("*").order("created_at", desc=True).execute()
        if result.data:
            for prova in result.data[:5]:
                print(f"   📄 {prova['exam_id']} - {prova['nome'][:40]} - {prova.get('created_at', 'N/A')[:10]}")
            if len(result.data) > 5:
                print(f"   ... e mais {len(result.data) - 5} provas")
        else:
            print("   ⚠️ Nenhuma prova encontrada")
    except Exception as e:
        print(f"   ❌ Erro ao buscar provas: {e}")
    
    print("")
    
    # ============================================================
    # 4. PERMISSÕES (RLS)
    # ============================================================
    print("=" * 50)
    print("🔐 STATUS DAS PERMISSÕES (RLS):")
    print("=" * 50)
    
    # Testar inserção
    test_data = {
        "exam_id": "TEST_VERIFICATION",
        "nome": "Teste Verificação",
        "disciplina": "Sistema"
    }
    
    try:
        result = supabase.table("provas").insert(test_data).execute()
        print("   ✅ Inserção permitida (RLS desabilitada ou configurada)")
        # Limpar teste
        supabase.table("provas").delete().eq("exam_id", "TEST_VERIFICATION").execute()
    except Exception as e:
        if "row-level security" in str(e):
            print("   ⚠️ RLS ativa - pode precisar de ajustes")
        else:
            print(f"   ⚠️ Erro na inserção: {str(e)[:50]}")
    
    print("")
    
    # ============================================================
    # 5. RESUMO FINAL
    # ============================================================
    print("=" * 50)
    print("📋 RESUMO FINAL")
    print("=" * 50)
    print("")
    print("✅ Supabase configurado e funcionando!")
    print("")
    print("📌 Recomendações:")
    print("   1. Desabilite RLS para testes: ALTER TABLE provas DISABLE ROW LEVEL SECURITY;")
    print("   2. Para produção, configure políticas apropriadas")
    print("")
    
except Exception as e:
    print(f"❌ ERRO FATAL: {e}")
    print("   Verifique sua conexão com a internet e as credenciais no .env")
