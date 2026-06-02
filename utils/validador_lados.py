import json
import sys
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Tuple

print("="*60)
print("🔒 VALIDADOR AUTOMÁTICO DO LADOS")
print("="*60)

# ============================================
# CONFIGURAÇÕES
# ============================================
SCHEMA_VERSION = "1.0"
TAXONOMY_VERSION = "1.0"

# Campos obrigatórios do schema
CAMPOS_OBRIGATORIOS = [
    "id", "enunciado", "alternativas", "gabarito", "descritor",
    "habilidade", "operacao_cognitiva", "dificuldade_qualitativa",
    "ano", "disciplina", "tipo", "matriz", "ativo",
    "contexto", "posicao_incognita", "sub_habilidade"
]

# Taxonomia fechada de erros
TAXONOMIA_ERROS = {
    # Matemática
    "mat_contagem": True,
    "mat_escrita_num": True,
    "mat_valor_posicional": True,
    "mat_operacao_inversa": True,
    "mat_interpretacao": True,
    "mat_estimativa": True,
    # Português
    "lp_decodificacao": True,
    "lp_leitura_literal": True,
    "lp_vocabulario": True,
    "lp_inferencia": True,
    "lp_intencao_autor": True,
    "lp_fluencia": True,
    # Correto (alternativa certa)
    "": True
}

# Dificuldades válidas
DIFICULDADES_VALIDAS = ["facil", "medio", "dificil"]

# Disciplinas válidas
DISCIPLINAS_VALIDAS = ["LP", "MAT"]

# Tipos válidos
TIPOS_VALIDOS = ["multipla_escolha", "leitura", "escrita", "leitura_oral"]

# Anos válidos
ANOS_VALIDOS = ["1EF", "2EF", "3EF", "4EF", "5EF", "6EF", "7EF", "8EF", "9EF"]

# ============================================
# FUNÇÕES DE VALIDAÇÃO
# ============================================

def validar_campos_obrigatorios(questao: Dict) -> List[str]:
    """Verifica se todos os campos obrigatórios estão presentes"""
    erros = []
    for campo in CAMPOS_OBRIGATORIOS:
        if campo not in questao:
            erros.append(f"Campo obrigatório ausente: '{campo}'")
    return erros

def validar_valores_campo(questao: Dict) -> List[str]:
    """Verifica se os valores dos campos estão dentro dos permitidos"""
    erros = []
    
    # Validar ano
    ano = questao.get("ano", "")
    if ano not in ANOS_VALIDOS:
        erros.append(f"Ano inválido: '{ano}'. Deve ser um de: {ANOS_VALIDOS}")
    
    # Validar disciplina
    disciplina = questao.get("disciplina", "")
    if disciplina not in DISCIPLINAS_VALIDAS:
        erros.append(f"Disciplina inválida: '{disciplina}'. Deve ser LP ou MAT")
    
    # Validar tipo
    tipo = questao.get("tipo", "")
    if tipo not in TIPOS_VALIDOS:
        erros.append(f"Tipo inválido: '{tipo}'. Deve ser um de: {TIPOS_VALIDOS}")
    
    # Validar dificuldade
    dificuldade = questao.get("dificuldade_qualitativa", "")
    if dificuldade not in DIFICULDADES_VALIDAS:
        erros.append(f"Dificuldade inválida: '{dificuldade}'. Deve ser facil, medio ou dificil")
    
    # Validar matriz
    matriz = questao.get("matriz", "")
    if matriz not in ["BNCC", "CNCA", "SAEB"]:
        erros.append(f"Matriz inválida: '{matriz}'")
    
    return erros

def validar_alternativas(questao: Dict) -> List[str]:
    """Verifica se as alternativas estão no formato correto"""
    erros = []
    alternativas = questao.get("alternativas", [])
    
    # Questões de escrita podem não ter alternativas
    if questao.get("tipo") == "escrita" and not alternativas:
        return erros
    
    if len(alternativas) != 4:
        erros.append(f"Deveria ter 4 alternativas, tem {len(alternativas)}")
    
    letras_encontradas = set()
    for i, alt in enumerate(alternativas):
        letra = alt.get("letra", "")
        if letra:
            letras_encontradas.add(letra)
        
        # Validar erro_associado
        erro = alt.get("erro_associado", "")
        if erro not in TAXONOMIA_ERROS:
            erros.append(f"Alternativa {letra}: erro_associado inválido '{erro}'")
        
        # Verificar texto
        if not alt.get("texto"):
            erros.append(f"Alternativa {letra}: texto ausente")
    
    # Verificar se tem exatamente uma correta
    corretas = [alt for alt in alternativas if alt.get("erro_associado") == ""]
    if len(corretas) != 1:
        erros.append(f"Deveria ter 1 alternativa correta, tem {len(corretas)}")
    
    # Verificar gabarito consistente
    gabarito = questao.get("gabarito", "")
    if gabarito and gabarito not in letras_encontradas:
        erros.append(f"Gabarito '{gabarito}' não corresponde a nenhuma alternativa")
    
    return erros

def validar_contexto(questao: Dict) -> List[str]:
    """Verifica o campo contexto"""
    erros = []
    contexto = questao.get("contexto", "")
    
    # Apenas aviso se for "geral", não erro fatal
    if contexto == "geral":
        pass  # Apenas aviso, não erro
    
    return erros

