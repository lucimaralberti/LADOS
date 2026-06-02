import time
import streamlit as st

print("🔍 DIAGNÓSTICO DE PERFORMANCE - LADOS 2.0")
print("")

# 1. Testar importação do OpenCV
print("1. Testando importação do OpenCV...")
start = time.time()
try:
    import cv2
    print(f"   ✅ OpenCV importado em {time.time()-start:.2f}s")
except:
    print(f"   ❌ Erro: {time.time()-start:.2f}s")

# 2. Testar importação do ReportLab
print("\n2. Testando importação do ReportLab...")
start = time.time()
try:
    from reportlab.lib.pagesizes import A4
    print(f"   ✅ ReportLab importado em {time.time()-start:.2f}s")
except:
    print(f"   ❌ Erro: {time.time()-start:.2f}s")

# 3. Testar importação do Supabase
print("\n3. Testando importação do Supabase...")
start = time.time()
try:
    from services.supabase_service import supabase_service
    print(f"   ✅ Supabase importado em {time.time()-start:.2f}s")
except:
    print(f"   ❌ Erro: {time.time()-start:.2f}s")

# 4. Testar carregamento de descritores
print("\n4. Testando carregamento de descritores BNCC...")
start = time.time()
try:
    from services.descritores_service import descritores_service
    descritores = descritores_service.get_descritores_bncc("5º Ano", "Matemática")
    print(f"   ✅ Descritores carregados em {time.time()-start:.2f}s ({len(descritores)} itens)")
except Exception as e:
    print(f"   ❌ Erro: {e}")

# 5. Testar cache do Streamlit
print("\n5. Verificando cache do Streamlit...")
@st.cache_data(ttl=60)
def funcao_teste():
    time.sleep(0.5)
    return "teste"

start = time.time()
funcao_teste()
print(f"   ✅ Primeira execução: {time.time()-start:.2f}s")

start = time.time()
funcao_teste()
print(f"   ✅ Segunda execução (cacheada): {time.time()-start:.2f}s")

print("\n✅ Diagnóstico concluído!")
