"""
analisador.py - Versão com suporte a operacao_cognitiva
"""

from typing import Dict, List, Any
from collections import Counter

class Analisador:
    """Analisa resultados de prova com suporte a diagnóstico por erro"""

    def diagnosticar(self, resultado_prova: Dict[str, Any]) -> Dict[str, Any]:
        """
        Diagnostica uma prova, incluindo distribuição de erros
        
        Args:
            resultado_prova: Dicionário com respostas do aluno e gabarito
        
        Returns:
            Dicionário com diagnóstico completo
        """
        respostas = resultado_prova.get("respostas", [])
        questoes = resultado_prova.get("questoes", [])
        
        # Contadores
        total = len(questoes)
        acertos = 0
        erros_por_tipo = Counter()
        operacoes_por_acerto = Counter()
        
        # Para cada questão
        for i, questao in enumerate(questoes):
            resposta_aluno = respostas[i] if i < len(respostas) else None
            gabarito = questao.get("gabarito")
            alternativas = questao.get("alternativas", [])
            
            # Registrar operação cognitiva
            operacao = questao.get("operacao_cognitiva", questao.get("nivel_bloom", ["desconhecido"])[0] if questao.get("nivel_bloom") else "desconhecido")
            
            # Verificar se acertou
            if resposta_aluno == gabarito:
                acertos += 1
                operacoes_por_acerto[operacao] += 1
            else:
                # Identificar o erro associado à alternativa marcada
                erro = self._identificar_erro_por_alternativa(resposta_aluno, alternativas)
                if erro:
                    erros_por_tipo[erro] += 1
        
        # Calcular percentuais
        percentual_acerto = (acertos / total * 100) if total > 0 else 0
        
        # Classificar nível SAEB
        nivel = self._classificar_nivel(percentual_acerto, resultado_prova.get("ano", "5EF"))
        
        # Preparar resultado
        diagnostico = {
            "total_questoes": total,
            "acertos": acertos,
            "percentual_acerto": round(percentual_acerto, 2),
            "nivel": nivel,
            "distribuicao_erros": dict(erros_por_tipo),
            "erro_predominante": erros_por_tipo.most_common(1)[0][0] if erros_por_tipo else None,
            "operacoes_cognitivas": dict(operacoes_por_acerto)
        }
        
        # Adicionar sugestão de intervenção
        diagnostico["intervencao_sugerida"] = self._sugerir_intervencao(erros_por_tipo)
        
        return diagnostico
    
    def _identificar_erro_por_alternativa(self, letra: str, alternativas: List) -> str:
        """Identifica o erro associado a uma alternativa específica"""
        if not alternativas:
            return None
        
        # Formato 1:1 (dicionário com erro_associado)
        if isinstance(alternativas[0], dict):
            for alt in alternativas:
                if alt.get("letra") == letra:
                    return alt.get("erro_associado", "")
        
        # Fallback: formato antigo (lista de strings)
        return None
    
    def _classificar_nivel(self, percentual: float, ano: str) -> str:
        """Classifica o nível de proficiência baseado no percentual"""
        if percentual >= 90:
            return "Avançado"
        elif percentual >= 70:
            return "Proficiente"
        elif percentual >= 50:
            return "Básico"
        elif percentual >= 30:
            return "Elementar"
        else:
            return "Inicial"
    
    def _sugerir_intervencao(self, erros_por_tipo: Counter) -> str:
        """Sugere intervenção pedagógica baseada nos erros predominantes"""
        if not erros_por_tipo:
            return "Nenhum erro identificado"
        
        predominante = erros_por_tipo.most_common(1)[0][0]
        
        intervencoes = {
            "lp_decodificacao": "Trabalhar consciência fonológica e correspondência letra-som",
            "lp_leitura_literal": "Praticar localização de informações explícitas no texto",
            "lp_inferencia": "Desenvolver atividades de inferência com contos e fábulas",
            "lp_vocabulario": "Ampliar vocabulário com leitura diversificada",
            "lp_intencao_autor": "Discutir propósito comunicativo de diferentes gêneros",
            "mat_contagem": "Retomar correspondência um-para-um com materiais concretos",
            "mat_escrita": "Praticar escrita e reconhecimento de números",
            "mat_espacial": "Trabalhar noções de posição e orientação",
            "mat_operacao": "Revisar operações básicas com situações-problema",
            "mat_interpretacao": "Praticar interpretação de enunciados",
            "mat_conceito": "Retomar conceitos fundamentais com exemplos",
            "mat_algoritmo": "Revisar passo a passo dos algoritmos"
        }
        
        return intervencoes.get(predominante, "Intervenção pedagógica direcionada")
    
    def diagnosticar_turma(self, resultados: List[Dict]) -> Dict[str, Any]:
        """Agrega diagnósticos de múltiplos alunos em uma turma"""
        if not resultados:
            return {"erro": "Nenhum resultado fornecido"}
        
        total_alunos = len(resultados)
        sum_acertos = sum(r.get("percentual_acerto", 0) for r in resultados)
        media_turma = sum_acertos / total_alunos if total_alunos > 0 else 0
        
        # Agregar erros
        todos_erros = Counter()
        todas_operacoes = Counter()
        for r in resultados:
            erros = r.get("distribuicao_erros", {})
            for erro, qtd in erros.items():
                todos_erros[erro] += qtd
            ops = r.get("operacoes_cognitivas", {})
            for op, qtd in ops.items():
                todas_operacoes[op] += qtd
        
        # Identificar padrões da turma
        erro_mais_comum = todos_erros.most_common(1)[0][0] if todos_erros else None
        percentual_erro_mais_comum = (todos_erros[erro_mais_comum] / sum(todos_erros.values()) * 100) if todos_erros else 0
        
        # Identificar operação cognitiva mais fraca
        operacao_mais_fraca = min(todas_operacoes, key=lambda x: todas_operacoes[x]) if todas_operacoes else None
        
        return {
            "total_alunos": total_alunos,
            "media_turma": round(media_turma, 2),
            "distribuicao_erros_turma": dict(todos_erros),
            "erro_mais_comum": erro_mais_comum,
            "percentual_erro_mais_comum": round(percentual_erro_mais_comum, 2),
            "operacao_cognitiva_mais_fraca": operacao_mais_fraca,
            "intervencao_recomendada": self._sugerir_intervencao(todos_erros)
        }


