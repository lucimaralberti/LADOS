"""
Selecionador de Itens - LADOS 2.0
Com distribuição proporcional SAEB (30% fácil, 50% médio, 20% difícil)
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import json
import random
from typing import List, Dict, Optional
from domain.modelos.item import Item, Alternativa


class SelecionadorItens:
    """
    Gerencia o banco de itens e seleciona questões para a prova
    com distribuição proporcional SAEB
    """
    
    def __init__(self, arquivo_json: str = "data/itens.json"):
        self.arquivo_json = arquivo_json
        self.itens: List[Item] = []
        self._carregar_itens()
    
    def _carregar_itens(self):
        if not os.path.exists(self.arquivo_json):
            print(f"⚠️ Arquivo {self.arquivo_json} não encontrado!")
            return
        
        try:
            with open(self.arquivo_json, 'r', encoding='utf-8') as f:
                dados = json.load(f)
            
            self.itens = []
            for item_data in dados.get('itens', []):
                alternativas = []
                for alt_data in item_data.get('alternativas', []):
                    alternativas.append(Alternativa.from_dict(alt_data))
                
                item = Item(
                    id=item_data['id'],
                    ano=item_data.get('ano', ''),
                    descritor=item_data['descritor'],
                    nivel=item_data.get('nivel', 'medio'),
                    area=item_data.get('area', ''),
                    habilidade=item_data.get('habilidade', ''),
                    dificuldade=item_data.get('dificuldade', 0.5),
                    texto=item_data.get('texto', ''),
                    enunciado=item_data.get('enunciado', ''),
                    alternativas=alternativas,
                    gabarito=item_data['gabarito'],
                    tipo_erro_provavel=item_data.get('tipo_erro_provavel', ''),
                    mapa_erros=item_data.get('mapa_erros', {}),
                    justificativa_correta=item_data.get('justificativa_correta', '')
                )
                self.itens.append(item)
            
            print(f"✅ Carregados {len(self.itens)} itens do banco")
        
        except Exception as e:
            print(f"❌ Erro ao carregar itens: {e}")
    
    def get_itens_por_descriptor(self, descritor: str) -> List[Item]:
        return [item for item in self.itens if item.descritor == descritor]
    
    def get_itens_por_nivel_dificuldade(self, nivel: str) -> List[Item]:
        """
        Retorna itens por nível de dificuldade
        fácil: dificuldade < 0.4
        médio: 0.4 <= dificuldade < 0.7
        difícil: dificuldade >= 0.7
        """
        if nivel == "facil":
            return [item for item in self.itens if item.dificuldade < 0.4]
        elif nivel == "medio":
            return [item for item in self.itens if 0.4 <= item.dificuldade < 0.7]
        elif nivel == "dificil":
            return [item for item in self.itens if item.dificuldade >= 0.7]
        return []
    
    def get_descritores_disponiveis(self, ano: str = None) -> List[str]:
        descritores = set()
        for item in self.itens:
            if ano and item.ano != ano:
                continue
            descritores.add(item.descritor)
        return sorted(list(descritores))
    
    def selecionar_questoes_saeb(self, descritores: List[str], quantidade: int) -> List[Item]:
        """
        Seleciona questões com distribuição proporcional SAEB:
        - 30% fáceis (dificuldade < 0.4)
        - 50% médias (dificuldade 0.4-0.7)
        - 20% difíceis (dificuldade >= 0.7)
        """
        # Calcular quantidades por nível
        qtd_facil = round(quantidade * 0.3)
        qtd_medio = round(quantidade * 0.5)
        qtd_dificil = quantidade - qtd_facil - qtd_medio
        
        # Ajustar se necessário
        if qtd_facil + qtd_medio + qtd_dificil != quantidade:
            qtd_facil += quantidade - (qtd_facil + qtd_medio + qtd_dificil)
        
        print(f"📊 Distribuição SAEB: {qtd_facil} fáceis, {qtd_medio} médias, {qtd_dificil} difíceis")
        
        # Filtrar itens pelos descritores
        itens_por_descriptor = {}
        for desc in descritores:
            itens_por_descriptor[desc] = self.get_itens_por_descriptor(desc)
        
        # Separar por nível de dificuldade
        itens_facil = []
        itens_medio = []
        itens_dificil = []
        
        for desc, itens_lista in itens_por_descriptor.items():
            for item in itens_lista:
                if item.dificuldade < 0.4:
                    itens_facil.append(item)
                elif 0.4 <= item.dificuldade < 0.7:
                    itens_medio.append(item)
                else:
                    itens_dificil.append(item)
        
        # Verificar disponibilidade
        if len(itens_facil) < qtd_facil:
            print(f"⚠️ Apenas {len(itens_facil)} questões fáceis disponíveis. Ajustando...")
            qtd_facil = len(itens_facil)
            qtd_medio += (quantidade - qtd_facil - qtd_medio)
        
        if len(itens_medio) < qtd_medio:
            print(f"⚠️ Apenas {len(itens_medio)} questões médias disponíveis. Ajustando...")
            qtd_medio = len(itens_medio)
            qtd_facil += (quantidade - qtd_facil - qtd_medio)
        
        if len(itens_dificil) < qtd_dificil:
            print(f"⚠️ Apenas {len(itens_dificil)} questões difíceis disponíveis. Ajustando...")
            qtd_dificil = len(itens_dificil)
            qtd_facil += (quantidade - qtd_facil - qtd_medio - qtd_dificil) if qtd_facil + qtd_medio + qtd_dificil < quantidade else 0
        
        # Selecionar aleatoriamente
        selecionados = []
        if qtd_facil > 0:
            selecionados.extend(random.sample(itens_facil, qtd_facil))
        if qtd_medio > 0:
            selecionados.extend(random.sample(itens_medio, qtd_medio))
        if qtd_dificil > 0:
            selecionados.extend(random.sample(itens_dificil, qtd_dificil))
        
        # Embaralhar para não ficar agrupado por nível
        random.shuffle(selecionados)
        
        # Numerar as questões
        for i, item in enumerate(selecionados, 1):
            item.numero = i
        
        # Estatísticas da seleção
        stats = {
            "total": len(selecionados),
            "facil": len([i for i in selecionados if i.dificuldade < 0.4]),
            "medio": len([i for i in selecionados if 0.4 <= i.dificuldade < 0.7]),
            "dificil": len([i for i in selecionados if i.dificuldade >= 0.7])
        }
        
        return selecionados, stats
    
    def estatisticas(self) -> Dict:
        descritores = {}
        niveis = {}
        areas = {}
        
        for item in self.itens:
            descritores[item.descritor] = descritores.get(item.descritor, 0) + 1
            niveis[item.nivel] = niveis.get(item.nivel, 0) + 1
            areas[item.area] = areas.get(item.area, 0) + 1
        
        # Estatísticas de dificuldade
        dificuldade_stats = {
            "facil": len([i for i in self.itens if i.dificuldade < 0.4]),
            "medio": len([i for i in self.itens if 0.4 <= i.dificuldade < 0.7]),
            "dificil": len([i for i in self.itens if i.dificuldade >= 0.7])
        }
        
        return {
            "total_itens": len(self.itens),
            "total_descriptores": len(descritores),
            "itens_por_descriptor": descritores,
            "itens_por_nivel": niveis,
            "itens_por_area": areas,
            "itens_por_dificuldade": dificuldade_stats
        }


def testar_selecionador():
    print("=" * 60)
    print("🧪 TESTANDO SELECIONADOR DE ITENS (DISTRIBUIÇÃO SAEB)")
    print("=" * 60)
    
    selecionador = SelecionadorItens()
    
    print(f"\n📊 Estatísticas do banco:")
    stats = selecionador.estatisticas()
    print(f"   Total de itens: {stats['total_itens']}")
    print(f"   Por dificuldade: {stats['itens_por_dificuldade']}")
    
    print(f"\n🎲 Selecionando 10 questões com distribuição SAEB:")
    descritores = selecionador.get_descritores_disponiveis()
    if descritores:
        selecionados, distrib = selecionador.selecionar_questoes_saeb(descritores[:2], 10)
        print(f"   Questões selecionadas: {len(selecionados)}")
        print(f"   Distribuição real: fáceis={distrib['facil']}, médias={distrib['medio']}, difíceis={distrib['dificil']}")
        for item in selecionados[:3]:
            print(f"      - {item.id}: dificuldade={item.dificuldade}")
    
    print("\n✅ TESTE CONCLUÍDO!")


if __name__ == "__main__":
    testar_selecionador()
