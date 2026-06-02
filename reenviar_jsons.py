import os
import json
from services.supabase_service import supabase_service

def enviar_json(caminho, tabela):
    """Envia dados JSON para o Supabase"""
    try:
        with open(caminho, "r", encoding="utf-8-sig") as f:
            dados = json.load(f)
        
        if not dados:
            print(f"   ⚠️ {os.path.basename(caminho)} está vazio")
            return
        
        if isinstance(dados, list):
            for item in dados:
                if item:
                    # Para turmas, enviar apenas campos válidos
                    if tabela == "turmas":
                        campos_validos = ["nome", "ano", "turno", "created_at"]
                        item = {k: v for k, v in item.items() if k in campos_validos}
                    
                    # Verificar se já existe
                    if "nome" in item and tabela == "turmas":
                        existing = supabase_service.client.table(tabela).select("*").eq("nome", item["nome"]).execute()
                        if existing.data:
                            print(f"   ⚠️ Turma {item['nome']} já existe")
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

print("📤 Reenviando JSONs corrigidos...")
print("")

pasta = "para_supabase"
for arquivo, tabela in mapeamento.items():
    caminho = os.path.join(pasta, arquivo)
    if os.path.exists(caminho):
        tamanho = os.path.getsize(caminho)
        if tamanho > 5:
            print(f"📄 {arquivo} → {tabela}")
            enviar_json(caminho, tabela)
        else:
            print(f"⚠️ {arquivo} está vazio")
    else:
        print(f"⚠️ {arquivo} não encontrado")
    print("")

print("✅ Envio concluído!")
