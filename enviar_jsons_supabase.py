import os
import json
from services.supabase_service import supabase_service

# Mapeamento de arquivos JSON para tabelas
mapeamento = {
    "usuarios.json": "usuarios",
    "turmas.json": "turmas",
    "alunos.json": "alunos",
    "provas.json": "provas",
    "correcoes.json": "correcoes",
    "sessoes_correcao.json": "sessoes_correcao",
    "atividades.json": "atividades",
    "historico_diagnosticos.json": "historico_diagnosticos"
}

def enviar_json(caminho, tabela):
    """Envia dados JSON para o Supabase"""
    try:
        with open(caminho, "r", encoding="utf-8") as f:
            dados = json.load(f)
        
        if not dados:
            print(f"   ⚠️ {os.path.basename(caminho)} está vazio")
            return
        
        # Se for lista, enviar cada item
        if isinstance(dados, list):
            for item in dados:
                if item:  # ignorar itens vazios
                    # Verificar se já existe (usando email ou id como chave)
                    if "email" in item:
                        existing = supabase_service.client.table(tabela).select("*").eq("email", item["email"]).execute()
                        if existing.data:
                            print(f"   ⚠️ {item.get('nome', item.get('email'))} já existe em {tabela}")
                            continue
                    supabase_service.client.table(tabela).insert(item).execute()
                    print(f"   ✅ Item inserido em {tabela}")
        else:
            # Objeto único
            supabase_service.client.table(tabela).insert(dados).execute()
            print(f"   ✅ Dados inseridos em {tabela}")
            
    except Exception as e:
        print(f"   ❌ Erro ao processar {os.path.basename(caminho)}: {e}")

print("📤 Enviando JSONs para o Supabase...")
print("")

pasta = "para_supabase"
for arquivo, tabela in mapeamento.items():
    caminho = os.path.join(pasta, arquivo)
    if os.path.exists(caminho):
        tamanho = os.path.getsize(caminho)
        if tamanho > 0:
            print(f"📄 {arquivo} → {tabela} ({tamanho} bytes)")
            enviar_json(caminho, tabela)
        else:
            print(f"⚠️ {arquivo} está vazio, ignorado")
    else:
        print(f"⚠️ {arquivo} não encontrado")
    print("")

print("✅ Envio concluído!")
