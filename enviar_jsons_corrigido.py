import os
import json
from services.supabase_service import supabase_service

def corrigir_bom_e_enviar(caminho, tabela):
    """Remove BOM e envia dados para o Supabase"""
    try:
        # Ler arquivo removendo BOM
        with open(caminho, "r", encoding="utf-8-sig") as f:
            dados = json.load(f)
        
        if not dados:
            print(f"   ⚠️ {os.path.basename(caminho)} está vazio")
            return
        
        # Se for lista, enviar cada item
        if isinstance(dados, list):
            for item in dados:
                if item:
                    # Remover campos vazios
                    item = {k: v for k, v in item.items() if v not in [None, "", []]}
                    
                    # Verificar se já existe (usando email)
                    if "email" in item:
                        existing = supabase_service.client.table(tabela).select("*").eq("email", item["email"]).execute()
                        if existing.data:
                            print(f"   ⚠️ {item.get('nome', item.get('email'))} já existe")
                            continue
                    
                    supabase_service.client.table(tabela).insert(item).execute()
                    print(f"   ✅ Item inserido em {tabela}")
        else:
            supabase_service.client.table(tabela).insert(dados).execute()
            print(f"   ✅ Dados inseridos em {tabela}")
            
    except Exception as e:
        print(f"   ❌ Erro: {e}")

# Mapeamento
mapeamento = {
    "usuarios.json": "usuarios",
    "turmas.json": "turmas",
    "alunos.json": "alunos"
}

print("📤 Enviando JSONs...")
print("")

pasta = "para_supabase"
for arquivo, tabela in mapeamento.items():
    caminho = os.path.join(pasta, arquivo)
    if os.path.exists(caminho):
        tamanho = os.path.getsize(caminho)
        if tamanho > 5:  # ignorar arquivos vazios
            print(f"📄 {arquivo} → {tabela}")
            corrigir_bom_e_enviar(caminho, tabela)
        else:
            print(f"⚠️ {arquivo} está vazio")
    else:
        print(f"⚠️ {arquivo} não encontrado")
    print("")

print("✅ Envio concluído!")
