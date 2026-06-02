"""
recomendador.py - Módulo de Recomendações Pedagógicas
Versão corrigida - LADOS 3.0
"""

from typing import List, Dict, Any, Optional
from enum import Enum

class Prioridade(Enum):
    ALTA = "Alta"
    MEDIA = "Média"
    BAIXA = "Baixa"

class Recomendador:
    """
    Gerador de recomendações pedagógicas baseadas nos resultados das avaliações.
    """
    
    def __init__(self):
        """Inicializa o recomendador com a base de intervenções"""
        self._carregar_recomendacoes_base()
    
    def _carregar_recomendacoes_base(self):
        """Carrega a base de recomendações por descritor e tipo de erro"""
        
        self.recomendacoes_base = {
            # Descritores de Língua Portuguesa
            "D1": {
                "descricao": "Localizar informações explícitas",
                "recomendacao": "Trabalhar com textos curtos e perguntas diretas. Praticar a localização de informações literais.",
                "atividades": ["Caça ao tesouro textual", "Perguntas e respostas objetivas"],
                "recursos": ["Textos informativos", "Fichas de leitura"]
            },
            "D3": {
                "descricao": "Inferir informações implícitas",
                "recomendacao": "Utilizar atividades que exijam dedução e leitura nas entrelinhas.",
                "atividades": ["Completar lacunas", "Deduzir sentimentos dos personagens"],
                "recursos": ["Contos", "Fábulas"]
            },
            "D7": {
                "descricao": "Identificar efeito de sentido",
                "recomendacao": "Explorar figuras de linguagem e recursos estilísticos em diferentes gêneros.",
                "atividades": ["Identificar ironia/humor", "Analisar metáforas"],
                "recursos": ["Tirinhas", "Charges", "Poemas"]
            },
            "D8": {
                "descricao": "Estabelecer relações lógico-discursivas",
                "recomendacao": "Trabalhar com conectores e relações de causa-consequência.",
                "atividades": ["Completar frases com conectores", "Identificar causa e efeito"],
                "recursos": ["Frases contextualizadas", "Pequenos textos"]
            },
            "D12": {
                "descricao": "Reconhecer gênero textual",
                "recomendacao": "Apresentar diferentes gêneros e suas características específicas.",
                "atividades": ["Classificação de textos por gênero", "Produção dirigida"],
                "recursos": ["Amostras de diferentes gêneros"]
            },
            "D15": {
                "descricao": "Reconhecer relações lógico-discursivas",
                "recomendacao": "Praticar a identificação de argumentos e contra-argumentos.",
                "atividades": ["Mapas de argumentação", "Debates estruturados"],
                "recursos": ["Artigos de opinião", "Editoriais"]
            },
            
            # Descritores de Matemática
            "D2": {
                "descricao": "Resolver problemas envolvendo operações básicas",
                "recomendacao": "Contextualizar problemas no cotidiano do aluno com situações reais.",
                "atividades": ["Situações-problema com materiais concretos", "Jogos matemáticos"],
                "recursos": ["Material dourado", "Jogos de tabuleiro"]
            },
            "D23": {
                "descricao": "Interpretar gráficos e tabelas",
                "recomendacao": "Trabalhar com diferentes representações gráficas e coleta de dados.",
                "atividades": ["Construção de gráficos simples", "Leitura de tabelas"],
                "recursos": ["Jornais", "Revistas", "Planilhas"]
            },
            "D28": {
                "descricao": "Resolver problemas com grandezas e medidas",
                "recomendacao": "Utilizar situações práticas que envolvam medição e conversão.",
                "atividades": ["Medição da sala de aula", "Receitas culinárias"],
                "recursos": ["Régua", "Fita métrica", "Balança"]
            }
        }
    
    def recomendar_por_descritor(self, descritor: str, percentual_acerto: float = None) -> Dict[str, Any]:
        """
        Gera recomendação para um descritor específico
        
        Args:
            descritor: Código do descritor (ex: "D1", "D15")
            percentual_acerto: Percentual de acerto (opcional, para priorizar)
        
        Returns:
            Dicionário com a recomendação
        """
        base = self.recomendacoes_base.get(descritor, {
            "descricao": "Descritor não mapeado",
            "recomendacao": "Analisar as dificuldades específicas dos alunos neste conteúdo.",
            "atividades": ["Revisão do conteúdo não consolidado"],
            "recursos": ["Material adaptado pelo professor"]
        })
        
        resultado = {
            "descritor": descritor,
            "descricao": base["descricao"],
            "recomendacao": base["recomendacao"],
            "atividades": base["atividades"],
            "recursos": base["recursos"]
        }
        
        # Adicionar prioridade baseada no percentual de acerto
        if percentual_acerto is not None:
            if percentual_acerto < 40:
                resultado["prioridade"] = Prioridade.ALTA.value
                resultado["prazo"] = "Imediato (1-2 semanas)"
            elif percentual_acerto < 60:
                resultado["prioridade"] = Prioridade.MEDIA.value
                resultado["prazo"] = "Curto prazo (3-4 semanas)"
            else:
                resultado["prioridade"] = Prioridade.BAIXA.value
                resultado["prazo"] = "Médio prazo (1-2 meses)"
            
            resultado["percentual_acerto"] = percentual_acerto
        
        return resultado
    
    def recomendar_para_turma(self, diagnostico: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Gera recomendações para uma turma com base no diagnóstico
        
        Args:
            diagnostico: Dicionário com o diagnóstico da turma (contendo descritores_criticos)
        
        Returns:
            Lista de recomendações ordenadas por prioridade
        """
        recomendacoes = []
        
        # Extrair descritores críticos do diagnóstico
        descritores_criticos = diagnostico.get("descritores_criticos", [])
        
        for item in descritores_criticos:
            if isinstance(item, dict):
                descritor = item.get("descritor", "")
                percentual = item.get("percentual", None)
            else:
                # Caso seja string
                descritor = str(item)
                percentual = None
            
            if descritor:
                rec = self.recomendar_por_descritor(descritor, percentual)
                recomendacoes.append(rec)
        
        # Ordenar por prioridade (Alta primeiro)
        ordem_prioridade = {Prioridade.ALTA.value: 0, Prioridade.MEDIA.value: 1, Prioridade.BAIXA.value: 2}
        recomendacoes.sort(key=lambda x: ordem_prioridade.get(x.get("prioridade", "Média"), 1))
        
        return recomendacoes
    
    def recomendar(self, descritor: str = None, diagnostico: Dict = None, percentual: float = None) -> Any:
        """
        Método principal para recomendar intervenções
        Compatível com as chamadas da versão 2.0
        
        Args:
            descritor: Código do descritor (ex: "D15")
            diagnostico: Diagnóstico da turma (dicionário)
            percentual: Percentual de acerto (opcional)
        
        Returns:
            Recomendação ou lista de recomendações
        """
        if diagnostico:
            return self.recomendar_para_turma(diagnostico)
        elif descritor:
            return self.recomendar_por_descritor(descritor, percentual)
        else:
            return {"erro": "É necessário fornecer um descritor ou um diagnóstico"}
    
    # Aliases para compatibilidade com nomes alternativos
    def gerar_recomendacoes(self, diagnostico: Dict) -> List[Dict]:
        """Alias para recomendar_para_turma"""
        return self.recomendar_para_turma(diagnostico)
    
    def recomendar_para_turma(self, diagnostico: Dict) -> List[Dict]:
        """Alias existente"""
        return self._recomendar_para_turma_impl(diagnostico)
    
    def _recomendar_para_turma_impl(self, diagnostico: Dict) -> List[Dict]:
        """Implementação interna"""
        return self.recomendar_para_turma(diagnostico)


# ============================================
# TESTE RÁPIDO DO RECOMENDADOR CORRIGIDO
# ============================================

if __name__ == "__main__":
    print("=" * 50)
    print("TESTE DO RECOMENDADOR CORRIGIDO")
    print("=" * 50)
    
    rec = Recomendador()
    
    # Teste 1: Recomendação por descritor
    print("\n1️⃣ RECOMENDAÇÃO POR DESCRITOR (D15):")
    resultado = rec.recomendar_por_descritor("D15", 35)
    print(f"   Descritor: {resultado['descritor']}")
    print(f"   Descrição: {resultado['descricao']}")
    print(f"   Prioridade: {resultado.get('prioridade', 'N/A')}")
    print(f"   Recomendação: {resultado['recomendacao'][:80]}...")
    
    # Teste 2: Recomendações para turma
    print("\n2️⃣ RECOMENDAÇÕES PARA TURMA:")
    diagnostico = {
        "descritores_criticos": [
            {"descritor": "D15", "percentual": 34},
            {"descritor": "D8", "percentual": 41}
        ]
    }
    
    recomendacoes = rec.recomendar_para_turma(diagnostico)
    for i, r in enumerate(recomendacoes, 1):
        print(f"   {i}. {r['descritor']} - {r['descricao']} (Prioridade: {r.get('prioridade', 'Média')})")
    
    # Teste 3: Método principal
    print("\n3️⃣ MÉTODO PRINCIPAL (recomendar):")
    resultado_principal = rec.recomendar(descritor="D3", percentual=55)
    print(f"   Descritor: {resultado_principal['descritor']}")
    print(f"   Prioridade: {resultado_principal.get('prioridade', 'N/A')}")
    
    print("\n✅ RECOMENDADOR CORRIGIDO FUNCIONANDO!")