# Teste rápido se executado diretamente
if __name__ == "__main__":
    import json
    
    with open("data/itens.json", "r", encoding="utf-8") as f:
        itens = json.load(f)
    
    if itens:
        print("🔍 TESTANDO ANALISADOR COM OPERACAO_COGNITIVA")
        print("="*50)
        
        # Verificar se tem operacao_cognitiva
        primeiro = itens[0]
        if "operacao_cognitiva" in primeiro:
            print(f"✅ Campo presente: {primeiro['operacao_cognitiva']}")
        else:
            print("⚠️ Campo 'operacao_cognitiva' não encontrado. Execute o script de migração primeiro.")
        
        # Testar diagnóstico
        respostas = ["A", "B", "C", "D"] + ["A"] * (len(itens) - 4)
        resultado = {"questoes": itens[:4], "respostas": respostas[:4], "ano": "5EF"}
        analisador = Analisador()
        diagnostico = analisador.diagnosticar(resultado)
        
        print(f"\nTotal: {diagnostico['total_questoes']}")
        print(f"Acertos: {diagnostico['acertos']}")
        print(f"Percentual: {diagnostico['percentual_acerto']}%")
        print(f"Nível: {diagnostico['nivel']}")
        print(f"Operações cognitivas: {diagnostico['operacoes_cognitivas']}")
        print(f"Distribuição de erros: {diagnostico['distribuicao_erros']}")
        print(f"Intervenção: {diagnostico['intervencao_sugerida']}")
        
        print("\n✅ Analisador atualizado com suporte a operacao_cognitiva!")

