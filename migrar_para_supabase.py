import json
import requests
from pathlib import Path
from datetime import datetime
import os

SUPABASE_URL = "https://cxelepvrrkxmwwejniau.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImN4ZWxlcHZycmt4bXd3ZWpuaWF1Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3Nzg5MDc4MDUsImV4cCI6MjA5NDQ4MzgwNX0.qVnx3CEWuMdZyO-Nb_Y7xnencaIG5SH-rVgA-qmPLwM"

HEADERS = {
    "apikey": SUPABASE_KEY,
    "Authorization": f"Bearer {SUPABASE_KEY}",
    "Content-Type": "application/json",
    "Prefer": "return=minimal"
}

def log_mensagem(msg, tipo="INFO"):
    cores = {"INFO": "Cyan", "ERRO": "Red", "OK": "Green", "AVISO": "Yellow"}
    cor = cores.get(tipo, "White")
    print(f"[{tipo}] {msg}")

def ler_json_com_bom(caminho):
    """Lê JSON ignorando BOM (Byte Order Mark)"""
    with open(caminho, "r", encoding="utf-8-sig") as f:
        return json.load(f)

def verificar_estrutura_json(caminho_json):
    try:
        dados = ler_json_com_bom(caminho_json)
        if not dados:
            return {"erro": "JSON vazio", "campos": []}
        primeiro_item = dados[0] if isinstance(dados, list) else dados
        campos = list(primeiro_item.keys()) if isinstance(primeiro_item, dict) else []
        return {"sucesso": True, "campos": campos, "quantidade": len(dados) if isinstance(dados, list) else 1}
    except Exception as e:
        return {"erro": str(e), "campos": []}

def enviar_para_supabase(dados, tabela):
    """Envia dados para o Supabase com tratamento de erro RLS"""
    try:
        url = f"{SUPABASE_URL}/rest/v1/{tabela}"
        
        sucessos = 0
        erros = []
        
        for i, item in enumerate(dados):
            try:
                response = requests.post(url, headers=HEADERS, json=item, timeout=30)
                
                if response.status_code in [200, 201]:
                    sucessos += 1
                    if (i + 1) % 50 == 0:
                        log_mensagem(f"Progresso: {i+1}/{len(dados)} itens", "INFO")
                elif response.status_code == 401:
                    erros.append(f"Erro 401: Chave invalida ou RLS bloqueando")
                    break
                else:
                    erros.append(f"Erro {response.status_code}: {response.text[:100]}")
            except Exception as e:
                erros.append(str(e))
        
        return {"sucesso": sucessos, "total": len(dados), "erros": erros[:5]}
    except Exception as e:
        return {"erro": str(e)}

def migrar_json_para_supabase(caminho_json, tabela_destino, mapeamento_custom=None):
    log_mensagem(f"Analisando {caminho_json} → tabela {tabela_destino}", "INFO")
    
    verificacao = verificar_estrutura_json(caminho_json)
    if "erro" in verificacao:
        log_mensagem(f"ERRO: {verificacao['erro']}", "ERRO")
        return False
    
    log_mensagem(f"Campos: {verificacao['campos'][:5]}...", "INFO")
    log_mensagem(f"Itens: {verificacao['quantidade']}", "INFO")
    
    dados = ler_json_com_bom(caminho_json)
    
    # Se não for lista, transformar
    if not isinstance(dados, list):
        dados = [dados]
    
    # Aplicar mapeamento customizado se fornecido
    if mapeamento_custom:
        dados_mapeados = []
        for item in dados:
            novo_item = {}
            for campo_json, campo_supabase in mapeamento_custom.items():
                if campo_json in item:
                    novo_item[campo_supabase] = item[campo_json]
            if "created_at" not in novo_item:
                novo_item["created_at"] = datetime.now().isoformat()
            dados_mapeados.append(novo_item)
    else:
        dados_mapeados = dados
    
    resultado = enviar_para_supabase(dados_mapeados, tabela_destino)
    
    if "erro" in resultado:
        log_mensagem(f"Falha: {resultado['erro']}", "ERRO")
        return False
    else:
        log_mensagem(f"Migrado: {resultado['sucesso']}/{resultado['total']} itens", "OK")
        if resultado.get("erros"):
            log_mensagem(f"Erros: {resultado['erros'][:2]}", "AVISO")
        return resultado['sucesso'] > 0

if __name__ == "__main__":
    print("🚀 INICIANDO MIGRACAO DE DADOS...\n")
    
    backup_dir = Path(f"backups_json_{datetime.now().strftime('%Y%m%d_%H%M%S')}")
    backup_dir.mkdir(exist_ok=True)
    
    import shutil
    for arquivo in ["data/usuarios.json", "data/turmas.json", "data/itens.json"]:
        if Path(arquivo).exists():
            shutil.copy(arquivo, backup_dir / Path(arquivo).name)
            log_mensagem(f"Backup: {backup_dir}/{Path(arquivo).name}", "OK")
    
    print("")
    
    # Mapeamentos customizados
    mapeamentos = {
        "usuarios": {
            "email": "email",
            "senha": "senha_hash", 
            "nome": "nome",
            "perfil": "perfil"
        },
        "turmas": {
            "nome": "nome",
            "ano": "ano",
            "turno": "turno"
        }
    }
    
    resultados = []
    
    # Migrar usuarios
    if Path("data/usuarios.json").exists():
        dados = ler_json_com_bom("data/usuarios.json")
        if isinstance(dados, list) and len(dados) > 0:
            sucesso = migrar_json_para_supabase("data/usuarios.json", "usuarios", mapeamentos["usuarios"])
            resultados.append({"arquivo": "usuarios.json", "sucesso": sucesso})
    
    # Migrar turmas
    if Path("data/turmas.json").exists():
        sucesso = migrar_json_para_supabase("data/turmas.json", "turmas", mapeamentos["turmas"])
        resultados.append({"arquivo": "turmas.json", "sucesso": sucesso})
    
    # Migrar questoes (sem mapeamento, enviar direto)
    if Path("data/itens.json").exists():
        sucesso = migrar_json_para_supabase("data/itens.json", "questoes")
        resultados.append({"arquivo": "itens.json", "sucesso": sucesso})
    
    print("\n" + "="*50)
    print("RELATORIO FINAL")
    print("="*50)
    for r in resultados:
        status = "✅" if r["sucesso"] else "❌"
        print(f"{status} {r['arquivo']}")
    
    print("\n✅ MIGRACAO CONCLUIDA!")
