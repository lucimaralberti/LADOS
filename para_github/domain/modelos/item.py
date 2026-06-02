"""
MODELO ITEM (QUESTÃO) - LADOS 2.0
Representa uma questão no sistema com todos os seus atributos
"""

import json
from datetime import datetime
from typing import List, Dict, Optional, Any
from dataclasses import dataclass, field, asdict

@dataclass
class Item:
    """
    Modelo de uma questão (item) do LADOS 2.0
    
    Atributos:
        id: Identificador único da questão
        texto: Enunciado da questão
        alternativas: Lista de alternativas (A, B, C, D)
        gabarito: Alternativa correta (A, B, C, D)
        descritor: Código do descritor (ex: MAT_5EF_D01)
        habilidade: Descrição da habilidade
        disciplina: Matemática, Português, etc.
        ano: Ano escolar (1 a 9)
        tipo_item: BNCC, CNCA, SAEB
        dificuldade: Nível de dificuldade (0 a 1)
        discriminacao: Poder de discriminação (TRI)
        bloom: Nível da Taxonomia de Bloom
        tipo_erro: Tipo de erro associado (opcional)
        ativo: Se a questão está ativa
        data_criacao: Data de criação
        ultima_atualizacao: Data da última atualizacao
        vezes_utilizada: Contador de uso
        taxa_acerto_historica: Percentual histórico de acertos
    """
    
    id: str
    texto: str
    alternativas: List[str]
    gabarito: str
    descritor: str
    habilidade: str
    disciplina: str
    ano: int
    tipo_item: str  # BNCC, CNCA, SAEB
    dificuldade: float = 0.5
    discriminacao: float = 1.0
    bloom: str = "Compreender"  # Lembrar, Compreender, Aplicar, Analisar, Avaliar, Criar
    tipo_erro: Optional[str] = None
    ativo: bool = True
    data_criacao: str = field(default_factory=lambda: datetime.now().isoformat())
    ultima_atualizacao: str = field(default_factory=lambda: datetime.now().isoformat())
    vezes_utilizada: int = 0
    taxa_acerto_historica: float = 0.0
    
    def to_dict(self) -> Dict[str, Any]:
        """Converte o Item para dicionário"""
        return asdict(self)
    
    def to_json(self) -> str:
        """Converte o Item para JSON"""
        return json.dumps(self.to_dict(), ensure_ascii=False, indent=2)
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Item":
        """Cria um Item a partir de um dicionário"""
        return cls(**data)
    
    @classmethod
    def from_json(cls, json_str: str) -> "Item":
        """Cria um Item a partir de uma string JSON"""
        data = json.loads(json_str)
        return cls.from_dict(data)
    
    def registrar_uso(self, acertou: bool):
        """Registra o uso da questão e atualiza estatísticas"""
        self.vezes_utilizada += 1
        # Atualizar taxa de acerto histórica (média móvel)
        novo_acerto = 1 if acertou else 0
        self.taxa_acerto_historica = (
            (self.taxa_acerto_historica * (self.vezes_utilizada - 1) + novo_acerto) 
            / self.vezes_utilizada
        )
        self.ultima_atualizacao = datetime.now().isoformat()
    
    def calibrar_dificuldade(self, novo_valor: float):
        """Calibra a dificuldade da questão (usado pelo calibrador)"""
        # Limitar entre 0.1 e 0.9 para evitar extremos
        self.dificuldade = max(0.1, min(0.9, novo_valor))
        self.ultima_atualizacao = datetime.now().isoformat()
    
    def get_nivel_dificuldade(self) -> str:
        """Retorna o nível textual da dificuldade"""
        if self.dificuldade < 0.3:
            return "Fácil"
        elif self.dificuldade < 0.7:
            return "Médio"
        else:
            return "Difícil"
    
    def get_nivel_bloom(self) -> str:
        """Retorna o nível da Taxonomia de Bloom"""
        niveis = {
            "Lembrar": 1,
            "Compreender": 2,
            "Aplicar": 3,
            "Analisar": 4,
            "Avaliar": 5,
            "Criar": 6
        }
        return self.bloom
    
    def validar(self) -> tuple[bool, str]:
        """Valida se o Item está consistente"""
        if not self.id:
            return False, "ID não pode ser vazio"
        if not self.texto:
            return False, "Texto da questão não pode ser vazio"
        if len(self.alternativas) != 4:
            return False, "Deve haver exatamente 4 alternativas"
        if self.gabarito not in ["A", "B", "C", "D"]:
            return False, "Gabarito deve ser A, B, C ou D"
        if self.ano < 1 or self.ano > 9:
            return False, "Ano deve ser entre 1 e 9"
        if self.dificuldade < 0 or self.dificuldade > 1:
            return False, "Dificuldade deve estar entre 0 e 1"
        return True, "OK"
    
    def __str__(self) -> str:
        return f"Item {self.id}: {self.texto[:50]}... ({self.disciplina} - {self.ano}º ano)"
    
    def __repr__(self) -> str:
        return f"Item(id='{self.id}', disciplina='{self.disciplina}', ano={self.ano}, dificuldade={self.dificuldade})"


