import streamlit as st
import sys
import os
from pathlib import Path

st.set_page_config(page_title="Diagnóstico LADOS", page_icon="🔍", layout="wide")

st.title("🔍 Diagnóstico do Sistema LADOS")
st.markdown("---")

# 1. Informações do ambiente
st.header("📌 Ambiente")
st.write(f"Python: {sys.version}")
st.write(f"Diretório atual: {os.getcwd()}")

# 2. Verificar arquivos
st.header("📁 Arquivos e Pastas")
col1, col2 = st.columns(2)

with col1:
    st.subheader("Arquivos na raiz")
    for item in Path(".").iterdir():
        if item.is_file():
            st.write(f"- {item.name}")

with col2:
    st.subheader("Pastas importantes")
    for pasta in ["services", "data", "pages"]:
        if Path(pasta).exists():
            st.success(f"✅ {pasta}/")
            for item in Path(pasta).iterdir():
                if item.is_file():
                    st.write(f"  - {pasta}/{item.name}")
        else:
            st.error(f"❌ {pasta}/")

# 3. Testar importações
st.header("🔐 Teste de Importações")

try:
    from services.auth_service import AuthService
    st.success("✅ AuthService importado com sucesso")
    
    auth = AuthService(usar_supabase=False)
    st.success("✅ Instância do AuthService criada")
    
    # Testar autenticação
    st.subheader("👤 Teste de Autenticação")
    usuario = auth.autenticar("admin@lados.com", "admin123")
    if usuario:
        st.success(f"✅ Login funcionou! Usuário: {usuario.get('nome')} (role: {usuario.get('role')})")
    else:
        st.error("❌ Login falhou - admin@lados.com/admin123")
        
except Exception as e:
    st.error(f"❌ Erro no AuthService: {e}")

# 4. Testar SupabaseService
st.header("🗄️ Teste do SupabaseService")

try:
    from services.supabase_service import SupabaseService
    st.success("✅ SupabaseService importado")
    
    supabase = SupabaseService()
    st.success("✅ Instância do SupabaseService criada")
    
    # Verificar método
    if hasattr(supabase, 'autenticar_usuario'):
        st.success("✅ Método 'autenticar_usuario' existe")
        usuario = supabase.autenticar_usuario("admin@lados.com", "admin123")
        if usuario:
            st.success(f"✅ autenticar_usuario funcionou! Usuário: {usuario.get('nome')}")
        else:
            st.error("❌ autenticar_usuario falhou")
    else:
        st.error("❌ Método 'autenticar_usuario' NÃO existe")
        
except Exception as e:
    st.error(f"❌ Erro no SupabaseService: {e}")

# 5. Conteúdo do usuarios.json
st.header("📄 Conteúdo do data/usuarios.json")

if Path("data/usuarios.json").exists():
    import json
    with open("data/usuarios.json", "r") as f:
        usuarios = json.load(f)
    st.write(usuarios)
else:
    st.error("❌ Arquivo data/usuarios.json não encontrado!")

st.markdown("---")
st.info("🔑 Para testar, use: admin@lados.com / admin123")
