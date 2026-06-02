"""
Teste de conexão com Supabase
"""

import sys
import os

# Adicionar o diretório atual ao path
sys.path.insert(0, os.getcwd())

print("=" * 50)
print("TESTE DE CONEXÃO COM SUPABASE")
print("=" * 50)

try:
    from services.supabase_service import supabase_service
    
    print("\n1. Verificando credenciais:")
    print(f"   URL: {supabase_service.url}")
    print(f"   KEY: {supabase_service.key[:50] if supabase_service.key else 'N/A'}...")
    
    print("\n2. Verificando conexão:")
    if supabase_service.client:
        print("   ✅ Cliente conectado")
        
        print("\n3. Testando consulta:")
        result = supabase_service.client.table("usuarios").select("*").limit(1).execute()
        print(f"   ✅ Tabela 'usuarios' acessível")
        
        result = supabase_service.client.table("provas").select("*").limit(1).execute()
        print(f"   ✅ Tabela 'provas' acessível")
        
        print("\n✅ CONEXÃO FUNCIONANDO CORRETAMENTE!")
    else:
        print("   ❌ Cliente NÃO conectado")
        
except Exception as e:
    print(f"\n❌ ERRO: {e}")
