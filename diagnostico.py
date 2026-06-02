"""
DIAGNÓSTICO COMPLETO DO SISTEMA LADOS
Testa cada componente individualmente
"""

import os
import sys
import json
from pathlib import Path

print("=" * 60)
print("🔍 DIAGNÓSTICO DO SISTEMA LADOS")
print("=" * 60)

# ============================================
# 1. VERIFICAR ARQUIVOS ESSENCIAIS
# ============================================
print("\n📁 1. VERIFICANDO ARQUIVOS ESSENCIAIS:")

arquivos_necessarios = [
    "app.py",
    "Login.py",
    "requirements.txt",
    "services/auth_service.py",
    "services/__init__.py"
]

for arquivo in arquivos_necessarios:
    if Path(arquivo).exists():
        print(f"   ✅ {arquivo}")
    else:
        print(f"   ❌ {arquivo} - FALTANDO!")

# ============================================
# 2. TESTAR IMPORTAÇÃO DO AUTH_SERVICE
# ============================================
print("\n🔐 2. TESTANDO IMPORTAÇÃO DO AUTH_SERVICE:")

try:
    from services.auth_service import AuthService
    print("   ✅ AuthService importado com sucesso")
    
    # Criar instância
    auth = AuthService(usar_supabase=False)  # Usar JSON para teste
    print("   ✅ Instância do AuthService criada")
    
    # Verificar métodos
    if hasattr(auth, 'autenticar'):
        print("   ✅ Método 'autenticar' existe")
    else:
        print("   ❌ Método 'autenticar' NÃO existe")
    
    if hasattr(auth, 'autenticar_usuario'):
        print("   ✅ Método 'autenticar_usuario' existe")
    else:
        print("   ⚠️ Método 'autenticar_usuario' não existe (opcional)")
        
except Exception as e:
    print(f"   ❌ ERRO: {e}")

# ============================================
# 3. TESTAR AUTENTICAÇÃO COM JSON
# ============================================
print("\n👤 3. TESTANDO AUTENTICAÇÃO COM JSON:")

try:
    from services.auth_service import AuthService
    auth = AuthService(usar_supabase=False)
    
    # Criar arquivo de usuários se não existir
    Path("data").mkdir(exist_ok=True)
    usuarios_path = Path("data/usuarios.json")
    
    if not usuarios_path.exists():
        usuarios_padrao = [
            {"id": "1", "nome": "Administrador", "email": "admin@lados.com", "senha": "admin123", "role": "admin"},
            {"id": "2", "nome": "Professor Demo", "email": "professor@lados.com", "senha": "professor123", "role": "professor"}
        ]
        with open(usuarios_path, 'w', encoding='utf-8') as f:
            json.dump(usuarios_padrao, f, indent=2)
        print("   ✅ Arquivo usuarios.json criado")
    
    # Testar login do admin
    usuario = auth.autenticar("admin@lados.com", "admin123")
    if usuario:
        print(f"   ✅ Login admin OK: {usuario.get('nome')} (role: {usuario.get('role')})")
    else:
        print("   ❌ Login admin FALHOU")
    
    # Testar login do professor
    usuario = auth.autenticar("professor@lados.com", "professor123")
    if usuario:
        print(f"   ✅ Login professor OK: {usuario.get('nome')} (role: {usuario.get('role')})")
    else:
        print("   ❌ Login professor FALHOU")
        
except Exception as e:
    print(f"   ❌ ERRO: {e}")

# ============================================
# 4. TESTAR SUPABASE (SE CONFIGURADO)
# ============================================
print("\n🗄️ 4. TESTANDO CONEXÃO COM SUPABASE:")

# Verificar variáveis de ambiente
supabase_url = os.environ.get('SUPABASE_URL')
supabase_key = os.environ.get('SUPABASE_KEY')

if supabase_url and supabase_key:
    print(f"   ✅ SUPABASE_URL configurada: {supabase_url[:30]}...")
    print(f"   ✅ SUPABASE_KEY configurada: {supabase_key[:30]}...")
    
    try:
        from supabase import create_client
        supabase = create_client(supabase_url, supabase_key)
        print("   ✅ Cliente Supabase criado")
        
        # Testar consulta simples
        response = supabase.table("usuarios").select("count").execute()
        print("   ✅ Consulta ao Supabase funcionou")
        
    except Exception as e:
        print(f"   ⚠️ Erro ao conectar Supabase: {e}")
else:
    print("   ⚠️ Variáveis SUPABASE não configuradas (login usará JSON)")

# ============================================
# 5. TESTAR STREAMLIT (SIMULADO)
# ============================================
print("\n🎨 5. VERIFICANDO CONFIGURAÇÃO STREAMLIT:")

try:
    import streamlit as st
    print(f"   ✅ Streamlit versão: {st.__version__}")
    
    # Verificar se set_page_config pode ser chamado
    print("   ✅ Streamlit disponível")
    
except ImportError:
    print("   ❌ Streamlit NÃO instalado")
except Exception as e:
    print(f"   ⚠️ Erro: {e}")

# ============================================
# 6. RESUMO FINAL
# ============================================
print("\n" + "=" * 60)
print("📊 RESUMO DO DIAGNÓSTICO")
print("=" * 60)

# Contagem de problemas
problemas = []

if not Path("app.py").exists():
    problemas.append("app.py não encontrado")
if not Path("Login.py").exists():
    problemas.append("Login.py não encontrado")
if not Path("services/auth_service.py").exists():
    problemas.append("auth_service.py não encontrado")

if problemas:
    print("❌ PROBLEMAS ENCONTRADOS:")
    for p in problemas:
        print(f"   - {p}")
    print("\n🔧 Execute as correções necessárias")
else:
    print("✅ Todos os arquivos essenciais estão OK!")
    print("\n🔑 Para testar o login localmente:")
    print("   streamlit run app.py")
    print("   Usuário: admin@lados.com")
    print("   Senha: admin123")

print("\n" + "=" * 60)
print("✅ DIAGNÓSTICO CONCLUÍDO!")
print("=" * 60)
