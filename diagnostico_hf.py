import os
import sys
import json
from pathlib import Path

print("=" * 60)
print("🔍 DIAGNÓSTICO LADOS - HUGGING FACE")
print("=" * 60)

# Verificar ambiente
print(f"\n📌 Ambiente:")
print(f"   Python: {sys.version}")
print(f"   Diretório atual: {os.getcwd()}")

# Verificar arquivos
print(f"\n📁 Arquivos na raiz:")
for item in Path(".").iterdir():
    if item.is_file():
        print(f"   - {item.name}")

# Verificar pastas importantes
pastas = ["services", "pages", "data"]
for pasta in pastas:
    if Path(pasta).exists():
        print(f"   ✅ Pasta '{pasta}' existe")
        for item in Path(pasta).iterdir():
            if item.is_file():
                print(f"      - {pasta}/{item.name}")
    else:
        print(f"   ❌ Pasta '{pasta}' NÃO existe")

# Testar importação
print(f"\n🔐 Testando importação do AuthService...")
try:
    sys.path.insert(0, os.getcwd())
    from services.auth_service import AuthService
    print("   ✅ AuthService importado!")
    
    auth = AuthService(usar_supabase=False)
    print("   ✅ Instância criada!")
    
    usuario = auth.autenticar("admin@lados.com", "admin123")
    if usuario:
        print(f"   ✅ Login funcionou! Usuário: {usuario.get('nome')}")
    else:
        print("   ❌ Login falhou - verifique usuarios.json")
        
except Exception as e:
    print(f"   ❌ Erro: {e}")

print("\n" + "=" * 60)
