"""
Proficiência (TRI leve) - LADOS 2.0
Calcula pontuação ponderada por dificuldade dos itens
"""

import sys
import os

# Adicionar o caminho do projeto para imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

import math
from typing import List, Dict, Any
from domain.modelos.item import Item


class CalculadorProficiencia:
    """
    Calcula proficiência usando modelo TRI simplificado
    
    Fórmula: Pontuação = Somatório(acerto * peso_dificuldade) / Somatório(pesos)
    Onde peso_dificuldade = 1 + (dificuldade * 2)
    """
    
    def __init__(self):
        # Pesos baseados na dificuldade do item (0=fácil, 1=difícil)
        self.peso_base = 1.0
        self.fator_dificuldade = 2.0
    
    def calcular_peso_item(self, dificuldade: float) -> float:
        """
        Calcula o peso de um item baseado em sua dificuldade
        
        Itens mais difíceis têm peso maior
        """
        return self.peso_base + (dificuldade * self.fator_dificuldade)
    
    def calcular_pontuacao_aluno(self, itens: List[Item], respostas: Dict[str, str]) -> Dict[str, Any]:
        """
        Calcula a pontuação ponderada do aluno
        
        Args:
            itens: Lista de itens da prova
            respostas: Dicionário {item_id: resposta_aluno}
        
        Returns:
            Dicionário com pontuação bruta, ponderada e porcentagem
        """
        pontuacao_ponderada = 0
        peso_total = 0
        acertos = 0
        
        resultados_por_item = []
        
        for item in itens:
            resposta = respostas.get(item.id, "")
            acertou = (resposta.upper() == item.gabarito.upper())
            
            peso = self.calcular_peso_item(item.dificuldade)
            peso_total += peso
            
            if acertou:
                pontuacao_ponderada += peso
                acertos += 1
            
            resultados_por_item.append({
                "item_id": item.id,
                "dificuldade": item.dificuldade,
                "peso": round(peso, 3),
                "acertou": acertou,
                "contribuicao": round(peso if acertou else 0, 3)
            })
        
        # Calcular porcentagem ponderada
        porcentagem_ponderada = (pontuacao_ponderada / peso_total * 100) if peso_total > 0 else 0
        
        # Calcular porcentagem simples (para comparação)
        porcentagem_simples = (acertos / len(itens) * 100) if itens else 0
        
        return {
            "acertos_simples": acertos,
            "total_itens": len(itens),
            "porcentagem_simples": round(porcentagem_simples, 1),
            "pontuacao_ponderada": round(pontuacao_ponderada, 2),
            "peso_total": round(peso_total, 2),
            "porcentagem_ponderada": round(porcentagem_ponderada, 1),
            "resultados_por_item": resultados_por_item
        }
    
    def calcular_proficiencia_turma(self, resultados_alunos: List[Dict]) -> Dict[str, Any]:
        """
        Calcula estatísticas agregadas de proficiência para uma turma
        
        Args:
            resultados_alunos: Lista de resultados individuais (do método calcular_pontuacao_aluno)
        
        Returns:
            Estatísticas agregadas da turma
        """
        if not resultados_alunos:
            return {
                "media_ponderada": 0,
                "media_simples": 0,
                "desvio_padrao": 0,
                "minimo": 0,
                "maximo": 0,
                "total_alunos": 0
            }
        
        pontuacoes_ponderadas = [r["porcentagem_ponderada"] for r in resultados_alunos]
        pontuacoes_simples = [r["porcentagem_simples"] for r in resultados_alunos]
        
        media_ponderada = sum(pontuacoes_ponderadas) / len(pontuacoes_ponderadas)
        media_simples = sum(pontuacoes_simples) / len(pontuacoes_simples)
        
        # Calcular desvio padrão
        variancia = sum((p - media_ponderada) ** 2 for p in pontuacoes_ponderadas) / len(pontuacoes_ponderadas)
        desvio_padrao = math.sqrt(variancia)
        
        return {
            "media_ponderada": round(media_ponderada, 1),
            "media_simples": round(media_simples, 1),
            "desvio_padrao": round(desvio_padrao, 1),
            "minimo": round(min(pontuacoes_ponderadas), 1),
            "maximo": round(max(pontuacoes_ponderadas), 1),
            "total_alunos": len(resultados_alunos)
        }


def testar_proficiencia():
    print("=" * 60)
    print("TESTANDO CALCULADOR DE PROFICIÊNCIA (TRI leve)")
    print("=" * 60)
    
    # Criar itens com diferentes dificuldades
    itens = [
        Item("Q001", "Questão fácil", ["A","B","C","D"], "A", "DESC_01", "Hab fácil", "erro_teste", 0.2),
        Item("Q002", "Questão média", ["A","B","C","D"], "A", "DESC_02", "Hab média", "erro_teste", 0.5),
        Item("Q003", "Questão difícil", ["A","B","C","D"], "A", "DESC_03", "Hab difícil", "erro_teste", 0.8),
    ]
    
    # Respostas de um aluno
    respostas = {"Q001": "A", "Q002": "B", "Q003": "A"}  # Acertou Q001 e Q003, errou Q002
    
    calculador = CalculadorProficiencia()
    resultado = calculador.calcular_pontuacao_aluno(itens, respostas)
    
    print(f"\n📊 RESULTADO DO ALUNO:")
    print(f"   Acertos simples: {resultado['acertos_simples']}/{resultado['total_itens']}")
    print(f"   % simples: {resultado['porcentagem_simples']}%")
    print(f"   % ponderada (TRI): {resultado['porcentagem_ponderada']}%")
    print(f"   Diferença: {resultado['porcentagem_ponderada'] - resultado['porcentagem_simples']:+.1f}%")
    
    print(f"\n📊 PESOS POR DIFICULDADE:")
    for r in resultado['resultados_por_item']:
        print(f"   {r['item_id']}: dificuldade={r['dificuldade']} → peso={r['peso']} {'✓' if r['acertou'] else '✗'}")
    
    print("\n✅ TESTE CONCLUÍDO!")


if __name__ == "__main__":
    testar_proficiencia()