class ItemBuilder:
    """Construtor para facilitar a criação de itens"""
    
    def __init__(self):
        self._item = None
        self.reset()
    
    def reset(self):
        """Reinicia o construtor"""
        self._item = Item(
            id="",
            texto="",
            alternativas=["", "", "", ""],
            gabarito="A",
            descritor="",
            habilidade="",
            disciplina="",
            ano=5,
            tipo_item="BNCC"
        )
        return self
    
    def set_id(self, id: str) -> "ItemBuilder":
        self._item.id = id
        return self
    
    def set_texto(self, texto: str) -> "ItemBuilder":
        self._item.texto = texto
        return self
    
    def set_alternativas(self, a: str, b: str, c: str, d: str) -> "ItemBuilder":
        self._item.alternativas = [a, b, c, d]
        return self
    
    def set_gabarito(self, gabarito: str) -> "ItemBuilder":
        self._item.gabarito = gabarito
        return self
    
    def set_descriptor(self, descritor: str, habilidade: str) -> "ItemBuilder":
        self._item.descriptor = descritor
        self._item.habilidade = habilidade
        return self
    
    def set_disciplina(self, disciplina: str) -> "ItemBuilder":
        self._item.disciplina = disciplina
        return self
    
    def set_ano(self, ano: int) -> "ItemBuilder":
        self._item.ano = ano
        return self
    
    def set_tipo_item(self, tipo_item: str) -> "ItemBuilder":
        self._item.tipo_item = tipo_item
        return self
    
    def set_dificuldade(self, dificuldade: float) -> "ItemBuilder":
        self._item.dificuldade = dificuldade
        return self
    
    def set_bloom(self, bloom: str) -> "ItemBuilder":
        self._item.bloom = bloom
        return self
    
    def set_tipo_erro(self, tipo_erro: str) -> "ItemBuilder":
        self._item.tipo_erro = tipo_erro
        return self
    
    def build(self) -> Item:
        """Retorna o Item construído"""
        return self._item

# Exemplo de uso
if __name__ == "__main__":
    # Criando um item de exemplo
    item = ItemBuilder()\
        .set_id("MAT_5EF_D01_001")\
        .set_texto("Qual é o resultado de 25 + 37?")\
        .set_alternativas("52", "62", "72", "82")\
        .set_gabarito("B")\
        .set_descriptor("MAT_5EF_D01", "Adição com reagrupamento")\
        .set_disciplina("Matemática")\
        .set_ano(5)\
        .set_tipo_item("BNCC")\
        .set_dificuldade(0.4)\
        .set_bloom("Aplicar")\
        .build()
    
    print("Item criado com sucesso!")
    print(f"ID: {item.id}")
    print(f"Texto: {item.texto}")
    print(f"Alternativas: {item.alternativas}")
    print(f"Gabarito: {item.gabarito}")
    print(f"Disciplina: {item.disciplina}")
    print(f"Dificuldade: {item.get_nivel_dificuldade()}")
    print(f"Bloom: {item.bloom}")