def validar_posicao_incognita(questao: Dict) -> List[str]:
    """Verifica o campo posicao_incognita (apenas para Matemática)"""
    erros = []
    disciplina = questao.get("disciplina", "")
    posicao = questao.get("posicao_incognita", "")
    
    if disciplina == "MAT" and posicao not in ["final", "inicial", "intermediaria", "nao_aplicavel"]:
        erros.append(f"Posição da incógnita inválida para MAT: '{posicao}'")
    
    return erros

def validar_sub_habilidade(questao: Dict) -> List[str]:
    """Verifica o campo sub_habilidade"""
    erros = []
    sub_habilidade = questao.get("sub_habilidade", "")
    
    # Apenas aviso se for genérico, não erro fatal
    if sub_habilidade in ["nao_classificado", "compreensao_textual", "operacao_matematica"]:
        pass  # Apenas aviso
    
    return erros

def validar_versao(questao: Dict) -> List[str]:
    """Verifica se a questão tem campos de versão"""
    erros = []
    
    if "schema_version" not in questao:
        erros.append("Campo 'schema_version' ausente (recomendado)")
    elif questao.get("schema_version") != SCHEMA_VERSION:
        erros.append(f"schema_version incompatível: {questao.get('schema_version')} (esperado {SCHEMA_VERSION})")
    
    if "taxonomy_version" not in questao:
        erros.append("Campo 'taxonomy_version' ausente (recomendado)")
    
    return erros

# ============================================
# VALIDADOR PRINCIPAL
# ============================================

class ValidadorLADOS:
    """Validador automático do LADOS"""
    
    def __init__(self):
        self.erros_totais = 0
        self.questoes_validas = 0
        self.questoes_invalidas = 0
    
    def validar_questao(self, questao: Dict) -> Tuple[bool, List[str]]:
        """Valida uma questão e retorna (aprovado, lista_de_erros)"""
        todos_erros = []
        
        # Executar todas as validações
        todos_erros.extend(validar_campos_obrigatorios(questao))
        todos_erros.extend(validar_valores_campo(questao))
        todos_erros.extend(validar_alternativas(questao))
        todos_erros.extend(validar_posicao_incognita(questao))
        todos_erros.extend(validar_versao(questao))
        
        # Apenas avisos (não reprovam)
        validar_contexto(questao)
        validar_sub_habilidade(questao)
        
        aprovado = len(todos_erros) == 0
        return aprovado, todos_erros
    
    def validar_arquivo(self, caminho: str) -> Dict:
        """Valida todas as questões de um arquivo JSON"""
        with open(caminho, "r", encoding="utf-8-sig") as f:
            questoes = json.load(f)
        
        resultados = {
            "total": len(questoes),
            "validas": 0,
            "invalidas": 0,
            "erros_por_questao": {}
        }
        
        for q in questoes:
            aprovado, erros = self.validar_questao(q)
            if aprovado:
                resultados["validas"] += 1
            else:
                resultados["invalidas"] += 1
                resultados["erros_por_questao"][q.get("id", "unknown")] = erros
        
        return resultados

# ============================================
# TESTE DO VALIDADOR COM O BANCO ATUAL
# ============================================
print("\n🧪 TESTANDO VALIDADOR COM O BANCO ATUAL...")

validador = ValidadorLADOS()
resultados = validador.validar_arquivo("data/itens.json")

print(f"\n📊 RESULTADOS DA VALIDAÇÃO:")
print(f"   Total de questões: {resultados['total']}")
print(f"   ✅ Válidas: {resultados['validas']}")
print(f"   ❌ Inválidas: {resultados['invalidas']}")

if resultados["invalidas"] > 0:
    print(f"\n⚠️ QUESTÕES INVÁLIDAS:")
    for id_q, erros in list(resultados["erros_por_questao"].items())[:5]:
        print(f"   {id_q}:")
        for erro in erros[:3]:
            print(f"      - {erro}")
    if len(resultados["erros_por_questao"]) > 5:
        print(f"   ... e mais {len(resultados['erros_por_questao']) - 5} questões")

# ============================================
# ADICIONAR CAMPOS DE VERSÃO AO BANCO
# ============================================
print("\n📝 ADICIONANDO CAMPOS DE VERSÃO AO BANCO...")

with open("data/itens.json", "r", encoding="utf-8") as f:
    itens = json.load(f)

atualizadas = 0
for item in itens:
    modificado = False
    if "schema_version" not in item:
        item["schema_version"] = SCHEMA_VERSION
        modificado = True
    if "taxonomy_version" not in item:
        item["taxonomy_version"] = TAXONOMY_VERSION
        modificado = True
    if modificado:
        atualizadas += 1

with open("data/itens.json", "w", encoding="utf-8") as f:
    json.dump(itens, f, indent=2, ensure_ascii=False)

print(f"   ✅ {atualizadas} questões atualizadas com campos de versão")

# ============================================
# FUNÇÃO PARA VALIDAR NOVAS QUESTÕES
# ============================================
print("\n" + "="*60)
print("✅ VALIDADOR AUTOMÁTICO PRONTO PARA USO!")
print("="*60)

print("""
📋 COMO USAR O VALIDADOR:

1. Para validar uma única questão:
   from validador import ValidadorLADOS
   validador = ValidadorLADOS()
   aprovado, erros = validador.validar_questao(questao_json)

2. Para validar um arquivo:
   validador = ValidadorLADOS()
   resultados = validador.validar_arquivo("caminho/arquivo.json")

3. O validador rejeita automaticamente questões que:
   - Faltam campos obrigatórios
   - Têm erro_associado fora da taxonomia
   - Têm formato inválido de alternativas
   - Têm schema_version incompatível
""")
